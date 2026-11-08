# Evaluación de texto — práctica 15 y métricas 16

La [práctica del bloque 15](https://learning-pro.skillnest.com/mod/page/view.php?id=15646) pide limpieza, tokenización, al menos tres respuestas reales y una comparación antes/después. El [bloque 16](https://learning-pro.skillnest.com/mod/page/view.php?id=15649) agrega precisión, cobertura y F1 contando repeticiones.

`src/pipeline_texto.py` normaliza mayúsculas, puntuación y espacios, y usa `Counter` para contar coincidencias. Maneja textos vacíos y se verifica en `tests/test_pipeline_texto.py`.

`src/evaluacion.py` aplica el pipeline a **20 respuestas reales** sobre el perfil de [Iranian Churn](datos-prueba-iranian-churn.md). Las referencias se escriben antes de consultar. Los [resultados](evidencias/resultados_metricas.json) guardan consulta, referencia, respuesta, métricas, versión, modelo, fecha y huella del CSV.

| Caso | Coincidencia cruda | Tras procesar |
|---|---:|---:|
| `columnas` | 40% | 60% |
| `objetivo` | 45,45% | 72,73% |

El F1 léxico promedio fue **0,323**. Su interpretación y la revisión de respuestas corresponden a la [core 17](bloque-17-core-limites-metrica.md); no mide rendimiento predictivo.

## Reproducción

```bash
python -m pytest tests/test_pipeline_texto.py -v
python -m src.evaluacion --ejecutar
```

El segundo comando consulta Gemini y consume cuota; conserva los casos ya completados para la misma configuración. [Casos y referencias](evidencias/casos_evaluacion.json).

Las evidencias usan `gemini-3.5-flash-lite`: el modelo inicialmente configurado, `gemini-3.6-flash`, agotó su cuota diaria con HTTP 429. El cliente rechaza respuestas truncadas o bloqueadas y excluye partes de razonamiento. El consumo REST incluye una estimación con tarifa didáctica, sin representar cargos comprobados.
