# Límites de la métrica de evaluación — core 17

## Qué mide

Coincidencia de palabras entre referencia y respuesta, después de normalizar mayúsculas, puntuación y espacios. Se cuentan repeticiones con `Counter`: precisión = coincidencias / tokens de respuesta; cobertura = coincidencias / tokens de referencia; F1 = media armónica. Si uno de los textos queda vacío, las tres métricas valen cero.

Las 20 respuestas reales obtuvieron F1 promedio **0,323** (precisión 0,228; cobertura 0,600). Estos números describen similitud léxica, no exactitud factual ni rendimiento de un clasificador.

## Modos de falla conocidos

- **Redacción equivalente:** `imputacion` responde correctamente que no hacen falta imputaciones, pero obtiene F1 **0,171** al decir «no hace falta» y usar otra estructura.
- **Formato numérico:** `uso` devuelve correctamente 0,0 y 17.090,0 frente a los enteros de la referencia y obtiene F1 **0,194**. La limpieza elimina signos, pero no convierte números a una representación canónica.
- **Texto adicional:** `duplicados` da el conteo correcto de 300 y agrega una recomendación; su F1 es **0,176**. Las presentaciones «Soy ModelLab AI» también añaden palabras que la referencia no necesita.
- **Omisión de contenido:** `metricas` explica por qué accuracy no basta, pero omite precisión, recall, F1, PR-AUC y matriz de confusión. Su F1 **0,182** es parecido al de respuestas correctas y completas: el número no explica la causa.
- **Negaciones:** la prueba de control en `tests/test_pipeline_texto.py` compara «No imputar los valores observados» con «Imputar los valores observados»: F1 **0,889**, aunque invierte la instrucción. Es un control construido, no un fallo observado en las diez respuestas revisadas.

## Muestra revisada

El 8 de noviembre de 2026 se revisaron caso por caso **10 de 20 respuestas** de `gemini-3.5-flash-lite`: las cinco con menor F1 y las cinco con mayor F1. Consulta, referencia y respuesta están en [resultados](evidencias/resultados_metricas.json); la rúbrica y la justificación de cada caso están en [revisión manual](evidencias/revision_manual.json).

| Grupo | Casos |
|---|---|
| Cinco menores | `imputacion`, `duplicados`, `metricas`, `uso`, `resultados` |
| Cinco mayores | `ventana`, `objetivo`, `balance`, `negativos`, `nulos` |

Los diez casos conservan datos verificables correctos y no contradicen la referencia. Ocho cubren lo solicitado; `metricas` y `resultados` tienen completitud parcial. Este último menciona ausencia de métricas, pero no afirma con claridad que el perfilado no entrena ni demuestra rendimiento. La muestra se eligió por extremos de F1, no al azar: no estima una tasa general de calidad.

## Recomendación de uso

Usar estas métricas para localizar cambios entre respuestas evaluadas con las mismas referencias y reglas de limpieza. Revisar números, negaciones y decisiones de preparación directamente contra el perfil y la documentación del dataset. En ModelLab AI, un F1 bajo no descarta una recomendación y un F1 alto no autoriza ejecutar un tratamiento. La revisión cualitativa determina si la respuesta es correcta, completa y coherente.
