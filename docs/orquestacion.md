# Orquestación y herramientas

## Chain de tres pasos — bloque 18

`src/orquestacion.py` conecta tres `PromptTemplate` mediante LCEL (`|`) y `StrOutputParser`:

1. **Diagnóstico:** identifica problemas y riesgos a partir del perfil local.
2. **Preparación:** usa el diagnóstico para justificar tratamientos.
3. **Estrategia:** usa ambos resultados para proponer partición, baseline y métricas.

El perfil original acompaña a los tres pasos para evitar que una interpretación intermedia sustituya la evidencia. El modelo se inyecta en `construir_cadena`: las pruebas comprueban tres llamadas y la transferencia de información sin usar red. Una respuesta truncada se rechaza antes del siguiente paso.

## Rutas y errores — bloques 19–20

La clasificación se normaliza con `strip().lower()`. `RunnablePassthrough.assign` conserva la entrada y agrega la categoría. `RunnableBranch` selecciona preparación, modelado o la ruta predeterminada de aclaración. Las dos primeras reutilizan la chain de tres pasos con enfoques distintos; la última usa su propio prompt. Una categoría desconocida también conduce a aclaración.

Cada destino usa `with_fallbacks`: si falla, devuelve una orientación para revisar el perfil local y registra la clase del error. `procesar_seguro` captura fallos anteriores a las rutas, incluida la clasificación. Las respuestas de recuperación están identificadas con `estado`; no se presentan como recomendaciones generadas correctamente. Los registros no incluyen claves ni cuerpos HTTP.

## Agente — bloque 21

`src/agente.py` usa `create_tool_calling_agent` y `AgentExecutor` de `langchain-classic`, con cuatro iteraciones máximas y `return_intermediate_steps=True`.

| Herramienta | Responsabilidad |
|---|---|
| `consultar_perfil_dataset` | Lee columnas, nulos, duplicados y rangos; excluye el resumen de balance |
| `calcular_balance_objetivo` | Calcula conteos y porcentajes de `Churn` |

Ambas leen el CSV local, devuelven texto JSON y aceptan solo el dataset registrado. No admiten rutas arbitrarias. Sus descripciones separan los usos y sus errores producen una observación legible. La evidencia conserva nombre, argumentos y observación de cada herramienta, sin publicar razonamiento interno.

Las corridas reales verifican la conexión entre pasos, la ruta elegida y el uso de herramientas. No certifican por sí solas la calidad de toda recomendación; las salidas generativas conservan los límites descritos en la evaluación.

## Ejecución

Desde la raíz del repositorio, con el entorno activado:

```bash
python -m src.demo --modo perfil
python -m src.demo --modo cadena --consultar
python -m src.demo --modo enrutamiento --mensaje "Revisa la calidad antes del ETL" --consultar
python -m src.demo --modo agente --mensaje "Calcula el balance de Churn en iranian_churn" --consultar
```

`--consultar` realiza llamadas reales. La suite usa modelos simulados. El cliente REST existente se utiliza en los bloques 15–17; LangChain emplea su integración Gemini y registra los tokens reportados por separado, sin atribuirle la tarifa didáctica del cliente REST.

Referencias: [integración Gemini](https://docs.langchain.com/oss/python/integrations/chat/google_generative_ai), [agente con herramientas](https://reference.langchain.com/python/langchain-classic/agents/tool_calling_agent/base/create_tool_calling_agent).
