"""Ensayo real del bloque 13, secuencial y acotado; requiere --ejecutar."""

import argparse
import json
import logging
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

from src import consumir_gemini as cliente

RAIZ = Path(__file__).resolve().parents[1]


class RegistroEnsayo(logging.Handler):
    """Captura solo eventos técnicos permitidos; nunca peticiones o claves."""

    def __init__(self, informe, guardar):
        super().__init__()
        self.informe = informe
        self.guardar = guardar
        self.operacion = None

    def emit(self, record):
        if not hasattr(record, "evento"):
            return
        self.informe["eventos"].append({
            "fecha_utc": datetime.now(timezone.utc).isoformat(),
            "operacion": self.operacion,
            "evento": record.evento,
            **record.datos,
        })
        print(record.getMessage(), flush=True)
        self.guardar()


def ejecutar(operaciones=10):
    if type(operaciones) is not int or not 1 <= operaciones <= 10:
        raise ValueError("El ensayo admite entre 1 y 10 operaciones.")
    inicio = datetime.now(timezone.utc)
    identificador = inicio.strftime("%Y%m%dT%H%M%S%fZ")
    salida = RAIZ / "docs" / "evidencias" / f"bloque-13-{identificador}.json"
    salida.parent.mkdir(parents=True, exist_ok=True)
    informe = {
        "id": identificador,
        "fecha_santiago": inicio.astimezone(ZoneInfo("America/Santiago")).isoformat(),
        "modelo": os.getenv("GEMINI_MODEL", "gemini-3.8-flash"),
        "tipo": "API real; sin mocks y sin concurrencia",
        "limites": {"operaciones": operaciones, "intentos_por_operacion": 3,
                    "max_output_tokens_por_peticion": 128},
        "tarifa": {"modo": "didactica", "usd_por_1000_tokens": cliente.COSTO_POR_1000_TOKENS,
                   "nota": "Estimación referencial; no tarifa vigente ni cargo comprobado"},
        "estado": "en_curso", "eventos": [], "operaciones": [],
    }

    def guardar():
        salida.write_text(json.dumps(informe, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    registro = RegistroEnsayo(informe, guardar)
    nivel_anterior = cliente.logger.level
    cliente.logger.setLevel(logging.INFO)
    cliente.logger.addHandler(registro)
    cliente.costo_total_sesion = 0.0
    guardar()
    try:
        for numero in range(1, operaciones + 1):
            registro.operacion = numero
            comienzo = time.monotonic()
            operacion = {"numero": numero}
            try:
                texto = cliente.consultar_modelo(
                    f"Ensayo académico {numero}. Responde únicamente OK.",
                    max_output_tokens=128,
                )
                operacion.update({"estado": "exito", "respuesta": texto})
            except (ValueError, RuntimeError, KeyError) as error:
                operacion.update({"estado": "fallo", "tipo_error": type(error).__name__,
                                  "error": str(error)})
            operacion["duracion_segundos"] = round(time.monotonic() - comienzo, 3)
            informe["operaciones"].append(operacion)
            guardar()
            print(f"Operación {numero}: {operacion['estado']}", flush=True)
            if any(e["evento"] == "http" and e["codigo"] == 429 for e in informe["eventos"]):
                informe["motivo_fin"] = "429 observado; se completó la operación con sus reintentos"
                break
            if operacion["estado"] == "fallo":
                informe["motivo_fin"] = "Fallo sin 429; detener para revisar antes de consumir más cuota"
                break
        else:
            informe["motivo_fin"] = "Límite de operaciones alcanzado sin observar 429"
        informe["estado"] = "finalizado"
    finally:
        cliente.logger.removeHandler(registro)
        cliente.logger.setLevel(nivel_anterior)
        http = [e for e in informe["eventos"] if e["evento"] == "http"]
        primer_429 = next((i for i, e in enumerate(http, 1) if e["codigo"] == 429), None)
        informe["resumen"] = {
            "respuestas_http": len(http), "primera_respuesta_429": primer_429,
            "respuestas_429": sum(e["codigo"] == 429 for e in http),
            "operaciones_exitosas": sum(o["estado"] == "exito" for o in informe["operaciones"]),
            "costo_estimado_usd": cliente.costo_total_sesion,
            "esperas_programadas_segundos": [e["espera_segundos"] for e in informe["eventos"]
                                              if e["evento"] == "reintento"],
            "nota_costo": "Solo consumo reportado; no permite inferir cargos por fallos ni consumo ausente",
        }
        informe["fin_utc"] = datetime.now(timezone.utc).isoformat()
        guardar()
    print(json.dumps(informe["resumen"], ensure_ascii=False, indent=2), flush=True)
    print(f"Evidencia: {salida.relative_to(RAIZ)}", flush=True)
    return salida


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ejecutar", action="store_true", help="Realizar llamadas reales a Gemini")
    parser.add_argument("--operaciones", type=int, default=10, choices=range(1, 11))
    args = parser.parse_args()
    if not args.ejecutar:
        parser.print_help()
        return
    ejecutar(args.operaciones)


if __name__ == "__main__":
    main()
