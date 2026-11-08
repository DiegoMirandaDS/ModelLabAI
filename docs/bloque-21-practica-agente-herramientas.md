# Agente con herramientas — práctica del bloque 21

La [actividad](https://learning-pro.skillnest.com/mod/page/view.php?id=15703) se implementa en `src/agente.py` con `create_tool_calling_agent` y `AgentExecutor` de `langchain-classic`, cuatro iteraciones máximas y `return_intermediate_steps=True`.

| Herramienta | Responsabilidad |
|---|---|
| `consultar_perfil_dataset` | Lee columnas, nulos, duplicados y rangos; excluye el resumen de balance |
| `calcular_balance_objetivo` | Calcula conteos y porcentajes de `Churn` |

Las descripciones indican cuándo usar cada herramienta. Ambas leen el CSV local de [Iranian Churn](datos-prueba-iranian-churn.md), devuelven texto JSON y admiten solo el dataset registrado. Sus errores producen una observación legible y no aceptan rutas arbitrarias.

## Verificación

Los registros `agente_perfil` y `agente_balance` de las [trazas reales](evidencias/orquestacion_agente.json) confirman la elección de cada herramienta por separado. `agente_general` responde qué significa ETL sin herramientas. Se guardan nombre, argumentos y observación; no se publica razonamiento interno.

`tests/test_agente.py` verifica datos devueltos, entradas no permitidas, el ciclo del agente y la lectura de respuestas en texto o bloques de contenido.

```bash
python -m src.demo --modo agente --mensaje "Calcula el balance de Churn en iranian_churn" --consultar
```

El comando consulta Gemini y consume cuota. Las trazas acreditan la selección y los resultados observados, no la calidad general de cualquier respuesta. [Referencia del agente con herramientas](https://reference.langchain.com/python/langchain-classic/agents/tool_calling_agent/base/create_tool_calling_agent).
