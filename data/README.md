# Datos de demostración

**Iranian Churn**, UCI Machine Learning Repository (2020). [Fuente](https://archive.ics.uci.edu/dataset/563/iranian+churn+dataset) · [DOI](https://doi.org/10.24432/C5JW3Z) · [Licencia CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

`raw/iranian_churn.csv` conserva los bytes del CSV oficial, únicamente renombrado. `raw/origen.json` contiene la URL de descarga y su SHA-256. El archivo tiene 3.150 registros y 14 columnas: 13 atributos y el objetivo `Churn` (1 = abandono).

La carga normaliza los espacios en los encabezados en memoria. No modifica valores ni elimina filas. Las variantes con nulos, tipos inválidos y columnas ausentes se crean en archivos temporales durante las pruebas; no se confunden con datos originales.

Para descargar y generar el perfil:

```bash
python -m src.datos --descargar
```

Si el CSV ya existe, el comando lo conserva. La prueba de integridad compara su huella con `raw/origen.json`.
