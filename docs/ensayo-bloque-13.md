# Ensayo real de rate limit — Bloque 13

Fecha: 29 de octubre de 2026, 18:37:56 a 18:38:17 (America/Santiago).
Modelo utilizado: `gemini-3.6-flash`, configurado en el entorno del proyecto.

## Objetivo y ejecución

Comprobar el cliente actualizado frente a un HTTP 429 real, con reintentos, espera con jitter y registro de consumo. Se utilizó la API de Gemini sin mocks, con peticiones secuenciales, preguntas cortas y respuestas limitadas a 128 tokens de salida por petición.

El ensayo tenía un máximo de diez operaciones y tres intentos por operación. Se detuvo después de completar la primera operación que recibió un 429. No se modificaron cuotas, credenciales ni facturación.

```bash
python -m src.ensayo_rate_limit --ejecutar
```

Sin `--ejecutar`, el módulo solo muestra la ayuda y no consulta la API.

## Resultados observados

| Medida | Resultado |
|---|---|
| Operaciones lógicas completadas | 7 de 7 iniciadas |
| Peticiones HTTP con respuesta | 8, incluido el reintento |
| Primer HTTP 429 | Petición HTTP 7; primer intento de la operación 7 |
| Espera programada con sleep real | 2.002360792797762 segundos |
| Respuesta del reintento | HTTP 200, texto `OK` |
| Registros de costo | 7, uno por cada respuesta exitosa |
| Tokens totales reportados en éxitos | 813 |
| Tarifa utilizada | Didáctica: USD 0.002 por 1000 tokens |
| Costo estimado total | USD 0.001626 |

La secuencia observada fue `200, 200, 200, 200, 200, 200, 429, 200`. El intento con 429 no generó un registro de costo adicional; la operación recuperada se registró una sola vez.

El costo anterior es una estimación referencial calculada a partir de tokens reales. No corresponde a una tarifa vigente verificada ni a un cargo comprobado. No permite inferir cargos por peticiones fallidas o consumo no reportado.

## Evidencia reproducible

[Registro JSON completo del ensayo](evidencias/bloque-13-20261029T213756336865Z.json).

El registro contiene las horas UTC de cada evento, código HTTP, operación asociada, espera programada, consumo reportado y acumulado. No contiene la clave, encabezados de autenticación ni datos del usuario; las preguntas y respuestas del ensayo son sintéticas.

El cliente emite eventos mediante `logging`. El script instala un observador que guarda esos eventos y los muestra en consola, sin sustituir la API ni la espera real. La opción `max_output_tokens` limita la salida de las peticiones del ensayo.

## Comprobación de requisitos

- Backoff exponencial con techo y jitter: implementado en el cliente. En este ensayo solo fue necesario el primer reintento; no se observó una segunda espera de cuatro segundos ni se afirma haberla observado.
- HTTP 429 real y recuperación: comprobados por la secuencia de respuestas del proveedor.
- Costo por operación y acumulado: siete registros, coherentes con las siete respuestas exitosas y los 813 tokens reportados.
- Error final al agotar intentos: cubierto por las pruebas unitarias del cliente y del ensayo. No ocurrió en esta ejecución real, que se recuperó.

Google documenta límites por proyecto y distintas dimensiones de cuota; el código HTTP observado no identifica por sí solo cuál se alcanzó. No se atribuye este resultado a una cuota específica de peticiones por minuto o por día.

## Fuentes

- [Material oficial de rate limits de Gemini](https://ai.google.dev/gemini-api/docs/rate-limits).
- [Referencia oficial de generación de contenido y configuración](https://ai.google.dev/api/generate-content).
- Material respaldado del curso, bloque 13: «Provocamos un rate limit a propósito, para aprender a manejarlo» y checklist de cierre.

## Validación automática

La suite incluye tres pruebas del script: 429 con agotamiento, recuperación y detención tras el 429, y ejecución que no encuentra un 429. Estas pruebas usan transporte y tiempo simulados; son independientes de la evidencia real anterior.

```bash
python -m pytest -v
python -m pip check
```

Resultado: 38 pruebas aprobadas y dependencias sin conflictos.
