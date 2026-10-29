"""Checklist del bloque 14: contratos reales del cliente con red y tiempo simulados."""

from unittest.mock import Mock, patch

import pytest
import requests

from src import consumir_gemini as cliente


@pytest.fixture(autouse=True)
def aislar_cliente(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "clave-ficticia")
    monkeypatch.setenv("GEMINI_MODEL", "modelo-de-prueba")
    monkeypatch.setattr(cliente, "costo_total_sesion", 0.0)
    # Un test que olvide simular red o tiempo debe fallar sin hacer llamadas reales.
    with patch.object(cliente.requests, "post", side_effect=AssertionError("Red no simulada")):
        with patch.object(cliente.time, "sleep", side_effect=AssertionError("Espera no simulada")):
            yield


def respuesta_http(codigo=200, datos=None):
    respuesta = Mock(status_code=codigo)
    respuesta.json.return_value = datos if datos is not None else {"texto": "respuesta simulada"}
    return respuesta


@pytest.mark.parametrize("codigo", [401, 403])
def test_enviar_peticion_credencial_invalida(codigo):
    with patch.object(cliente.requests, "post", return_value=respuesta_http(codigo)):
        with pytest.raises(ValueError, match=str(codigo)):
            cliente.enviar_peticion("https://ejemplo.invalid", {}, {})


@pytest.mark.parametrize("codigo", [429, 500, 503])
def test_enviar_peticion_error_temporal(codigo):
    with patch.object(cliente.requests, "post", return_value=respuesta_http(codigo)):
        with pytest.raises(TimeoutError, match=str(codigo)):
            cliente.enviar_peticion("https://ejemplo.invalid", {}, {})


def test_enviar_peticion_exito_devuelve_json_sin_alterar():
    datos = {"candidates": [], "usageMetadata": {"totalTokenCount": 12}}
    with patch.object(cliente.requests, "post", return_value=respuesta_http(datos=datos)) as post:
        assert cliente.enviar_peticion("https://ejemplo.invalid", {"h": "v"}, {"p": "v"}) is datos
    post.assert_called_once_with(
        "https://ejemplo.invalid", headers={"h": "v"}, json={"p": "v"}, timeout=30
    )


def test_enviar_peticion_timeout_transporte_es_recuperable():
    with patch.object(cliente.requests, "post", side_effect=requests.Timeout("simulado")):
        with pytest.raises(TimeoutError):
            cliente.enviar_peticion("https://ejemplo.invalid", {}, {})


def test_enviar_peticion_otro_http_conserva_diagnostico():
    respuesta = respuesta_http(400)
    respuesta.raise_for_status.side_effect = requests.HTTPError("simulado")
    with patch.object(cliente.requests, "post", return_value=respuesta):
        with pytest.raises(RuntimeError, match="HTTP 400"):
            cliente.enviar_peticion("https://ejemplo.invalid", {}, {})


def test_con_reintento_recupera_y_espera_entre_intentos():
    operacion = Mock(side_effect=[TimeoutError("simulado"), "ok"])
    with patch.object(cliente.time, "sleep") as dormir:
        assert cliente.con_reintento(operacion) == "ok"
    assert operacion.call_count == 2
    dormir.assert_called_once()


def test_con_reintento_agota_y_propaga_excepcion_original():
    error = TimeoutError("simulado")
    operacion = Mock(side_effect=error)
    with patch.object(cliente.time, "sleep") as dormir:
        with pytest.raises(TimeoutError) as capturado:
            cliente.con_reintento(operacion, intentos=3)
    assert capturado.value is error
    assert operacion.call_count == 3
    assert dormir.call_count == 2


@pytest.mark.parametrize("tipo", [ValueError, RuntimeError])
def test_con_reintento_no_reintenta_otros_errores(tipo):
    error = tipo("definitivo")
    operacion = Mock(side_effect=error)
    with patch.object(cliente.time, "sleep") as dormir:
        with pytest.raises(tipo) as capturado:
            cliente.con_reintento(operacion)
    assert capturado.value is error
    operacion.assert_called_once()
    dormir.assert_not_called()


def test_con_reintento_respeta_tope_con_jitter():
    operacion = Mock(side_effect=TimeoutError("simulado"))
    with patch.object(cliente.time, "sleep") as dormir:
        with pytest.raises(TimeoutError):
            cliente.con_reintento(operacion, intentos=4, espera_base=2, espera_maxima=3)
    esperas = [llamada.args[0] for llamada in dormir.call_args_list]
    assert len(esperas) == 3
    assert 2 <= esperas[0] <= 2.2
    assert all(0 <= espera <= 3 for espera in esperas)


@pytest.mark.parametrize("intentos", [0, -1, True, 1.5])
def test_con_reintento_rechaza_intentos_invalidos(intentos):
    operacion = Mock()
    with pytest.raises(ValueError):
        cliente.con_reintento(operacion, intentos=intentos)
    operacion.assert_not_called()


def test_registrar_costo_calcula_desde_total_tokens():
    costo = cliente.registrar_costo({"usageMetadata": {"totalTokenCount": 1000}})
    assert costo == pytest.approx(cliente.COSTO_POR_1000_TOKENS)
    assert cliente.costo_total_sesion == pytest.approx(costo)


def test_registrar_costo_acumula_dos_operaciones():
    cliente.registrar_costo({"usageMetadata": {"totalTokenCount": 1000}})
    cliente.registrar_costo({"usageMetadata": {"totalTokenCount": 500}})
    assert cliente.costo_total_sesion == pytest.approx(1.5 * cliente.COSTO_POR_1000_TOKENS)


def test_registrar_costo_desglosado_incluye_razonamiento():
    datos = {"usageMetadata": {
        "promptTokenCount": 100, "candidatesTokenCount": 20, "thoughtsTokenCount": 10,
    }}
    costo = cliente.registrar_costo(datos, precio_entrada=0.000001, precio_salida=0.000002)
    assert costo == pytest.approx(0.00016)
    assert cliente.costo_total_sesion == pytest.approx(costo)


def test_registrar_costo_no_inventa_consumo_faltante():
    with pytest.raises(KeyError):
        cliente.registrar_costo({})
    assert cliente.costo_total_sesion == 0


def test_consultar_modelo_convierte_timeout_agotado():
    with patch.object(cliente.requests, "post", return_value=respuesta_http(429)) as post:
        with patch.object(cliente.time, "sleep") as dormir:
            with pytest.raises(RuntimeError, match="agotar") as capturado:
                cliente.consultar_modelo("Recomienda un tratamiento", intentos=2)
    assert isinstance(capturado.value.__cause__, TimeoutError)
    assert post.call_count == 2
    dormir.assert_called_once()
    assert cliente.costo_total_sesion == 0


def test_consultar_modelo_propaga_value_error_sin_cambios():
    error = ValueError("credencial inválida")
    with patch.object(cliente, "enviar_peticion", side_effect=error) as enviar:
        with pytest.raises(ValueError) as capturado:
            cliente.consultar_modelo("Perfil sintético")
    assert capturado.value is error
    enviar.assert_called_once()


def test_consultar_modelo_recupera_y_registra_exito_una_sola_vez():
    datos = {
        "candidates": [{"content": {"parts": [{"text": "Plan simulado"}]}}],
        "usageMetadata": {"totalTokenCount": 1000},
    }
    with patch.object(cliente.requests, "post", side_effect=[respuesta_http(503), respuesta_http(datos=datos)]):
        with patch.object(cliente.time, "sleep"):
            assert cliente.consultar_modelo("Perfil sintético") == "Plan simulado"
    assert cliente.costo_total_sesion == pytest.approx(cliente.COSTO_POR_1000_TOKENS)


def test_consultar_modelo_acepta_texto_sin_metadatos_de_consumo():
    datos = {"candidates": [{"content": {"parts": [{"text": "Sin consumo reportado"}]}}]}
    with patch.object(cliente.requests, "post", return_value=respuesta_http(datos=datos)):
        assert cliente.consultar_modelo("Perfil sintético") == "Sin consumo reportado"
    assert cliente.costo_total_sesion == 0


def test_consultar_modelo_valida_precios_antes_de_enviar():
    with patch.object(cliente.requests, "post") as post:
        with pytest.raises(ValueError):
            cliente.consultar_modelo("Perfil sintético", precio_entrada=1)
    post.assert_not_called()
