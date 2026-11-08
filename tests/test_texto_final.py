import pytest

from src.consumir_gemini import extraer_texto


def test_extrae_todas_las_partes_finales_y_excluye_razonamiento():
    datos = {"candidates": [{"finishReason": "STOP", "content": {"parts": [
        {"text": "interno", "thought": True}, {"text": "Respuesta "}, {"text": "completa"},
    ]}}]}
    assert extraer_texto(datos) == "Respuesta completa"


@pytest.mark.parametrize("motivo", ["MAX_TOKENS", "SAFETY"])
def test_rechaza_resultado_incompleto_o_bloqueado(motivo):
    with pytest.raises(RuntimeError, match=motivo):
        extraer_texto({"candidates": [{"finishReason": motivo, "content": {"parts": [{"text": "parcial"}]}}]})


def test_rechaza_solo_razonamiento():
    with pytest.raises(RuntimeError, match="texto esperado"):
        extraer_texto({"candidates": [{"content": {"parts": [{"text": "interno", "thought": True}]}}]})
