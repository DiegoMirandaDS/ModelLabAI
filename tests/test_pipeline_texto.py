import pytest

from src.pipeline_texto import (
    procesar_texto, calcular_metricas, calcular_precision_cobertura_f1,
    contar_coincidencias, coincidencia_palabras,
)


def test_normalizacion_conserva_espanol_y_numeros():
    assert procesar_texto("  El Cielo, es AZUL! Niñez 15. ") == ["el", "cielo", "es", "azul", "niñez", "15"]


@pytest.mark.parametrize("texto", ["", "¡¡¡...!!!", "  \n "])
def test_texto_vacio(texto):
    assert procesar_texto(texto) == []
    assert calcular_metricas(texto, "respuesta") == {"precision": 0, "cobertura": 0, "f1": 0}


def test_entrada_no_textual_es_error():
    with pytest.raises(TypeError):
        procesar_texto(None)


def test_repeticiones_no_inflan_coincidencias():
    assert contar_coincidencias(["el", "gato"], ["el", "gato", "el", "gato"]) == 2
    assert calcular_metricas("el gato", "el gato el gato") == pytest.approx(
        {"precision": 0.5, "cobertura": 1, "f1": 2 / 3}
    )


def test_ejemplo_calculado_a_mano():
    assert calcular_metricas("El gato duerme en el sofá.", "El gato duerme en el sillón todo el día.") == pytest.approx(
        {"precision": 5 / 9, "cobertura": 5 / 6, "f1": 2 / 3}
    )


def test_rechaza_cadenas_en_funcion_de_tokens():
    with pytest.raises(TypeError):
        calcular_precision_cobertura_f1("el gato", ["el"])


def test_antes_y_despues():
    assert coincidencia_palabras("El Gato.", "el gato", False) == 0
    assert coincidencia_palabras("El Gato.", "el gato") == 1


def test_f1_alto_no_detecta_negacion():
    assert calcular_metricas("No imputar los valores observados", "Imputar los valores observados")["f1"] > 0.8
