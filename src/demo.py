"""Ejecuta perfil, chain, enrutamiento o agente desde una misma entrada."""

import argparse
from datetime import datetime, timezone
import json
import os
import time

from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.messages import AIMessage
from langchain_core.output_parsers import StrOutputParser

from src.agente import construir_agente
from src.datos import RAIZ, guardar_json, perfil_publico
from src.orquestacion import construir_cadena, construir_enrutamiento, crear_modelo, procesar_seguro


class ConsumoLangChain(BaseCallbackHandler):
    """Registra tokens reportados; no atribuye la tarifa REST a estas llamadas."""
    def __init__(self):
        self.llamadas = []
        self.ultima_llamada = 0.0

    def on_chat_model_start(self, serialized, messages, **kwargs):
        # Cuatro inicios por minuto como máximo durante la demostración real.
        time.sleep(max(0, 15 - (time.monotonic() - self.ultima_llamada)))
        self.ultima_llamada = time.monotonic()

    def on_llm_end(self, response, **kwargs):
        mensaje = response.generations[0][0].message
        self.llamadas.append({
            "tokens": mensaje.usage_metadata or {},
            "modelo_reportado": mensaje.response_metadata.get("model_name"),
            "finish_reason": mensaje.response_metadata.get("finish_reason"),
        })


def resumir_cadena(resultado):
    return {k: resultado[k] for k in (
        "categoria", "diagnostico", "preparacion", "estrategia", "respuesta", "estado"
    ) if k in resultado}


def texto_salida_agente(contenido):
    """LangChain puede devolver texto simple o una lista de bloques de contenido."""
    return StrOutputParser().invoke(AIMessage(content=contenido))


def ejecutar(modo, mensaje, modelo, perfil):
    if modo == "cadena":
        return resumir_cadena(procesar_seguro(construir_cadena(modelo), {"mensaje": mensaje, "perfil": perfil}))
    if modo == "enrutamiento":
        resultado = procesar_seguro(construir_enrutamiento(modelo), {"mensaje": mensaje, "perfil": perfil})
        if "resultado" not in resultado:
            return resultado
        return {"categoria": resultado["categoria"], **resumir_cadena(resultado["resultado"])}
    resultado = construir_agente(modelo).invoke({"entrada": mensaje})
    texto = texto_salida_agente(resultado["output"])
    if not texto.strip() or texto.startswith("Agent stopped"):
        raise RuntimeError("El agente no produjo una respuesta final")
    return {
        "respuesta": texto,
        "pasos": [{"herramienta": accion.tool, "entrada": accion.tool_input, "observacion": observacion}
                  for accion, observacion in resultado["intermediate_steps"]],
    }


def generar_evidencias():
    """Corridas reales de la chain, las tres rutas y las decisiones del agente."""
    perfil = perfil_publico()
    consumo = ConsumoLangChain()
    modelo = crear_modelo([consumo])
    ruta = RAIZ / "docs/evidencias/orquestacion_agente.json"
    evidencia = json.loads(ruta.read_text(encoding="utf-8")) if ruta.exists() else []
    casos = [
        ("cadena", "cadena", "Propón preparación y validación para predecir abandono con este perfil.", None),
        ("ruta_preparacion", "enrutamiento", "Revisa los nulos y la calidad de los datos antes de preparar el ETL.", "preparacion"),
        ("ruta_modelado", "enrutamiento", "Propón partición y métricas para evaluar un clasificador de abandono.", "modelado"),
        ("ruta_consulta", "enrutamiento", "Hola, ¿en qué me puedes ayudar?", "consulta"),
        ("agente_perfil", "agente", "Consulta el perfil de iranian_churn: ¿cuántas filas y columnas hay y cuántos nulos tiene?", "consultar_perfil_dataset"),
        ("agente_balance", "agente", "Calcula el balance de Churn en iranian_churn: dame conteos y porcentajes de las dos clases.", "calcular_balance_objetivo"),
        ("agente_general", "agente", "Explica en una frase qué significa ETL, sin consultar ningún dataset.", "ninguna"),
    ]
    if any(e["sha256_csv"] != perfil["sha256_csv"] or e["modelo"] != os.environ["GEMINI_MODEL"] for e in evidencia):
        raise ValueError("Las evidencias existentes usan otro modelo o archivo")
    completos = {e["id"] for e in evidencia}
    for identificador, modo, mensaje, esperado in casos:
        if identificador in completos:
            continue
        inicio = len(consumo.llamadas)
        resultado = ejecutar(modo, mensaje, modelo, perfil)
        if any(c["finish_reason"] != "STOP" for c in consumo.llamadas[inicio:]):
            raise RuntimeError(f"La corrida {identificador} contiene una respuesta incompleta")
        if resultado.get("estado") in {"error", "fallback"}:
            raise RuntimeError(f"La corrida {identificador} no completó el camino normal")
        if modo == "enrutamiento" and resultado["categoria"] != esperado:
            raise AssertionError(f"Ruta inesperada: {resultado['categoria']}")
        if modo == "agente":
            elegidas = [paso["herramienta"] for paso in resultado["pasos"]]
            if (esperado == "ninguna" and elegidas) or (esperado != "ninguna" and elegidas != [esperado]):
                raise AssertionError(f"Herramientas inesperadas: {elegidas}")
        evidencia.append({
            "id": identificador, "modo": modo, "entrada": mensaje, "esperado": esperado,
            "verificacion": "correcta", "resultado": resultado,
            "modelo": os.environ["GEMINI_MODEL"], "sha256_csv": perfil["sha256_csv"],
            "fecha_utc": datetime.now(timezone.utc).isoformat(), "llamadas": consumo.llamadas[inicio:],
        })
        guardar_json(ruta, evidencia)
        print(f"{identificador}: verificado", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--modo", choices=["perfil", "cadena", "enrutamiento", "agente"], default="perfil")
    parser.add_argument("--mensaje", default="Recomienda preparación y validación para predecir abandono.")
    parser.add_argument("--consultar", action="store_true", help="Consulta Gemini y consume cuota")
    parser.add_argument("--evidencias", action="store_true", help="Ejecuta las siete verificaciones reales")
    args = parser.parse_args()
    if args.evidencias:
        if not args.consultar:
            parser.error("--evidencias requiere --consultar")
        generar_evidencias()
        return
    perfil = perfil_publico()
    if args.modo == "perfil":
        print(json.dumps(perfil, ensure_ascii=False, indent=2))
    elif args.consultar:
        resultado = ejecutar(args.modo, args.mensaje, crear_modelo(), perfil)
        print(json.dumps(resultado, ensure_ascii=False, indent=2))
    else:
        print("Agrega --consultar para realizar una llamada real a Gemini.")


if __name__ == "__main__":
    main()
