import json

from langchain_core.language_models.fake_chat_models import FakeMessagesListChatModel
from langchain_core.messages import AIMessage

from src.agente import construir_agente, construir_herramientas
from src.demo import texto_salida_agente


class ModeloConHerramientasFalso(FakeMessagesListChatModel):
    def bind_tools(self, tools, **kwargs):
        return self


def test_herramientas_calculan_datos_reales_y_devuelven_texto():
    perfil, balance = construir_herramientas()
    datos = json.loads(perfil.invoke({"dataset_id": "iranian_churn"}))
    assert datos["filas"] == 3150 and "objetivo" not in datos
    datos = json.loads(balance.invoke({"dataset_id": "iranian_churn"}))
    assert datos["conteos"] == {"0": 2655, "1": 495}


def test_herramientas_no_aceptan_rutas_ni_otro_objetivo():
    perfil, balance = construir_herramientas()
    assert "No se pudo" in perfil.invoke({"dataset_id": "../../.env"})
    assert "No se pudo" in balance.invoke({"dataset_id": "iranian_churn", "columna_objetivo": "Age"})


def test_ciclo_del_agente_conserva_observacion_y_traza():
    modelo = ModeloConHerramientasFalso(responses=[
        AIMessage(content="", tool_calls=[{"name": "calcular_balance_objetivo", "args": {"dataset_id": "iranian_churn"}, "id": "llamada-1"}]),
        AIMessage(content="Hay 495 abandonos."),
    ])
    resultado = construir_agente(modelo).invoke({"entrada": "calcula balance"})
    accion, observacion = resultado["intermediate_steps"][0]
    assert accion.tool == "calcular_balance_objetivo"
    assert json.loads(observacion)["conteos"]["1"] == 495
    assert resultado["output"] == "Hay 495 abandonos."


def test_pregunta_general_no_necesita_herramientas():
    modelo = ModeloConHerramientasFalso(responses=[AIMessage(content="ETL significa extraer, transformar y cargar.")])
    assert construir_agente(modelo).invoke({"entrada": "qué es ETL"})["intermediate_steps"] == []


def test_salida_en_bloques_conserva_solo_texto():
    assert texto_salida_agente([{"type": "text", "text": "Resultado calculado."}]) == "Resultado calculado."
    assert texto_salida_agente("Texto simple.") == "Texto simple."
