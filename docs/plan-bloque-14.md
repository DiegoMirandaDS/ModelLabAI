# Orientación del producto y plan de entrega — Bloque 14

Fecha: 29 de octubre de 2026.
Estado: plan implementado localmente; validación y evidencia en `entrega-bloque-14.md`. El envío a Skillnest se registra por separado.

## Intención del proyecto

ModelLab AI evolucionará hacia una aplicación que recibe datos tabulares, identifica sus características y problemas de calidad, y recomienda un proceso de ETL y una estrategia de modelado predictivo con ayuda de Gemini.

El usuario aporta los datos, explica qué quiere predecir y confirma la variable objetivo y el significado de sus clases. El sistema mide el perfil de los datos localmente y consulta a Gemini para obtener recomendaciones justificadas. Las estadísticas se calculan mediante código; el modelo generativo interpreta ese perfil, identifica incertidumbres y propone un plan. No se deben presentar recomendaciones como transformaciones ejecutadas ni resultados de entrenamiento que no se hayan medido.

La primera versión se limitará a clasificación binaria sobre una tabla. La visión posterior incluye Excel y conexiones a bases de datos, tratamiento de columnas, ejecución controlada de transformaciones y entrenamiento integrado. En este documento, modelado significa modelado predictivo; el diseño de esquemas de bases de datos queda fuera del alcance inicial.

## Diagnóstico inicial antes de implementar

Inspección del repositorio `/home/diego/modellab-ai`:

- Existe un cliente REST en `src/consumir_gemini.py`, construcción de peticiones, extracción de texto y validación básica de respuestas JSON.
- Existe cálculo estimado de costo por tokens de entrada, salida y razonamiento.
- Hay un punto de entrada de consola, un banco de prompts y registros históricos de evaluaciones.
- El README presenta el proyecto como un asistente educativo de Machine Learning; todavía no expresa la visión de ETL y clasificación binaria.
- `enviar_peticion` convierte actualmente los errores HTTP y de red en `RuntimeError`, sin la distinción pedida por el curso.
- No existen las funciones `con_reintento`, `registrar_costo` ni `consultar_modelo` del checklist.
- `requirements.txt` no declara pytest.
- Las seis pruebas existentes pasan con `python -m unittest discover -s tests -v`. Esto verifica el estado anterior; no acredita la actividad core del bloque 14.

## Requisito académico confirmado

Fuente local: `E:/Proyectos/SKILLNESTIA/Respaldo-bloques-13-14/index.html`, secciones r3, r4 y r5. El último respaldo incluye los bloques 13 y 14. La actividad core se titula «Escribe tus pruebas unitarias y verifica que pasen» y cierra la Unidad 2.1.

Se exige una suite con pytest, mocks de API y esperas, nombres descriptivos y cobertura de cada escenario del checklist. Las cuatro funciones evaluadas son `enviar_peticion`, `con_reintento`, `registrar_costo` y `consultar_modelo`.

| Función | Comportamientos que se deben implementar y verificar |
|---|---|
| `enviar_peticion` | HTTP 401 y 403 → `ValueError`; HTTP 429 y 5xx → `TimeoutError`; éxito → JSON recibido sin alteraciones. |
| `con_reintento` | Reintenta ante `TimeoutError`; puede recuperarse; no reintenta otras excepciones; al agotarse propaga la excepción original. Las esperas se simulan en las pruebas. |
| `registrar_costo` | Calcula un costo a partir de uso conocido y lo acumula en `costo_total_sesion`; cada prueba comienza con el estado aislado. |
| `consultar_modelo` | Convierte el `TimeoutError` agotado en `RuntimeError`; propaga `ValueError` sin cambios. |

El ejemplo del curso muestra siete pruebas, pero la instrucción pide cubrir todos los escenarios: el número siete no sustituye la matriz de cobertura.

El curso muestra `cliente.py` y `test_cliente.py` juntos en la raíz. El repositorio ya usa `src/` y `tests/`, que pueden funcionar ejecutando `python -m pytest` desde la raíz. Propuesta: conservar esta estructura y documentar las equivalencias y el comando. Si la evaluación automatizada exige esos nombres o rutas literales, adaptar la entrega; ese detalle no está confirmado en el respaldo.

La actividad indica commit y push al repositorio. El formulario de entrega está solo en la plataforma original; sus campos y cualquier requisito adicional deben revisarse allí al cerrar la entrega. El bloque 14 es la primera entrega de Gate 2. Gate 2 continúa con más bloques y entregas; este trabajo no lo cierra.

## Alcance concreto para bloque 14

### 1. Documentar el producto

- Actualizar la presentación del README con la visión, el alcance actual y el MVP de clasificación binaria.
- Mantener este documento como guía de implementación y entrega.
- Añadir una decisión de arquitectura sobre la separación entre perfilado local y recomendación generativa, sin reescribir las decisiones históricas.
- Documentar qué se envía a Gemini: inicialmente un perfil sintético; posteriormente metadatos y estadísticas revisados, excluyendo por defecto filas originales y valores sensibles. Los nombres de columnas también pueden revelar información y deben revisarse.

### 2. Completar la base técnica exigida por bloques 12–14

- Mantener `src/consumir_gemini.py` como única implementación del cliente durante esta entrega.
- Clasificar errores recuperables y definitivos según el checklist. Traducir también el timeout de transporte a `TimeoutError`; mantener el diagnóstico de otros errores.
- Añadir reintentos con backoff exponencial, jitter y espera acotada. No reintentar credenciales inválidas ni dormir después del último intento.
- Añadir el registro de costo por operación y acumulado de sesión. Conservar `calcular_costo` y sus unidades explícitas; el valor de referencia por total de tokens del curso debe distinguirse de la estimación desglosada usada por el proyecto. Si se conserva ese modo académico, etiquetarlo como referencial y probarlo con `totalTokenCount`, sin presentarlo como facturación real.
- Añadir `consultar_modelo` como coordinador de petición, reintentos, registro y extracción; conservar la opción de instrucciones de sistema y esquema JSON.
- Revisar los consumidores existentes (`main`, benchmark y evaluación de prompts) ante el cambio de excepciones para mantener su manejo de errores.

### 3. Dar identidad al caso de demostración

Crear un ejemplo separado con un perfil tabular sintético y una variable objetivo binaria confirmada. Propuesta de caso: abandono de clientes; clase positiva = cliente que abandona.

Entrada: cantidad de filas, columnas, tipos observados, porcentaje de nulos, cardinalidad, duplicados, distribución de la variable objetivo y contexto temporal. Todos los datos del ejemplo deben estar identificados como sintéticos.

Salida JSON propuesta: resumen, tratamientos sugeridos por columna y su justificación, riesgos, plan de partición y validación, modelos candidatos, métricas recomendadas y preguntas pendientes.

El caso debe mostrar que un ID no es automáticamente una variable predictora, que dos valores distintos no bastan para establecer el significado del objetivo y que la elección de partición depende del tiempo y de posibles grupos. Si falta información, debe pedirla.

Para este bloque basta con construir la petición del ejemplo y verificar su integración con respuestas simuladas. Una llamada real puede aportar evidencia adicional si se ejecuta expresamente; no forma parte de las pruebas unitarias ni demuestra por sí sola la calidad de la recomendación.

No implementar todavía lectura de Excel, conectores de base de datos, ejecución de ETL, entrenamiento automático o interfaz web. Son etapas posteriores, no requisitos de esta actividad core.

### 4. Completar y ejecutar las pruebas

- Conservar las pruebas anteriores y adaptarlas solo donde cambie el contrato de errores.
- Añadir `tests/test_cliente.py` con la matriz completa, usando pytest y `unittest.mock`.
- Verificar el número de intentos y llamadas, la recuperación, el agotamiento y la ausencia de reintentos ante errores definitivos.
- Aislar el acumulador de costos mediante fixture; comprobar cálculo y acumulación en más de una operación.
- Simular red y `sleep`; usar credenciales ficticias. La suite debe poder ejecutarse sin una clave real ni conectarse a Gemini.
- Declarar pytest y configurar su descubrimiento en `tests/`. El archivo `src/prompts/test_consistencia.py` realiza evaluaciones con la API y no debe entrar en la suite unitaria automática.
- Comando objetivo: `python -m pytest tests -v` desde la raíz, con todas las pruebas aprobadas.

### 5. Preparar evidencia y entrega

Crear `docs/entrega-bloque-14.md` con la relación requisito → función → prueba, comandos reproducibles, resultado real de ejecución y explicación del vínculo con el producto final. Guardar salida de pytest sin secretos y revisar el diff antes de preparar commit/push y completar el formulario.

La entrega estará lista cuando los cuatro contratos estén implementados, la suite completa pase sin API real ni esperas reales, las dependencias sean reproducibles, el README distinga capacidades actuales y futuras y la evidencia corresponda al código entregado.

## Organización propuesta

Cambios pequeños para bloque 14; conservar los módulos e históricos existentes:

```text
src/
  consumir_gemini.py         # Cliente compartido y contratos del curso
  main.py                    # Entrada actual; integrar el coordinador
  ejemplos/
    recomendar_etl.py         # Demostración orientada al producto
  prompts/
    banco.py                 # Mantener prompts y evidencia anteriores
    etl_binario.py            # Nuevo prompt y esquema, separados
    ...                      # Históricos existentes intactos
 tests/
  test_consumir_gemini.py
  test_main.py
  test_cliente.py             # Cobertura del checklist
 docs/
  plan-bloque-14.md
  entrega-bloque-14.md        # Crear con evidencia real al implementar
  ...                       # Documentación histórica
```

Los archivos nuevos indicados se incorporaron para esta entrega; consultar la evidencia de ejecución. No mover ahora todos los módulos ni crear capas sin uso. Incorporar `ingesta/`, `perfilado/`, `etl/` y `modelado/` cuando se implementen sus responsabilidades.

## Qué se conserva

- Nombre ModelLab AI y repositorio actual.
- Python, REST, Requests y configuración por entorno.
- Instrucciones de sistema y salida JSON estructurada.
- Banco de prompts anterior como evidencia y posible apoyo a interpretación de métricas.
- Benchmarks, registros y documentos históricos con su contexto y fechas.
- Separación actual `src/`, `tests/` y `docs/`, salvo exigencia literal de la evaluación.

No cambiar ahora de proveedor, incorporar agentes/RAG ni desarrollar frontend: no resuelven el requisito inmediato. No reutilizar tarifas o nombres de modelos históricos como datos actuales verificados; confirmar disponibilidad y precios cuando se prepare una nueva ejecución real.

## Continuidad de Gate 2

El bloque 14 es la primera entrega de Gate 2 y el único bloque de entrega abordado ahora. El objetivo es completar el trabajo acumulado necesario para esta actividad, con el proyecto ya orientado hacia ETL y modelado.

Para la entrega del bloque 15 se extraerá su material y sus subbloques, se verificará su actividad core y se ajustará el siguiente incremento. Se repetirá ese procedimiento para las siguientes entregas hasta completar Gate 2. No se adelanta ahora un cronograma de funcionalidades para Gate 3.

La dirección del producto queda documentada en `intencion-proyecto.md`. Las capacidades futuras se incorporarán gradualmente según el material confirmado del curso y las necesidades del proyecto.
