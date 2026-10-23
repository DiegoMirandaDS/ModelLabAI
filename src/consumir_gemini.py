
"""Módulo reutilizable para consumir la API de Gemini."""

import os
import json
import re

import requests
from dotenv import load_dotenv

load_dotenv()



def armar_peticion(pregunta, system_instruction=None, response_schema=None):
    """Construye una petición REST a Gemini, con salida estructurada opcional."""

    if not isinstance(pregunta, str) or not pregunta.strip():
        raise ValueError("La pregunta debe ser un texto no vacío.")

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("Falta GEMINI_API_KEY en el archivo .env.")

    modelo = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")

    url = (
        "https://generativelanguage.googleapis.com"
        f"/v1beta/models/{modelo}:generateContent"
    )

    headers = {
        "x-goog-api-key": api_key,
        "Content-Type": "application/json",
    }

    body = {
        "contents": [
            {
                "parts": [
                    {"text": pregunta}
                ]
            }
        ]
    }

    if system_instruction is not None:
        body["systemInstruction"] = {
            "parts": [
                {"text": system_instruction}
            ]
        }

    if response_schema is not None:
        body["generationConfig"] = {
            "responseMimeType": "application/json",
            "responseSchema": response_schema,
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


def calcular_costo(datos, precio_entrada, precio_salida):
    """Calcula el costo estimado de una petición en USD."""
    uso = datos["usageMetadata"]

    tokens_entrada = uso["promptTokenCount"]
    tokens_salida = uso.get("candidatesTokenCount", 0)
    tokens_razonamiento = uso.get("thoughtsTokenCount", 0)

    costo = (
        tokens_entrada * precio_entrada
        + (tokens_salida + tokens_razonamiento) * precio_salida
    )

    return costo


def obtener_dato_de_prueba(pregunta):
    """Coordina la petición y devuelve el texto generado."""
    url, headers, body = armar_peticion(pregunta)
    datos = enviar_peticion(url, headers, body)
    return extraer_texto(datos)


def parsear_respuesta_json(texto, esquema):
    """Convierte la respuesta en dict y valida claves y tipos esperados."""

    texto = texto.strip()

    texto = re.sub(r"^```(?:json)?\s*", "", texto)
    texto = re.sub(r"\s*```$", "", texto)

    try:
        datos = json.loads(texto)
    except json.JSONDecodeError as error:
        raise ValueError(
            "La respuesta del modelo no contiene JSON válido."
        ) from error

    if not isinstance(datos, dict):
        raise ValueError("La respuesta debe ser un objeto JSON.")

    propiedades = esquema.get("properties", {})
    requeridas = esquema.get("required", [])

    tipos = {
        "STRING": str,
        "NUMBER": (int, float),
        "INTEGER": int,
        "BOOLEAN": bool,
        "ARRAY": list,
        "OBJECT": dict,
    }

    for clave in requeridas:
        if clave not in datos:
            raise ValueError(f"Falta la clave requerida: {clave}")

    for clave, valor in datos.items():
        if clave not in propiedades:
            raise ValueError(f"Clave inesperada: {clave}")

        definicion = propiedades[clave]
        tipo = definicion["type"]

        if tipo == "NUMBER":
            valido = (
                isinstance(valor, (int, float))
                and not isinstance(valor, bool)
            )
        elif tipo == "INTEGER":
            valido = type(valor) is int
        else:
            valido = isinstance(valor, tipos[tipo])

        if not valido:
            raise ValueError(
                f"La clave '{clave}' no tiene el tipo {tipo}."
            )

        if tipo == "ARRAY" and "items" in definicion:
            tipo_items = definicion["items"]["type"]
            esperado = tipos[tipo_items]

            if not all(isinstance(item, esperado) for item in valor):
                raise ValueError(
                    f"Los elementos de '{clave}' no tienen el tipo esperado."
                )

    return datos

if __name__ == "__main__":
    try:
        resultado = obtener_dato_de_prueba(
            "Explica brevemente qué es el overfitting."
        )
        print("Respuesta de Gemini:\n")
        print(resultado)
    except (ValueError, RuntimeError) as error:
        print(f"No se pudo completar la operación: {error}")
