"""Normalización y métricas léxicas de los bloques 15–16."""

from collections import Counter
import re


def limpiar_texto(texto: str) -> str:
    if not isinstance(texto, str):
        raise TypeError("Se esperaba un texto")
    return re.sub(r"\s+", " ", re.sub(r"[^\w\s]", "", texto.lower())).strip()


def tokenizar(texto_limpio: str) -> list[str]:
    return texto_limpio.split()


def procesar_texto(texto: str) -> list[str]:
    return tokenizar(limpiar_texto(texto))


def contar_coincidencias(referencia: list[str], respuesta: list[str]) -> int:
    if not isinstance(referencia, list) or not isinstance(respuesta, list):
        raise TypeError("Las métricas requieren listas de tokens")
    return sum((Counter(referencia) & Counter(respuesta)).values())


def calcular_precision_cobertura_f1(referencia: list[str], respuesta: list[str]) -> dict[str, float]:
    coincidencias = contar_coincidencias(referencia, respuesta)
    if not referencia or not respuesta:
        return {"precision": 0.0, "cobertura": 0.0, "f1": 0.0}
    precision = coincidencias / len(respuesta)
    cobertura = coincidencias / len(referencia)
    f1 = 2 * precision * cobertura / (precision + cobertura) if coincidencias else 0.0
    return {"precision": precision, "cobertura": cobertura, "f1": f1}


def calcular_metricas(referencia: str, respuesta: str) -> dict[str, float]:
    return calcular_precision_cobertura_f1(procesar_texto(referencia), procesar_texto(respuesta))


def coincidencia_palabras(referencia: str, respuesta: str, procesado: bool = True) -> float:
    """Proporción simple del bloque 15; el bloque 16 usa Counter."""
    funcion = procesar_texto if procesado else str.split
    esperadas = set(funcion(referencia))
    return len(esperadas & set(funcion(respuesta))) / len(esperadas) if esperadas else 0.0
