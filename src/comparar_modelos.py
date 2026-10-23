"""Benchmark reproducible de modelos Gemini para ModelLab AI.
"""

import json
import os
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from unittest.mock import patch

from src.consumir_gemini import (
    armar_peticion,
    calcular_costo,
    enviar_peticion,
    extraer_texto,
)

RAIZ = Path(__file__).resolve().parents[1]
LOG = RAIZ / "logs" / "benchmark.jsonl"
INFORME = RAIZ / "docs" / "comparacion_modelos.md"

# Tarifas estandar de pago en USD por 1 millon de tokens (20-10-2026).
# Revisar https://ai.google.dev/gemini-api/docs/pricing.
MODELOS = {
    "gemini-3.8-flash": {"entrada": 0.75, "salida": 3.75},
    "gemini-3.6-flash": {"entrada": 0.75, "salida": 3.75},
}
PREGUNTAS = [
    "Explica brevemente qué es el overfitting en Machine Learning y cómo prevenirlo."
]
REPETICIONES = 4
PAUSA_SEGUNDOS = 3


def guardar_registro(registro):
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a", encoding="utf-8") as archivo:
        archivo.write(json.dumps(registro, ensure_ascii=False) + "\n")


def tabla_markdown(filas):
    encabezado = (
        "| Modelo | Exitosas / intentos | Latencia media (s) | "
        "Entrada media | Salida media* | Costo medio (USD) |\n"
        "|---|---:|---:|---:|---:|---:|"
    )
    renglones = [encabezado]
    for modelo in MODELOS:
        registros = [r for r in filas if r["modelo"] == modelo]
        exitosos = [r for r in registros if r["estado"] == "ok"]
        if exitosos:
            renglones.append(
                f"| `{modelo}` | {len(exitosos)} / {len(registros)} "
                f"| {mean(r['latencia_s'] for r in exitosos):.2f} "
                f"| {mean(r['tokens_entrada'] for r in exitosos):.1f} "
                f"| {mean(r['tokens_salida_facturable'] for r in exitosos):.1f} "
                f"| ${mean(r['costo_usd'] for r in exitosos):.8f} |"
            )
        else:
            renglones.append(f"| `{modelo}` | 0 / {len(registros)} | — | — | — | — |")
    return "\n".join(renglones)


def crear_informe(filas, ejecucion, fecha):
    INFORME.parent.mkdir(parents=True, exist_ok=True)
    partes = [
        "# Comparación de modelos — ModelLab AI",
        "",
        f"**Fecha (UTC):** {fecha}",
        f"**ID de ejecución:** `{ejecucion}`",
        f"**Preguntas:** {len(PREGUNTAS)}; **repeticiones por pregunta:** {REPETICIONES}.",
        "",
        "## Tarifas utilizadas",
        "",
        "| Modelo | Entrada USD/1M | Salida USD/1M |",
        "|---|---:|---:|",
    ]
    for modelo, precio in MODELOS.items():
        partes.append(f"| `{modelo}` | ${precio['entrada']:.2f} | ${precio['salida']:.2f} |")
    partes += [
        "",
        "Los costos son **estimaciones con tarifas estándar de pago**, no cargos comprobados; "
        "la cuota gratuita puede no generar cobro. Los precios pueden cambiar.",
        "",
        "## Resultados medidos",
        "",
        tabla_markdown(filas),
        "",
        "*Salida media facturable = tokens visibles generados + tokens de razonamiento, "
        "cuando ambos campos están disponibles. No incluye otras posibles modalidades de cobro.*",
        "",
        "Las latencias miden la solicitud HTTP completa, sin las pausas del benchmark. "
        "Solo las peticiones exitosas entran en los promedios.",
        "",
        "## Respuestas y evidencia",
        "",
    ]
    for r in filas:
        partes.append(
            f"### {r['modelo']} — pregunta {r['pregunta_id']} / intento {r['intento']}"
        )
        partes.append("")
        partes.append(f"**Estado:** {r['estado']} | **Latencia:** {r['latencia_s']:.2f} s")
        partes.append("")
        partes.append("**Pregunta:** " + r["pregunta"])
        partes.append("")
        if r["estado"] == "ok":
            partes.append("**Respuesta:**")
            partes.append("")
            partes.append(r["respuesta"])
        else:
            partes.append("**Error:** " + r["error"].replace("\n", " "))
        partes.append("")
    partes += [
        "## Fuentes",
        "",
        "- https://ai.google.dev/gemini-api/docs/pricing",
        "",
    ]
    INFORME.write_text("\n".join(partes), encoding="utf-8")


def ejecutar():
    ejecucion = uuid.uuid4().hex[:12]
    fecha = datetime.now(timezone.utc).isoformat(timespec="seconds")
    registros = []
    for modelo, precios in MODELOS.items():
        print(f"\nMODELO: {modelo}")
        for pregunta_id, pregunta in enumerate(PREGUNTAS, start=1):
            for intento in range(1, REPETICIONES + 1):
                registro = {
                    "ejecucion": ejecucion,
                    "fecha_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                    "modelo": modelo,
                    "pregunta_id": pregunta_id,
                    "pregunta": pregunta,
                    "intento": intento,
                    "precio_entrada_por_millon": precios["entrada"],
                    "precio_salida_por_millon": precios["salida"],
                }
                inicio = None
                try:
                    with patch.dict(os.environ, {"GEMINI_MODEL": modelo}):
                        url, headers, body = armar_peticion(pregunta)
                    inicio = time.perf_counter()
                    datos = enviar_peticion(url, headers, body)
                    latencia = time.perf_counter() - inicio
                    respuesta = extraer_texto(datos)
                    uso = datos["usageMetadata"]
                    entrada = uso["promptTokenCount"]
                    visible = uso.get("candidatesTokenCount", 0)
                    razonamiento = uso.get("thoughtsTokenCount", 0)
                    costo = calcular_costo(
                        datos,
                        precios["entrada"] / 1_000_000,
                        precios["salida"] / 1_000_000,
                    )
                    registro.update({
                        "estado": "ok",
                        "latencia_s": round(latencia, 4),
                        "tokens_entrada": entrada,
                        "tokens_salida_visible": visible,
                        "tokens_razonamiento": razonamiento,
                        "tokens_salida_facturable": visible + razonamiento,
                        "tokens_totales_reportados": uso.get("totalTokenCount"),
                        "costo_usd": costo,
                        "respuesta": respuesta,
                    })
                    print(f"  Intento {intento}: {latencia:.2f} s | ${costo:.8f}")
                except (ValueError, RuntimeError, KeyError, IndexError, TypeError) as error:
                    transcurrido = (time.perf_counter() - inicio) if inicio is not None else 0.0
                    registro.update({
                        "estado": "error", "latencia_s": round(transcurrido, 4),
                        "error": str(error),
                    })
                    print(f"  Intento {intento}: ERROR — {error}")
                registros.append(registro)
                guardar_registro(registro)
                crear_informe(registros, ejecucion, fecha)
                time.sleep(PAUSA_SEGUNDOS)

    print("\nInforme actualizado:", INFORME.relative_to(RAIZ))
    print("Historial acumulado:", LOG.relative_to(RAIZ))
    print("\n" + tabla_markdown(registros))


if __name__ == "__main__":
    ejecutar()
