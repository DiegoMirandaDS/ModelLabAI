# Iranian Churn: datos reales de prueba y controles de calidad

La demostración de los bloques 15–21 usa [Iranian Churn, UCI](https://archive.ics.uci.edu/dataset/563/iranian+churn+dataset), con licencia CC BY 4.0. La atribución y la huella del archivo están en [data](../data/README.md). Es una muestra histórica de telecomunicaciones; no acredita comportamiento actual ni resultados para clientes de otra empresa.

## Resultados del perfilado

| Control | Resultado | Implicación |
|---|---|---|
| Tamaño | 3.150 registros, 14 columnas | 13 atributos y `Churn` |
| Valores faltantes | 0 | El archivo original no necesita imputación por nulos |
| Abandono | 495 positivos, 15,7143% | Evaluar la clase minoritaria; accuracy sola no basta |
| Permanencia | 2.655 negativos, 84,2857% | Referencia mayoritaria, sin modelo entrenado |
| Repeticiones | 300 filas adicionales; 465 registros en grupos repetidos | No prueban identidad de cliente: falta un identificador verificable |
| Predictores iguales, etiquetas distintas | 14 grupos | No formar los grupos de partición usando la etiqueta objetivo |
| `Charge Amount` | 7 registros con valor 10 | Discrepancia frente al dominio 0–9 documentado; se conserva el valor y se señala |

`src/datos.py` calcula conteos, nulos, cardinalidad, rangos, medianas y dominios categóricos. El [perfil completo](evidencias/perfil_iranian_churn.json) y el [control de predictores](evidencias/controles_predictores.json) conservan los resultados. La suite contrasta los totales y la huella del CSV, y prueba copias alteradas sin cambiar el original.

## Decisiones de uso

Los códigos de `Tariff Plan`, `Status`, `Complains`, `Age Group` y `Charge Amount` tienen significado categórico u ordinal, aunque se almacenen como números. El valor 10 de `Charge Amount` se marca como anomalía; no se reemplaza por 9 ni se elimina automáticamente.

UCI sitúa los atributos en los primeros nueve meses y el abandono al finalizar doce meses. El CSV no contiene fechas individuales, por lo que no demuestra una validación cronológica. Tampoco permite verificar la identidad de cada cliente. Para una evaluación predictiva, las filas con predictores idénticos deben permanecer en la misma partición y las transformaciones se ajustan solo con entrenamiento.

Gemini recibe estadísticas agregadas y contexto del dataset. El perfilado y las herramientas calculan datos; las recomendaciones generativas no ejecutan ETL ni entrenan modelos.
