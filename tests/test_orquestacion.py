from unittest.mock import Mock

from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableLambda
import pytest

from src.orquestacion import (
    construir_cadena, construir_enrutamiento, procesar_seguro, validar_salida,
)


def test_tres_pasos_consumen_salida_anterior_y_preservan_perfil():
    modelo = Mock(side_effect=[AIMessage(content="diagnóstico medido"),
                               AIMessage(content="preparación derivada"), AIMessage(content="estrategia final")])
    resultado = construir_cadena(modelo).invoke({"mensaje": "recomienda", "perfil": {"filas": 10}})
    assert modelo.call_count == 3
    prompts = [llamada.args[0].to_string() for llamada in modelo.call_args_list]
    assert "diagnóstico medido" in prompts[1]
    assert "diagnóstico medido" in prompts[2] and "preparación derivada" in prompts[2]
    assert all('"filas": 10' in p for p in prompts)
    assert resultado["estrategia"] == "estrategia final"


@pytest.mark.parametrize("categoria,esperada", [
    (" PREPARACION\n", "preparacion"), ("Modelado", "modelado"),
    ("consulta", "consulta"), ("no_reconocida", "consulta"),
])
def test_normalizacion_y_cada_ruta_incluida_predeterminada(categoria, esperada):
    rutas = {k: Mock(return_value={"ruta": k}) for k in ["preparacion", "modelado", "consulta"]}
    cadena = construir_enrutamiento(paso_clasificacion=RunnableLambda(lambda _: categoria),
                                    rutas={k: RunnableLambda(v) for k, v in rutas.items()})
    resultado = cadena.invoke({"mensaje": "entrada original", "perfil": {"filas": 10}})
    assert resultado["resultado"] == {"ruta": esperada}
    for ruta, destino in rutas.items():
        assert destino.call_count == int(ruta == esperada)
    assert rutas[esperada].call_args.args[0]["mensaje"] == "entrada original"


def test_fallo_de_ruta_ejecuta_fallback_y_registra(caplog):
    def fallar(_):
        raise ConnectionError("simulado")
    rutas = {k: RunnableLambda(fallar) for k in ["preparacion", "modelado", "consulta"]}
    cadena = construir_enrutamiento(paso_clasificacion=RunnableLambda(lambda _: "modelado"), rutas=rutas)
    resultado = procesar_seguro(cadena, {"mensaje": "modelo", "perfil": {}})
    assert resultado["resultado"]["estado"] == "fallback"
    assert "perfil local" in resultado["resultado"]["respuesta"]
    assert "fallback" in caplog.text


def test_fallo_clasificacion_cubierto_por_entrada_general(caplog):
    def fallar(_):
        raise ConnectionError("simulado")
    rutas = {k: Mock() for k in ["preparacion", "modelado", "consulta"]}
    cadena = construir_enrutamiento(paso_clasificacion=RunnableLambda(fallar), rutas=rutas)
    assert procesar_seguro(cadena, {"mensaje": "prueba", "perfil": {}})["estado"] == "error"
    assert all(r.call_count == 0 for r in rutas.values())
    assert "ConnectionError" in caplog.text


def test_paso_truncado_no_alimenta_siguiente():
    modelo = Mock(return_value=AIMessage(content="incompleto", response_metadata={"finish_reason": "MAX_TOKENS"}))
    resultado = procesar_seguro(construir_cadena(modelo), {"mensaje": "prueba", "perfil": {}})
    assert resultado["estado"] == "error"
    assert modelo.call_count == 1


def test_validador_admite_fin_normal():
    mensaje = AIMessage(content="completo", response_metadata={"finish_reason": "STOP"})
    assert validar_salida(mensaje) is mensaje
