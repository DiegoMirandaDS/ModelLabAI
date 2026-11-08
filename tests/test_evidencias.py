"""Coherencia entre el dataset, las corridas reales y la revisión documentada."""

import hashlib
import json

import pytest

from src.datos import CSV, RAIZ
from src.evaluacion import construir_casos

CARPETA = RAIZ / "docs/evidencias"


def leer(nombre):
    return json.loads((CARPETA / nombre).read_text(encoding="utf-8"))


def test_evaluacion_real_tiene_20_casos_trazables():
    resultados = leer("resultados_metricas.json")
    casos = leer("casos_evaluacion.json")
    perfil = leer("perfil_iranian_churn.json")
    assert len(resultados) == 20 and len({r["id"] for r in resultados}) == 20
    assert construir_casos(perfil) == casos
    assert {r["id"] for r in resultados} == {c["id"] for c in casos}
    assert len({r["version_evaluacion"] for r in resultados}) == 1
    huella = hashlib.sha256(CSV.read_bytes()).hexdigest()
    for caso, resultado in zip(casos, resultados):
        assert all(resultado[k] == caso[k] for k in ("id", "consulta", "referencia"))
        assert resultado["sha256_csv"] == huella
        assert resultado["respuesta"].strip() and resultado["modelo"] and resultado["fecha_utc"]
        assert resultado["consumo"][0]["tokens"]["totalTokenCount"] > 0
    assert any(r["coincidencia_cruda"] != r["coincidencia_procesada"] for r in resultados[:3])


def test_revision_incluye_cinco_menores_y_cinco_mayores_con_notas():
    resultados = sorted(leer("resultados_metricas.json"), key=lambda x: x["f1"])
    revision = leer("revision_manual.json")
    assert len(revision) == 10
    assert {r["id"] for r in revision} == {r["id"] for r in resultados[:5] + resultados[-5:]}
    por_id = {r["id"]: r for r in resultados}
    for r in revision:
        assert r["f1"] == pytest.approx(por_id[r["id"]]["f1"])
        assert r["correccion_factual"] in {"si", "no", "parcialmente"}
        assert r["completitud"] in {"si", "no", "parcialmente"}
        assert r["contradiccion"] in {"si", "no"} and r["nota"].strip()


def test_corridas_reales_cubren_chain_rutas_y_herramientas():
    registros = {r["id"]: r for r in leer("orquestacion_agente.json")}
    assert set(registros) == {
        "cadena", "ruta_preparacion", "ruta_modelado", "ruta_consulta",
        "agente_perfil", "agente_balance", "agente_general",
    }
    huella = hashlib.sha256(CSV.read_bytes()).hexdigest()
    for r in registros.values():
        assert r["sha256_csv"] == huella and r["verificacion"] == "correcta"
        assert r["llamadas"] and all(c["finish_reason"] == "STOP" for c in r["llamadas"])
    assert len(registros["cadena"]["llamadas"]) == 3
    for ruta in ("preparacion", "modelado", "consulta"):
        assert registros[f"ruta_{ruta}"]["resultado"]["categoria"] == ruta
    pasos = registros["agente_perfil"]["resultado"]["pasos"]
    assert [p["herramienta"] for p in pasos] == ["consultar_perfil_dataset"]
    assert json.loads(pasos[0]["observacion"])["filas"] == 3150
    pasos = registros["agente_balance"]["resultado"]["pasos"]
    assert [p["herramienta"] for p in pasos] == ["calcular_balance_objetivo"]
    assert json.loads(pasos[0]["observacion"])["conteos"] == {"0": 2655, "1": 495}
    assert registros["agente_general"]["resultado"]["pasos"] == []
