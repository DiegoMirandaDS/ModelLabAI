"""El ensayo guarda evidencia real en uso normal; aquí el transporte se simula."""

import json
from unittest.mock import Mock, patch

import pytest

from src import consumir_gemini as cliente
from src import ensayo_rate_limit as ensayo


@pytest.fixture(autouse=True)
def configurar(monkeypatch, tmp_path):
    monkeypatch.setenv("GEMINI_API_KEY", "secreto-que-no-debe-guardarse")
    monkeypatch.setenv("GEMINI_MODEL", "modelo-de-prueba")
    monkeypatch.setattr(ensayo, "RAIZ", tmp_path)
    monkeypatch.setattr(cliente, "costo_total_sesion", 0)


def respuesta(codigo):
    resultado = Mock(status_code=codigo)
    resultado.json.return_value = {
        "candidates": [{"content": {"parts": [{"text": "OK"}]}}],
        "usageMetadata": {"totalTokenCount": 100},
    }
    return resultado


def test_ensayo_registra_429_esperas_y_error_final_sin_costo():
    with patch.object(cliente.requests, "post", return_value=respuesta(429)) as post:
        with patch.object(cliente.time, "sleep") as dormir:
            ruta = ensayo.ejecutar(10)
    datos = json.loads(ruta.read_text())
    assert datos["estado"] == "finalizado"
    assert datos["resumen"]["respuestas_http"] == 3
    assert datos["resumen"]["primera_respuesta_429"] == 1
    assert datos["resumen"]["costo_estimado_usd"] == 0
    assert datos["operaciones"][0]["tipo_error"] == "RuntimeError"
    assert len(datos["resumen"]["esperas_programadas_segundos"]) == 2
    assert dormir.call_count == 2
    assert post.call_count == 3
    assert post.call_args.kwargs["json"]["generationConfig"]["maxOutputTokens"] == 128
    assert "secreto-que-no-debe-guardarse" not in ruta.read_text()


def test_ensayo_registra_recuperacion_y_detiene_nuevas_operaciones():
    with patch.object(cliente.requests, "post", side_effect=[respuesta(200), respuesta(429), respuesta(200)]):
        with patch.object(cliente.time, "sleep"):
            ruta = ensayo.ejecutar(10)
    datos = json.loads(ruta.read_text())
    assert datos["resumen"]["primera_respuesta_429"] == 2
    assert datos["resumen"]["operaciones_exitosas"] == 2
    assert len(datos["operaciones"]) == 2
    assert datos["resumen"]["costo_estimado_usd"] == pytest.approx(0.0004)
    assert len([e for e in datos["eventos"] if e["evento"] == "costo"]) == 2


def test_ensayo_sin_429_no_declara_que_lo_observo():
    with patch.object(cliente.requests, "post", return_value=respuesta(200)):
        ruta = ensayo.ejecutar(2)
    datos = json.loads(ruta.read_text())
    assert datos["resumen"]["primera_respuesta_429"] is None
    assert datos["motivo_fin"] == "Límite de operaciones alcanzado sin observar 429"
