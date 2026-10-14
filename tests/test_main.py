
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(
    0,
    str(Path(__file__).resolve().parents[1] / "src"),
)

from main import generar_explicacion


class TestGeminiAPI(unittest.TestCase):

    @patch("main.load_dotenv")
    @patch.dict(os.environ, {}, clear=True)
    def test_api_key_obligatoria(self, mock_dotenv):
        with self.assertRaises(ValueError):
            generar_explicacion("Machine learning")

    @patch("main.load_dotenv")
    @patch.dict(
        os.environ,
        {
            "GEMINI_API_KEY": "clave-ficticia",
            "GEMINI_MODEL": "gemini-2.5-flash",
        },
        clear=True,
    )
    @patch("main.requests.post")
    def test_respuesta_exitosa(self, mock_post, mock_dotenv):
        respuesta = MagicMock()
        respuesta.status_code = 200
        respuesta.json.return_value = {
            "candidates": [
                {
                    "content": {
                        "parts": [
                            {"text": "Explicación de prueba"}
                        ]
                    }
                }
            ]
        }
        mock_post.return_value = respuesta

        resultado = generar_explicacion("Overfitting")

        self.assertEqual(resultado, "Explicación de prueba")
        mock_post.assert_called_once()

        argumentos = mock_post.call_args
        self.assertEqual(
            argumentos.kwargs["headers"]["x-goog-api-key"],
            "clave-ficticia",
        )


if __name__ == "__main__":
    unittest.main()
