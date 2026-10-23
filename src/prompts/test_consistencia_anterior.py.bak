
"""Evalúa la consistencia estructural de los prompts."""

import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path

from src.prompts.banco import BANCO_DE_PROMPTS

from src.consumir_gemini import (
    armar_peticion,
    enviar_peticion,
    extraer_texto,
    parsear_respuesta_json,
)

REPETICIONES = 3
PAUSA_SEGUNDOS = 10

RUTA_RESULTADOS = (
    Path(__file__).resolve().parent
    / "registro_resultados.json"
)


def evaluar_prompt(prompt):
    exitos = 0
    resultados = []

    for intento in range(1, REPETICIONES + 1):
        print(f"  Intento {intento}/{REPETICIONES}")

        inicio = time.perf_counter()

        try:
            url, headers, body = armar_peticion(
                pregunta=prompt["ejemplo_usuario"],
                system_instruction=prompt["system_instruction"],
                response_schema=prompt["response_schema"],
            )

            respuesta = enviar_peticion(url, headers, body)
            texto = extraer_texto(respuesta)

            datos = parsear_respuesta_json(
                texto,
                prompt["response_schema"],
            )

            latencia = time.perf_counter() - inicio

            exitos += 1

            resultados.append({
                "intento": intento,
                "estado": "exito",
                "latencia_s": round(latencia, 3),
                "respuesta": datos,
            })

            print(f"    JSON válido | {latencia:.2f} s")

        except (ValueError, RuntimeError, KeyError, TypeError) as error:
            latencia = time.perf_counter() - inicio

            resultados.append({
                "intento": intento,
                "estado": "fallo",
                "latencia_s": round(latencia, 3),
                "error": str(error),
            })

            print(f"    Error: {error}")

        if intento < REPETICIONES:
            time.sleep(PAUSA_SEGUNDOS)

    return {
        "exitos": exitos,
        "fallos": REPETICIONES - exitos,
        "intentos": REPETICIONES,
        "consistencia_pct": round(
            exitos / REPETICIONES * 100, 2
        ),
        "resultados": resultados,
    }


def main():
    registro = {
        "fecha_utc": datetime.now(timezone.utc).isoformat(),
        "modelo": os.getenv("GEMINI_MODEL", "gemini-3.8-flash"),
        "repeticiones_por_prompt": REPETICIONES,
        "prompts": {},
    }

    for prompt in BANCO_DE_PROMPTS:
        nombre = prompt["nombre"]

        print(f"\nEvaluando: {nombre}")

        resultado = evaluar_prompt(prompt)

        registro["prompts"][nombre] = resultado

        print(
            f"Resultado: {resultado['exitos']}/"
            f"{resultado['intentos']} respuestas válidas"
        )

    RUTA_RESULTADOS.write_text(
        json.dumps(
            registro,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print(f"\nRegistro guardado en: {RUTA_RESULTADOS}")


if __name__ == "__main__":
    main()
