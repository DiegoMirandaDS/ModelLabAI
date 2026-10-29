"""Punto de entrada histórico de ModelLab AI; consulta real a Gemini."""

import sys

from src import consumir_gemini as cliente

# Valores históricos del proyecto, no tarifas vigentes verificadas.
PRECIO_ENTRADA = 0.75 / 1_000_000
PRECIO_SALIDA = 3.75 / 1_000_000

SYSTEM_INSTRUCTION = (
    "Eres ModelLab AI, un asistente especializado en datos tabulares "
    "y Machine Learning. Explica con precisión y no inventes resultados."
)


def main():
    pregunta = "Explica brevemente qué es el overfitting y menciona dos formas de prevenirlo."
    texto = cliente.consultar_modelo(
        pregunta,
        system_instruction=SYSTEM_INSTRUCTION,
        precio_entrada=PRECIO_ENTRADA,
        precio_salida=PRECIO_SALIDA,
    )
    print("\n=== ModelLab AI ===")
    print("\nRespuesta del modelo:\n")
    print(texto)
    print(
        "\nCosto acumulado registrado (solo consumo reportado; tarifas históricas): "
        f"USD {cliente.costo_total_sesion:.8f}"
    )
    print("\nProceso terminado correctamente.")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, RuntimeError, KeyError) as error:
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)
