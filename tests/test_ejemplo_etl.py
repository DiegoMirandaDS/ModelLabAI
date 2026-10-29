"""Integración del ejemplo con el cliente real y transporte simulado."""

import json
from unittest.mock import Mock, patch

import pytest

from src import consumir_gemini as cliente
from src.ejemplos.recomendar_etl import recomendar, main
from src.prompts.etl_binario import PERFIL_SINTETICO


@pytest.fixture
def plan_simulado():
    return {
        "resumen": "Respuesta simulada para probar el contrato, no evaluación de Gemini",
        "tratamientos": ["Revisar gasto_mensual: 8% de nulos"],
        "riesgos": ["Excluir cliente_id como predictor provisionalmente"],
        "validacion": "Confirmar horizonte temporal antes de elegir partición",
        "modelos_candidatos": ["Regresión logística como candidato"],
        "metricas": ["Recall de la clase positiva"],
        "preguntas_pendientes": ["¿Cuándo se conoce el abandono?"],
    }


def test_ejemplo_envia_perfil_y_valida_respuesta(monkeypatch, plan_simulado):
    monkeypatch.setenv("GEMINI_API_KEY", "clave-ficticia")
    monkeypatch.setenv("GEMINI_MODEL", "modelo-de-prueba")
    monkeypatch.setattr(cliente, "costo_total_sesion", 0)
    respuesta = Mock(status_code=200)
    respuesta.json.return_value = {
        "candidates": [{"content": {"parts": [{"text": json.dumps(plan_simulado)}]}}],
        "usageMetadata": {"totalTokenCount": 1000},
    }
    with patch.object(cliente.requests, "post", return_value=respuesta) as post:
        assert recomendar(PERFIL_SINTETICO) == plan_simulado
    cuerpo = post.call_args.kwargs["json"]
    assert json.loads(cuerpo["contents"][0]["parts"][0]["text"]) == PERFIL_SINTETICO
    assert cuerpo["generationConfig"]["responseMimeType"] == "application/json"
    assert "clasificación binaria" in cuerpo["systemInstruction"]["parts"][0]["text"]
    assert cliente.costo_total_sesion == pytest.approx(cliente.COSTO_POR_1000_TOKENS)


def test_ejemplo_rechaza_respuesta_incompleta():
    with patch("src.ejemplos.recomendar_etl.consultar_modelo", return_value='{"resumen": "incompleto"}'):
        with pytest.raises(ValueError, match="Falta la clave"):
            recomendar(PERFIL_SINTETICO)


def test_vista_previa_no_consulta_api(monkeypatch, capsys):
    monkeypatch.setattr("sys.argv", ["recomendar_etl"])
    with patch.object(cliente.requests, "post", side_effect=AssertionError("Red inesperada")):
        main()
    assert json.loads(capsys.readouterr().out)["perfil"] == PERFIL_SINTETICO
