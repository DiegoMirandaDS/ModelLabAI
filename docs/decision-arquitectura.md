# ADR-001: Selección del modelo de lenguaje

**Proyecto:** ModelLab AI  
**Fecha:** 23-10-2026  
**Estado:** Decisión para prototipo  
**Responsable:** Diego Miranda

## 1. Modelo elegido

Se selecciona `gemini-3.8-flash` como modelo inicial para el desarrollo experimental de ModelLab AI, mediante la API REST de Google Gemini.

ModelLab AI busca facilitar la interpretación de métricas, el diagnóstico de problemas y la explicación de resultados de modelos de Machine Learning.

La selección es provisional: se reevaluara cuando se disponga de pruebas representativas de calidad para estas tareas.

## 2. Diagrama de arquitectura

El sistema separa la construcción de la solicitud, el envío HTTP y el procesamiento de respuestas.

![Arquitectura de ModelLab AI](diagrama_arquitectura.png)

El archivo fuente editable es `arquitectura.dot`. También se dispone de una versión SVG.

La clave `GEMINI_API_KEY` se obtiene desde `.env` utilizando `python-dotenv` y se transmite mediante la cabecera `x-goog-api-key`.

El módulo contiene funciones para extraer texto y calcular costos a partir de `usageMetadata`.

## 3. Comparación de candidatos

Se compararon `gemini-3.8-flash` y `gemini-3.6-flash`, mediante cuatro intentos por modelo con una misma pregunta sobre overfitting.

**Fecha de medición:** 21-10-2026.

| Criterio | Gemini 3.8 Flash | Gemini 3.6 Flash |
|---|---:|---:|
| Precio entrada, USD/1.000 tokens | 0.00075 | 0.00075 |
| Precio salida, USD/1.000 tokens | 0.00375 | 0.00375 |
| Respuestas exitosas | 2/4 | 4/4 |
| Latencia media exitosa | 27.00 s | 7.92 s |
| Tokens de entrada medios | 16 | 16 |
| Tokens de salida facturables medios | 1261 | 1316.8 |
| Costo medio por petición exitosa | USD 0.00474075 | USD 0.00494981 |

Las latencias se promediaron únicamente entre las peticiones exitosas. Gemini 3.8 presentó dos errores por agotamiento del tiempo de espera.

### Evaluación de calidad

Las respuestas registradas explican el concepto de sobreajuste y proponen técnicas de prevención.

No se aplicó una rúbrica cuantitativa de calidad en el benchmark inicial. Sin embargo, gemini-3.8-flash corresponde a una evolución natural de los modelos gemini se la serie 3-flash, por lo que se asume que su desempeño en tareas generales debe ser superior (demostrado por benchmarks oficiales).

### Fuente de evidencia

- [Comparación experimental completa](comparacion_modelos.md)
- [Precios oficiales de Gemini](https://ai.google.dev/gemini-api/docs/pricing)
- [Documentación de modelos](https://ai.google.dev/gemini-api/docs/models)

## 4. Justificación de la elección

Se selecciona provisionalmente Gemini 3.8 Flash porque el proyecto está orientado a interpretar modelos y resolver tareas técnicas de Machine Learning.

Google posiciona este modelo para tareas complejas y flujos relacionados con ingeniería de software.

En el contexto actual, ModelLab AI es un prototipo educativo que prioriza la exploración de capacidades sobre la respuesta inmediata.

Si bien la prueba realizada favorece claramente a Gemini 3.6 en latencia (probablemente debido a problemas de saturación) y porcentaje de solicitudes exitosas, se considera que por un valor similar y conociendo que Gemini 3.8 es su evolución oficial, este es el modelo óptimo para el proyecto. Si se observa que durante pruebas en modulos futuros Gemini 3.8 sigue presentando problemas de solicitudes y latencia, se considerará el fallback a 3.6.

## 5. Alternativa descartada

`gemini-3.6-flash` no se selecciona como modelo principal del prototipo.

Sin embargo, sus resultados fueron favorables: respondió los cuatro intentos y presentó una latencia considerablemente menor.

Se conservará como alternativa técnica para tareas simples o situaciones donde la velocidad y la disponibilidad sean prioritarias.

Si Gemini 3.8 mantiene tasas elevadas de timeout o no ofrece ventajas significativas en calidad, se reconsiderará la decisión.

## 6. Riesgos y trabajo futuro

- Repetir pruebas de latencia con más muestras.
- Evaluar calidad mediante una rúbrica común.
- Limitar la longitud de respuestas para controlar costos.
- Implementar reintentos controlados ante errores temporales.
- Evaluar escalabilidad y límites de cuota antes del despliegue.

La arquitectura mantiene el modelo configurable mediante `GEMINI_MODEL`, facilitando comparaciones posteriores.