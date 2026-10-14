
"""Cliente HTTP para la API de Gemini."""

import os

import requests
from dotenv import load_dotenv

API_URL = (
    "https://generativelanguage.googleapis.com"
    "/v1beta/models/{model}:generateContent"
)


def generar_explicacion(tema: str) -> str:
    """Solicita una explicación educativa a Gemini."""
    load_dotenv()

    api_key = os.getenv("GEMINI_API_KEY")
    model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    if not api_key:
        raise ValueError("Falta GEMINI_API_KEY en .env")

    url = API_URL.format(model=model)

    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": api_key,
    }

    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": (
                            "Explica de manera breve y sencilla "
                            f"el siguiente concepto: {tema}"
                        )
                    }
                ]
            }
        ]
    }

    respuesta = requests.post(
        url,
        headers=headers,
        json=payload,
        timeout=60,
    )

    print(f"HTTP Status: {respuesta.status_code}")
    print(f"Respuesta de Google: {respuesta.text}")

    respuesta.raise_for_status()

    datos = respuesta.json()

    return datos["candidates"][0]["content"]["parts"][0]["text"]


if __name__ == "__main__":
    try:
        resultado = generar_explicacion("Overfitting")
        print("\nRespuesta de Gemini:\n")
        print(resultado)
    except (requests.RequestException, KeyError, IndexError) as error:
        print(f"Error en la solicitud: {error}")
        raise SystemExit(1)
    except ValueError as error:
        print(f"Error de configuración: {error}")
        raise SystemExit(1)
