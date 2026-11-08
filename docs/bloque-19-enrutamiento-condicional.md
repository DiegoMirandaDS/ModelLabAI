# Enrutamiento condicional — bloque 19

El [flujo condicional](https://learning-pro.skillnest.com/mod/page/view.php?id=15658) vive en `construir_enrutamiento`, en `src/orquestacion.py`.

La clasificación se normaliza con `strip().lower()`. `RunnablePassthrough.assign` conserva la entrada y agrega la categoría; `RunnableBranch` selecciona el destino:

| Categoría | Destino |
|---|---|
| `preparacion` | Chain de tres pasos enfocada en calidad y ETL |
| `modelado` | Chain de tres pasos enfocada en clasificación y evaluación |
| `consulta` o categoría desconocida | Prompt de aclaración |

Las dos primeras rutas reutilizan la [chain del bloque 18](bloque-18-practica-chain-tres-pasos.md) con enfoques distintos. La predeterminada tiene su propio prompt.

`tests/test_orquestacion.py` prueba cada ruta, la normalización y una categoría desconocida, conservando el mensaje original. Las corridas reales están identificadas como `ruta_preparacion`, `ruta_modelado` y `ruta_consulta` en las [evidencias](evidencias/orquestacion_agente.json).

```bash
python -m src.demo --modo enrutamiento --mensaje "Revisa la calidad antes del ETL" --consultar
```

El comando consulta Gemini y consume cuota. La recuperación ante errores está documentada en la [core 20](bloque-20-core-verificacion-orquestacion.md).
