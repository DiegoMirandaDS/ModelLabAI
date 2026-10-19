
import os
import requests
from dotenv import load_dotenv

load_dotenv()


def armar_peticion(pregunta):
    api_key = os.getenv("GEMINI_API_KEY")
    modelo = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    url = (
        "https://generativelanguage.googleapis.com"
        f"/v1beta/models/{modelo}:generateContent"
    )

    headers = {"x-goog-api-key": api_key}
    body = {"contents": [{"parts": [{"text": pregunta}]}]}

    return url, headers, body


def enviar_peticion(url, headers, body):
    respuesta = requests.post(
        url, headers=headers, json=body, timeout=30
    )
    return respuesta.json()


def extraer_texto(datos):
    return datos["candidates"][0]["content"]["parts"][0]["text"]


def obtener_dato_de_prueba(pregunta):
    url, headers, body = armar_peticion(pregunta)
    datos = enviar_peticion(url, headers, body)
    return extraer_texto(datos)


if __name__ == "__main__":
    print(obtener_dato_de_prueba(
        "Explica brevemente qué es el overfitting."
    ))
