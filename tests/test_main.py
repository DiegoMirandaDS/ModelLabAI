
"""Pruebas del punto de entrada de ModelLab AI."""

import unittest
from unittest.mock import patch

from src.main import main


class TestMain(unittest.TestCase):

    @patch("src.main.calcular_costo")
    @patch("src.main.extraer_texto")
    @patch("src.main.enviar_peticion")
    @patch("src.main.armar_peticion")
    def test_main_exitoso(
        self,
        mock_armar,
        mock_enviar,
        mock_extraer,
        mock_costo,
    ):
        """Comprueba que main coordina correctamente las funciones."""

        mock_armar.return_value = (
            "https://api.ejemplo.com",
            {"x-goog-api-key": "clave-ficticia"},
            {"contents": []},
        )

        mock_enviar.return_value = {
            "candidates": [
                {
                    "content": {
                        "parts": [
                            {"text": "El overfitting es el sobreajuste."}
                        ]
                    }
                }
            ],
            "usageMetadata": {
                "promptTokenCount": 10,
                "candidatesTokenCount": 20,
            },
        }

        mock_extraer.return_value = (
            "El overfitting es el sobreajuste."
        )

        mock_costo.return_value = 0.0001

        with patch("builtins.print") as mock_print:
            main()

        mock_armar.assert_called_once()
        mock_enviar.assert_called_once()
        mock_extraer.assert_called_once()
        mock_costo.assert_called_once()

        mock_print.assert_any_call(
            "El overfitting es el sobreajuste."
        )


if __name__ == "__main__":
    unittest.main()
