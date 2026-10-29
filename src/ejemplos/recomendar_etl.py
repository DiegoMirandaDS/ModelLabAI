"""Vista previa local del caso ETL; --consultar realiza una llamada real."""

import argparse
import json

from src.consumir_gemini import consultar_modelo, parsear_respuesta_json
from src.prompts.etl_binario import ESQUEMA_ETL, PERFIL_SINTETICO, SYSTEM_INSTRUCTION


def recomendar(perfil):
    texto = consultar_modelo(
        json.dumps(perfil, ensure_ascii=False),
        system_instruction=SYSTEM_INSTRUCTION,
        response_schema=ESQUEMA_ETL,
    )
    return parsear_respuesta_json(texto, ESQUEMA_ETL)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--consultar", action="store_true", help="Enviar perfil sintético a Gemini")
    args = parser.parse_args()
    if args.consultar:
        resultado = recomendar(PERFIL_SINTETICO)
    else:
        resultado = {
            "modo": "Vista previa local; no se consultó Gemini",
            "perfil": PERFIL_SINTETICO,
            "instrucciones": SYSTEM_INSTRUCTION,
            "esquema_respuesta": ESQUEMA_ETL,
        }
    print(json.dumps(resultado, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
