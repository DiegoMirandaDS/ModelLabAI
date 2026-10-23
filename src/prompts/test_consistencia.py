
"""Validación acumulativa e idempotente de prompts de ModelLab AI."""

import hashlib
import json
import os
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

from src.prompts.banco import BANCO_DE_PROMPTS
from src.consumir_gemini import (
    armar_peticion,
    enviar_peticion,
    extraer_texto,
    parsear_respuesta_json,
)

load_dotenv()

DIRECTORIO = Path(__file__).resolve().parent
LOG = DIRECTORIO / "registro_intentos.jsonl"
RESUMEN = DIRECTORIO / "registro_resultados.json"

OBJETIVO_EXITOS = 3
MAX_INTENTOS_POR_EJECUCION = 3
PAUSA_SEGUNDOS = 10


def fecha_actual():
    return datetime.now(timezone.utc).isoformat()


def version_prompt(prompt):
    """Identifica una versión concreta del prompt y su esquema."""
    contenido = {
        "system_instruction": prompt["system_instruction"],
        "ejemplo_usuario": prompt["ejemplo_usuario"],
        "response_schema": prompt["response_schema"],
    }
    texto = json.dumps(contenido, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()[:16]


def leer_historial():
    """Carga los registros históricos sin modificar el archivo."""
    if not LOG.exists():
        return []

    registros = []

    with LOG.open("r", encoding="utf-8") as archivo:
        for numero, linea in enumerate(archivo, start=1):
            if not linea.strip():
                continue

            try:
                registros.append(json.loads(linea))
            except json.JSONDecodeError as error:
                raise RuntimeError(
                    f"Registro JSONL inválido en línea {numero}"
                ) from error

    return registros


def guardar_intento(registro):
    """Añade un intento al historial y lo sincroniza con disco."""
    LOG.parent.mkdir(parents=True, exist_ok=True)

    with LOG.open("a", encoding="utf-8") as archivo:
        archivo.write(
            json.dumps(registro, ensure_ascii=False) + "\n"
        )
        archivo.flush()
        os.fsync(archivo.fileno())


def registros_de_prueba(historial, modelo, nombre, version):
    """Obtiene intentos de la misma prueba lógica."""
    return [
        registro for registro in historial
        if registro.get("modelo") == modelo
        and registro.get("prompt") == nombre
        and registro.get("version_prompt") == version
    ]


def contar_exitos(registros):
    """Evita contabilizar dos veces un mismo intento."""
    identificadores = set()
    exitos = 0

    for registro in registros:
        identificador = registro["id_intento"]

        if identificador in identificadores:
            continue

        identificadores.add(identificador)

        if registro["estado"] == "exito":
            exitos += 1

    return exitos


def generar_resumen(historial, modelo):
    """Regenera una vista resumida de las pruebas actuales."""
    resumen = {
        "actualizado_utc": fecha_actual(),
        "modelo": modelo,
        "objetivo_exitos": OBJETIVO_EXITOS,
        "prompts": {},
    }

    for prompt in BANCO_DE_PROMPTS:
        nombre = prompt["nombre"]
        version = version_prompt(prompt)

        registros = registros_de_prueba(
            historial, modelo, nombre, version
        )

        exitos = contar_exitos(registros)
        fallos = sum(
            r["estado"] == "fallo" for r in registros
        )

        resumen["prompts"][nombre] = {
            "version_prompt": version,
            "exitos": exitos,
            "fallos": fallos,
            "intentos": len(registros),
            "objetivo_cumplido": exitos >= OBJETIVO_EXITOS,
            "exitos_pendientes": max(
                0, OBJETIVO_EXITOS - exitos
            ),
        }

    temporal = RESUMEN.with_suffix(".json.tmp")
    temporal.write_text(
        json.dumps(resumen, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    temporal.replace(RESUMEN)

    return resumen


def evaluar_prompt(prompt, modelo, historial):
    nombre = prompt["nombre"]
    version = version_prompt(prompt)

    registros = registros_de_prueba(
        historial, modelo, nombre, version
    )

    exitos = contar_exitos(registros)
    pendientes = max(0, OBJETIVO_EXITOS - exitos)

    print(f"\nPROMPT: {nombre}")
    print(f"Versión: {version}")
    print(f"Éxitos acumulados: {exitos}")
    print(f"Pendientes: {pendientes}")

    if pendientes == 0:
        print("Completado: no se realizarán nuevas peticiones.")
        return

    for numero in range(1, MAX_INTENTOS_POR_EJECUCION + 1):
        if exitos >= OBJETIVO_EXITOS:
            break

        registro = {
            "id_intento": str(uuid.uuid4()),
            "fecha_utc": fecha_actual(),
            "modelo": modelo,
            "prompt": nombre,
            "version_prompt": version,
            "estado": None,
        }

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

            registro["estado"] = "exito"
            registro["respuesta"] = datos
            registro["uso_tokens"] = respuesta.get(
                "usageMetadata", {}
            )

            exitos += 1
            print(f"  Intento {numero}: JSON válido")

        except (ValueError, RuntimeError, KeyError, TypeError) as error:
            registro["estado"] = "fallo"
            registro["error"] = str(error)
            print(f"  Intento {numero}: {error}")

        registro["latencia_s"] = round(
            time.perf_counter() - inicio, 3
        )

        # Guardar inmediatamente después de cada intento.
        guardar_intento(registro)
        historial.append(registro)

        # Actualizar resumen sin esperar al final.
        generar_resumen(historial, modelo)

        if exitos < OBJETIVO_EXITOS:
            time.sleep(PAUSA_SEGUNDOS)


def main():
    modelo = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")
    historial = leer_historial()

    print("=== ModelLab AI: consistencia acumulativa ===")
    print(f"Modelo: {modelo}")
    print(f"Registros históricos: {len(historial)}")

    generar_resumen(historial, modelo)

    for prompt in BANCO_DE_PROMPTS:
        evaluar_prompt(prompt, modelo, historial)

    resumen = generar_resumen(historial, modelo)

    print("\n=== RESUMEN FINAL ===")

    for nombre, datos in resumen["prompts"].items():
        print(
            f"{nombre}: {datos['exitos']} éxitos, "
            f"{datos['fallos']} fallos, "
            f"{datos['exitos_pendientes']} pendientes"
        )

    print(f"\nHistorial: {LOG}")
    print(f"Resumen: {RESUMEN}")


if __name__ == "__main__":
    main()
