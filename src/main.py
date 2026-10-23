
"""Punto de entrada de ModelLab AI."""

import sys

from src.consumir_gemini import (
    armar_peticion,
    enviar_peticion,
    extraer_texto,
    calcular_costo,
)


PRECIO_ENTRADA = 0.75 / 1_000_000
PRECIO_SALIDA = 3.75 / 1_000_000

SYSTEM_INSTRUCTION = (
    "Eres ModelLab AI, un asistente educativo "
    "especializado en Machine Learning. "
    "Explica conceptos técnicos con precisión, "
    "claridad y ejemplos cuando sean útiles. "
    "No inventes resultados experimentales."
)


def main():
    pregunta = (
        "Explica brevemente qué es el overfitting "
        "y menciona dos formas de prevenirlo."
    )

    url, headers, body = armar_peticion(
        pregunta,
        system_instruction=SYSTEM_INSTRUCTION,
    )

    respuesta = enviar_peticion(url, headers, body)

    texto = extraer_texto(respuesta)

    costo = calcular_costo(
        respuesta,
        PRECIO_ENTRADA,
        PRECIO_SALIDA,
    )

    print("\n=== ModelLab AI ===")
    print("\nRespuesta del modelo:\n")
    print(texto)

    print(f"\nCosto estimado: USD {costo:.8f}")
    print("\nProceso terminado correctamente.")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, RuntimeError, KeyError) as error:
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)
