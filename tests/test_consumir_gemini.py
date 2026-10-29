
import os
import unittest
from unittest.mock import patch, Mock

from src.consumir_gemini import (
    armar_peticion,
    enviar_peticion,
    extraer_texto,
    obtener_dato_de_prueba,
)


class TestConsumirGemini(unittest.TestCase):

    def test_pregunta_vacia(self):
        with self.assertRaisesRegex(ValueError, "no vacío"):
            armar_peticion("   ")

    def test_dato_faltante(self):
        with self.assertRaisesRegex(RuntimeError, "texto esperado"):
            extraer_texto({"candidates": []})

    @patch("src.consumir_gemini.requests.post")
    def test_error_conexion(self, mock_post):
        import requests

        mock_post.side_effect = requests.ConnectionError()

        with self.assertRaisesRegex(RuntimeError, "conectar"):
            enviar_peticion("https://ejemplo.com", {}, {})

    @patch("src.consumir_gemini.requests.post")
    def test_json_invalido(self, mock_post):
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.side_effect = ValueError(
            "JSON inválido"
        )

        with self.assertRaisesRegex(RuntimeError, "JSON válido"):
            enviar_peticion("https://ejemplo.com", {}, {})

    @patch.dict(os.environ, {"GEMINI_API_KEY": "clave-prueba"})
    @patch("src.consumir_gemini.requests.post")
    def test_respuesta_exitosa(self, mock_post):
        respuesta = Mock()
        respuesta.status_code = 200
        respuesta.json.return_value = {
            "candidates": [{
                "content": {
                    "parts": [{"text": "Explicación correcta"}]
                }
            }]
        }
        mock_post.return_value = respuesta

        resultado = obtener_dato_de_prueba("Overfitting")
        self.assertEqual(resultado, "Explicación correcta")


if __name__ == "__main__":
    unittest.main()
