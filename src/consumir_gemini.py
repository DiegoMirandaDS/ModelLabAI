
"""Módulo reutilizable para consumir la API de Gemini."""

import os
import json
import re
import random
import time
import logging

import requests
from dotenv import load_dotenv

load_dotenv()

# Tarifa didáctica, no precio vigente de Gemini ni cargo comprobado.
COSTO_POR_1000_TOKENS = 0.002
costo_total_sesion = 0.0
logger = logging.getLogger(__name__)



def armar_peticion(pregunta, system_instruction=None, response_schema=None, max_output_tokens=None):
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

    if max_output_tokens is not None:
        if type(max_output_tokens) is not int or max_output_tokens < 1:
            raise ValueError("max_output_tokens debe ser un entero positivo.")
        body.setdefault("generationConfig", {})["maxOutputTokens"] = max_output_tokens

    return url, headers, body

def enviar_peticion(url, headers, body):
    """Envía la solicitud HTTP y convierte el JSON."""
    try:
        respuesta = requests.post(
            url, headers=headers, json=body, timeout=30
        )
    except requests.exceptions.Timeout as error:
        raise TimeoutError(
            "La conexión superó el tiempo de espera."
        ) from error
    except requests.exceptions.ConnectionError as error:
        raise RuntimeError(
            "No se pudo conectar con el servicio Gemini."
        ) from error

    logger.info(
        "Respuesta HTTP %s", respuesta.status_code,
        extra={"evento": "http", "datos": {"codigo": respuesta.status_code}},
    )
    if respuesta.status_code in (401, 403):
        raise ValueError(
            f"Gemini respondió con HTTP {respuesta.status_code}: revisa credenciales y permisos."
        )
    if respuesta.status_code == 429 or 500 <= respuesta.status_code < 600:
        raise TimeoutError(f"Gemini respondió con HTTP {respuesta.status_code}.")

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


def con_reintento(funcion, intentos=3, espera_base=2, espera_maxima=30):
    """Reintenta solo TimeoutError; intentos incluye la primera llamada."""
    if type(intentos) is not int or intentos < 1:
        raise ValueError("intentos debe ser un entero positivo.")
    if espera_base < 0 or espera_maxima < 0:
        raise ValueError("Las esperas no pueden ser negativas.")
    for intento in range(intentos):
        try:
            return funcion()
        except TimeoutError:
            if intento == intentos - 1:
                raise
            espera = min(espera_base * (2 ** intento), espera_maxima)
            espera = min(espera + random.uniform(0, espera * 0.1), espera_maxima)
            logger.info(
                "Intento %s de %s falló. Reintentando en %.3fs.", intento + 1, intentos, espera,
                extra={"evento": "reintento", "datos": {
                    "intento_fallido": intento + 1, "intentos_maximos": intentos,
                    "espera_segundos": espera,
                }},
            )
            time.sleep(espera)


def registrar_costo(respuesta, precio_entrada=None, precio_salida=None):
    """Acumula USD estimados; sin precios usa la tarifa didáctica por total."""
    global costo_total_sesion
    if (precio_entrada is None) != (precio_salida is None):
        raise ValueError("Debes proporcionar ambos precios por token.")
    if precio_entrada is None:
        # No inventar un costo cero cuando el proveedor no reportó consumo.
        costo = respuesta["usageMetadata"]["totalTokenCount"] / 1000 * COSTO_POR_1000_TOKENS
    else:
        if precio_entrada < 0 or precio_salida < 0:
            raise ValueError("Los precios no pueden ser negativos.")
        costo = calcular_costo(respuesta, precio_entrada, precio_salida)
    costo_total_sesion += costo
    logger.info(
        "Operación: costo estimado USD %.8f; acumulado USD %.8f.", costo, costo_total_sesion,
        extra={"evento": "costo", "datos": {
            "tokens": {k: respuesta["usageMetadata"][k] for k in (
                "promptTokenCount", "candidatesTokenCount", "thoughtsTokenCount", "totalTokenCount"
            ) if k in respuesta["usageMetadata"]},
            "costo_estimado_usd": costo, "acumulado_usd": costo_total_sesion,
            "modo_tarifa": "didactica" if precio_entrada is None else "desglosada",
        }},
    )
    return costo


def consultar_modelo(
    pregunta, system_instruction=None, response_schema=None,
    intentos=3, espera_base=2, espera_maxima=30,
    precio_entrada=None, precio_salida=None,
    max_output_tokens=None,
):
    """Consulta con reintentos; registra consumo reportado y devuelve texto."""
    if (precio_entrada is None) != (precio_salida is None):
        raise ValueError("Debes proporcionar ambos precios por token.")
    if precio_entrada is not None and (precio_entrada < 0 or precio_salida < 0):
        raise ValueError("Los precios no pueden ser negativos.")
    url, headers, body = armar_peticion(
        pregunta, system_instruction, response_schema, max_output_tokens=max_output_tokens,
    )
    try:
        datos = con_reintento(
            lambda: enviar_peticion(url, headers, body),
            intentos=intentos, espera_base=espera_base, espera_maxima=espera_maxima,
        )
    except TimeoutError as error:
        raise RuntimeError("No se pudo completar la consulta tras agotar los intentos.") from error
    uso = datos.get("usageMetadata", {})
    campo = "totalTokenCount" if precio_entrada is None else "promptTokenCount"
    if campo in uso:
        registrar_costo(datos, precio_entrada, precio_salida)
    return extraer_texto(datos)


def obtener_dato_de_prueba(pregunta):
    """Entrada histórica compatible; usa el coordinador del cliente."""
    return consultar_modelo(pregunta)


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
