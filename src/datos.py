"""Carga y perfilado local de Iranian Churn; nunca modifica el CSV original."""

import argparse
import hashlib
import io
import json
from pathlib import Path
import zipfile

import pandas as pd
import requests

RAIZ = Path(__file__).resolve().parents[1]
CSV = RAIZ / "data/raw/iranian_churn.csv"
URL = "https://archive.ics.uci.edu/static/public/563/iranian%2Bchurn%2Bdataset.zip"
FUENTE = "https://archive.ics.uci.edu/dataset/563/iranian+churn+dataset"
CONTEXTO = {
    "unidad": "Una fila por registro de cliente; sin identificador verificable en el CSV",
    "objetivo_negocio": "Predecir abandono de clientes de telecomunicaciones",
    "columna_objetivo": "Churn",
    "clase_positiva": 1,
    "significado": {"0": "no abandona", "1": "abandona"},
    "ventana": "Atributos de los primeros 9 meses; abandono al mes 12; brecha de 3 meses (UCI)",
    "limite_temporal": "El CSV no contiene fechas individuales: no permite verificar un corte cronológico",
    "codigos_categoricos": {
        "Complains": [0, 1], "Age Group": [1, 2, 3, 4, 5],
        "Tariff Plan": [1, 2], "Status": [1, 2], "Charge Amount": list(range(10)),
    },
}


def guardar_json(ruta, datos):
    """Escribe UTF-8 y reemplaza el destino solo después de completar la escritura."""
    ruta = Path(ruta)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    temporal = ruta.with_suffix(ruta.suffix + ".tmp")
    temporal.write_text(json.dumps(datos, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    temporal.replace(ruta)


def descargar():
    """Obtiene el archivo oficial y conserva sus bytes sin alterar."""
    if CSV.exists():
        return CSV
    respuesta = requests.get(URL, timeout=60)
    respuesta.raise_for_status()
    with zipfile.ZipFile(io.BytesIO(respuesta.content)) as archivo:
        nombres = [n for n in archivo.namelist() if n.lower().endswith(".csv")]
        if len(nombres) != 1:
            raise ValueError("El paquete UCI debe contener exactamente un CSV")
        contenido = archivo.read(nombres[0])
    CSV.parent.mkdir(parents=True, exist_ok=True)
    CSV.write_bytes(contenido)
    guardar_json(CSV.parent / "origen.json", {
        "dataset": "Iranian Churn", "fuente": FUENTE, "descarga": URL,
        "doi": "10.24432/C5JW3Z", "licencia": "CC BY 4.0",
        "sha256": hashlib.sha256(contenido).hexdigest(),
        "transformacion": "Ninguna; archivo renombrado a iranian_churn.csv",
    })
    return CSV


def cargar_csv(ruta=CSV):
    tabla = pd.read_csv(ruta)
    tabla.columns = [" ".join(str(nombre).split()) for nombre in tabla.columns]
    if tabla.empty or tabla.columns.duplicated().any():
        raise ValueError("La tabla debe contener filas y nombres de columnas únicos")
    if "Churn" not in tabla:
        raise ValueError("Falta la columna objetivo Churn")
    for nombre in tabla:
        if not pd.api.types.is_numeric_dtype(tabla[nombre]):
            raise ValueError(f"Tipo inválido en {nombre}: este dataset requiere valores numéricos")
    return tabla


def balance_objetivo(tabla, objetivo="Churn"):
    if objetivo not in tabla:
        raise ValueError(f"No existe la columna objetivo: {objetivo}")
    serie = tabla[objetivo]
    if serie.isna().any() or set(serie.unique()) != {0, 1}:
        raise ValueError("El objetivo debe contener las dos clases 0 y 1 y ningún nulo")
    conteos = {str(int(k)): int(v) for k, v in serie.value_counts().sort_index().items()}
    return {
        "columna": objetivo, "clase_positiva": 1, "conteos": conteos,
        "porcentajes": {k: round(v / len(tabla) * 100, 4) for k, v in conteos.items()},
    }


def perfilar(tabla):
    """Calcula estadísticas observadas sin inferir semántica por el tipo numérico."""
    columnas = []
    for nombre in tabla:
        serie = tabla[nombre]
        fila = {
            "nombre": nombre, "tipo_observado": str(serie.dtype),
            "nulos": int(serie.isna().sum()), "nulos_pct": round(float(serie.isna().mean() * 100), 4),
            "distintos": int(serie.nunique()),
        }
        if pd.api.types.is_numeric_dtype(serie) and serie.notna().any():
            fila.update(minimo=float(serie.min()), maximo=float(serie.max()), mediana=float(serie.median()))
        if nombre in CONTEXTO["codigos_categoricos"]:
            fila["valores_fuera_de_dominio"] = int((serie.notna() & ~serie.isin(CONTEXTO["codigos_categoricos"][nombre])).sum())
        columnas.append(fila)
    return {
        "dataset_id": "iranian_churn", "fuente": FUENTE, "contexto": CONTEXTO,
        "filas": len(tabla), "columnas_total": len(tabla.columns),
        "duplicados_exactos_adicionales": int(tabla.duplicated().sum()),
        "registros_en_grupos_duplicados": int(tabla.duplicated(keep=False).sum()),
        "columnas": columnas, "objetivo": balance_objetivo(tabla),
    }


def perfil_publico():
    """Perfil agregado del único dataset permitido; no acepta rutas del usuario."""
    perfil = perfilar(cargar_csv())
    perfil["sha256_csv"] = hashlib.sha256(CSV.read_bytes()).hexdigest()
    return perfil


def auditar_predictores(tabla):
    """Detecta perfiles idénticos sin usar la etiqueta para formar los grupos."""
    predictores = list(tabla.columns.drop("Churn"))
    grupos = tabla.groupby(predictores, dropna=False)["Churn"]
    return {
        "criterio_grupo": "Todas las columnas predictoras, excluyendo Churn",
        "grupos_con_etiquetas_distintas": int(grupos.nunique().gt(1).sum()),
        "grupos_con_mas_de_un_registro": int(grupos.size().gt(1).sum()),
        "interpretacion": "Perfiles iguales no prueban identidad; se mantienen juntos al proponer particiones",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--descargar", action="store_true")
    args = parser.parse_args()
    if args.descargar:
        descargar()
    perfil = perfil_publico()
    guardar_json(RAIZ / "docs/evidencias/perfil_iranian_churn.json", perfil)
    guardar_json(RAIZ / "docs/evidencias/controles_predictores.json", auditar_predictores(cargar_csv()))
    print(json.dumps(perfil, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
