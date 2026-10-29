"""Pruebas de la entrada de consola sin consultar la API."""

import unittest
from unittest.mock import patch

from src.main import main, SYSTEM_INSTRUCTION, PRECIO_ENTRADA, PRECIO_SALIDA


class TestMain(unittest.TestCase):
    @patch("src.main.cliente.consultar_modelo", return_value="Explicación simulada")
    def test_main_exitoso(self, consultar):
        with patch("builtins.print") as imprimir:
            main()
        consultar.assert_called_once_with(
            "Explica brevemente qué es el overfitting y menciona dos formas de prevenirlo.",
            system_instruction=SYSTEM_INSTRUCTION,
            precio_entrada=PRECIO_ENTRADA,
            precio_salida=PRECIO_SALIDA,
        )
        imprimir.assert_any_call("Explicación simulada")


if __name__ == "__main__":
    unittest.main()
