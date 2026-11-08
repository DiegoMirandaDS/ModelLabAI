# Bloques 15–21: implementación y evidencias

ModelLab AI usa **Iranian Churn**, un CSV real de 3.150 registros. El código calcula el perfil; Gemini interpreta los resultados y propone preparación y validación. Las evidencias reales usan `gemini-3.5-flash-lite` y conservan la huella del CSV, el modelo y la fecha.

## Correspondencia con las actividades

| Bloque | Requisito | Implementación y evidencia |
|---|---|---|
| [15 · Práctica](https://learning-pro.skillnest.com/mod/page/view.php?id=15646) | Limpieza, tokenización, tres respuestas reales y antes/después | [Pipeline](../src/pipeline_texto.py), [pruebas](../tests/test_pipeline_texto.py) y [resultados](evidencias/resultados_metricas.json): 20 casos, incluidos los tres iniciales |
| [16 · Métricas](https://learning-pro.skillnest.com/mod/page/view.php?id=15649) | Precisión, cobertura y F1 contando repeticiones | `Counter`, manejo de vacíos y [evaluación integrada](../src/evaluacion.py); consulta, referencia, respuesta y métricas guardadas por caso |
| [17 · Core](https://learning-pro.skillnest.com/mod/page/view.php?id=15652) | 20 respuestas, revisión de 10 y límites documentados | [Revisión cualitativa](evidencias/revision_manual.json) con cinco menores y cinco mayores; [documento de cuatro secciones](limites_metrica.md) |
| [18 · Práctica](https://learning-pro.skillnest.com/mod/page/view.php?id=15655) | Tres templates dependientes, LCEL, parsers y corrida completa | [Orquestación](../src/orquestacion.py): diagnóstico → preparación → estrategia; la prueba verifica el paso de información entre los tres |
| [19 · Enrutamiento](https://learning-pro.skillnest.com/mod/page/view.php?id=15658) | Categoría normalizada y pruebas de todas las rutas | Preparación, modelado y aclaración por defecto; [pruebas de selección](../tests/test_orquestacion.py), incluida categoría desconocida |
| [20 · Core](https://learning-pro.skillnest.com/mod/page/view.php?id=15700) | Fallback probado y protección general, incluida clasificación | `with_fallbacks` por destino y `procesar_seguro`; las pruebas fuerzan fallo de ruta y de clasificación, verifican respuesta y registro del error |
| [21 · Práctica](https://learning-pro.skillnest.com/mod/page/view.php?id=15703) | Dos herramientas propias y dos decisiones reales comprobadas | [Agente](../src/agente.py): perfil y balance; [trazas reales](evidencias/orquestacion_agente.json), más una consulta general sin herramientas |

## Resultados que explican las decisiones

- **Datos:** 0 nulos, 300 repeticiones adicionales, 495 abandonos y 7 valores de `Charge Amount` fuera del dominio documentado. Se conservan los registros originales. [Detalle](dataset.md).
- **Antes/después:** en el caso `columnas`, la coincidencia simple pasa de 40% a 60%; en `objetivo`, de 45,45% a 72,73%. Se normalizan ambos textos de la misma manera.
- **Evaluación:** F1 léxico promedio 0,323. La revisión encuentra ocho respuestas completas y dos parciales entre las diez seleccionadas; un puntaje bajo no distingue por sí solo una paráfrasis de una omisión.
- **Orquestación:** una corrida de tres pasos, las tres rutas y tres consultas del agente. Las trazas registran herramienta, argumentos y observación, además de tokens reportados.

## Reproducibilidad

```bash
python -m pytest -v
python -m src.demo --modo perfil
```

Estas verificaciones no necesitan API. La suite completa pasó con **77 pruebas**; la [salida de pytest](evidencias/bloques-15-21-pytest.txt) conserva el resultado.

Las llamadas reales se reproducen con `python -m src.evaluacion --ejecutar` y `python -m src.demo --evidencias --consultar`. Guardan avances y consumen cuota. Las referencias se escriben antes de consultar; la revisión cualitativa corresponde a esas respuestas concretas. [Casos y referencias](evidencias/casos_evaluacion.json).

El modelo inicialmente configurado, `gemini-3.6-flash`, devolvió HTTP 429 por cuota diaria agotada. Se verificó respuesta del modelo alternativo y se utilizó una sola configuración para las evidencias finales. El cliente rechaza respuestas truncadas o bloqueadas y excluye partes de razonamiento. Los tokens REST se conservan con una estimación didáctica; LangChain registra tokens sin inventar precios.

El alcance es carga, perfilado, evaluación de texto y recomendación orquestada. No se ejecutaron transformaciones ni entrenamientos; las métricas de texto no acreditan rendimiento predictivo.
