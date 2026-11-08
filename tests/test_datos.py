import hashlib
import json

import pytest

from src.datos import CSV, cargar_csv, perfilar, balance_objetivo, auditar_predictores


def test_archivo_oficial_y_perfil_reconciliados():
    tabla = cargar_csv()
    perfil = perfilar(tabla)
    origen = json.loads((CSV.parent / "origen.json").read_text())
    assert hashlib.sha256(CSV.read_bytes()).hexdigest() == origen["sha256"]
    assert tabla.shape == (3150, 14)
    assert sum(c["nulos"] for c in perfil["columnas"]) == 0
    assert perfil["duplicados_exactos_adicionales"] == 300
    assert perfil["registros_en_grupos_duplicados"] == 465
    assert balance_objetivo(tabla)["conteos"] == {"0": 2655, "1": 495}
    assert sum(balance_objetivo(tabla)["porcentajes"].values()) == pytest.approx(100)
    cargo = next(c for c in perfil["columnas"] if c["nombre"] == "Charge Amount")
    assert cargo["valores_fuera_de_dominio"] == 7
    assert cargo["maximo"] == 10
    assert auditar_predictores(tabla)["grupos_con_etiquetas_distintas"] == 14


def test_variante_con_nulos_sin_modificar_original(tmp_path):
    original = CSV.read_bytes()
    tabla = cargar_csv().copy()
    tabla["Seconds of Use"] = tabla["Seconds of Use"].astype(float)
    tabla.loc[:30, "Seconds of Use"] = float("nan")
    ruta = tmp_path / "con_nulos.csv"
    tabla.to_csv(ruta, index=False)
    columna = next(c for c in perfilar(cargar_csv(ruta))["columnas"] if c["nombre"] == "Seconds of Use")
    assert columna["nulos"] == 31
    assert columna["nulos_pct"] == pytest.approx(31 / 3150 * 100, abs=0.0001)
    assert CSV.read_bytes() == original


def test_variante_con_duplicado_adicional():
    import pandas as pd
    tabla = cargar_csv()
    assert perfilar(pd.concat([tabla, tabla.iloc[[0]]], ignore_index=True))["duplicados_exactos_adicionales"] == 301


def test_variante_con_tipo_invalido(tmp_path):
    tabla = cargar_csv()
    tabla["Seconds of Use"] = tabla["Seconds of Use"].astype(object)
    tabla.loc[0, "Seconds of Use"] = "invalido"
    ruta = tmp_path / "tipo_invalido.csv"
    tabla.to_csv(ruta, index=False)
    with pytest.raises(ValueError, match="Tipo inválido"):
        cargar_csv(ruta)


def test_variante_sin_objetivo(tmp_path):
    ruta = tmp_path / "sin_objetivo.csv"
    cargar_csv().drop(columns="Churn").to_csv(ruta, index=False)
    with pytest.raises(ValueError, match="objetivo"):
        cargar_csv(ruta)


@pytest.mark.parametrize("valores", [[0, 0], [0, 2], [0, None]])
def test_balance_rechaza_objetivo_invalido(valores):
    import pandas as pd
    with pytest.raises(ValueError, match="dos clases"):
        balance_objetivo(pd.DataFrame({"Churn": valores}))
