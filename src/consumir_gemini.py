
"""Módulo reutilizable para consumir la API de Gemini."""

import os

import requests
from dotenv import load_dotenv

load_dotenv()


def armar_peticion(pregunta):
    """Valida la entrada y prepara la solicitud HTTP."""
    if not isinstance(pregunta, str) or not pregunta.strip():
        raise ValueError("La pregunta debe ser un texto no vacío.")

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("Falta GEMINI_API_KEY en el archivo .env.")

    modelo = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    url = (
        "https://generativelanguage.googleapis.com"
        f"/v1beta/models/{modelo}:generateContent"
    )

    headers = {"x-goog-api-key": api_key}
    body = {
        "contents": [{"parts": [{"text": pregunta}]}]
    }

    return url, headers, body


def enviar_peticion(url, headers, body):
    """Envía la solicitud HTTP y convierte el JSON."""
    try:
        respuesta = requests.post(
            url, headers=headers, json=body, timeout=30
        )
    except requests.exceptions.Timeout as error:
        raise RuntimeError(
            "La conexión superó el tiempo de espera."
        ) from error
    except requests.exceptions.ConnectionError as error:
        raise RuntimeError(
            "No se pudo conectar con el servicio Gemini."
        ) from error

    try:
        respuesta.raise_for_status()
    except requests.exceptions.HTTPError as error:
        raise RuntimeError(
            f"Gemini respondió con HTTP {respuesta.status_code}."
        ) from error

    try:
        return respuesta.json()
    except (requests.exceptions.JSONDecodeError, ValueError) as error:
        raise RuntimeError(
            "La respuesta del servicio no contiene JSON válido."
        ) from error


def extraer_texto(datos):
    """Extrae el texto generado desde la respuesta JSON."""
    try:
        texto = datos["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError, TypeError) as error:
        raise RuntimeError(
            "La respuesta de Gemini no contiene el texto esperado."
        ) from error

    if not isinstance(texto, str):
        raise RuntimeError(
            "El texto generado tiene un formato inesperado."
        )

    return texto


def obtener_dato_de_prueba(pregunta):
    """Coordina la petición y devuelve el texto generado."""
    url, headers, body = armar_peticion(pregunta)
    datos = enviar_peticion(url, headers, body)
    return extraer_texto(datos)


if __name__ == "__main__":
    try:
        resultado = obtener_dato_de_prueba(
            "Explica brevemente qué es el overfitting."
        )
        print("Respuesta de Gemini:\n")
        print(resultado)
    except (ValueError, RuntimeError) as error:
        print(f"No se pudo completar la operación: {error}")
