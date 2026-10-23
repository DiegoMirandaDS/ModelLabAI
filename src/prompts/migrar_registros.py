
"""Migración única de registros anteriores al historial JSONL."""

import hashlib
import json
from pathlib import Path

from src.prompts.banco import BANCO_DE_PROMPTS
from src.prompts.test_consistencia import (
    DIRECTORIO,
    LOG,
    version_prompt,
)

ARCHIVOS = [
    DIRECTORIO / "registro_resultados_2026-10-23.json",
    DIRECTORIO / "registro_resultados.json",
]

VERSIONES = {
    prompt["nombre"]: version_prompt(prompt)
    for prompt in BANCO_DE_PROMPTS
}


def main():
    if LOG.exists() and LOG.stat().st_size > 0:
        raise RuntimeError(
            "Ya existe un historial JSONL. "
            "No se realizará una segunda migración."
        )

    eventos = []

    for ruta in ARCHIVOS:
        if not ruta.exists():
            continue

        documento = json.loads(ruta.read_text(encoding="utf-8"))
        modelo = documento["modelo"]

        for nombre, info in documento["prompts"].items():
            if nombre not in VERSIONES:
                continue

            for resultado in info["resultados"]:
                identidad = (
                    f"{ruta.name}:{modelo}:{nombre}:"
                    f"{resultado['intento']}"
                )

                identificador = hashlib.sha256(
                    identidad.encode("utf-8")
                ).hexdigest()[:24]

                evento = {
                    "id_intento": identificador,
                    "fecha_utc": documento["fecha_utc"],
                    "modelo": modelo,
                    "prompt": nombre,
                    "version_prompt": VERSIONES[nombre],
                    "estado": resultado["estado"],
                    "latencia_s": resultado.get("latencia_s"),
                    "origen": ruta.name,
                }

                if "respuesta" in resultado:
                    evento["respuesta"] = resultado["respuesta"]

                if "error" in resultado:
                    evento["error"] = resultado["error"]

                eventos.append(evento)

    if not eventos:
        raise RuntimeError("No se encontraron resultados para migrar.")

    with LOG.open("x", encoding="utf-8") as archivo:
        for evento in eventos:
            archivo.write(
                json.dumps(evento, ensure_ascii=False) + "\n"
            )

    print(f"Migrados {len(eventos)} intentos a {LOG}")


if __name__ == "__main__":
    main()
