# ModelLab AI: alcance y responsabilidades

ModelLab AI ayuda a interpretar un perfil tabular y proponer preparación de datos y validación para clasificación binaria. La demostración usa el CSV público Iranian Churn, cuyo objetivo y clase positiva están documentados.

## Responsabilidades

- **Python:** carga el CSV, calcula el perfil, detecta anomalías y obtiene el balance del objetivo. Conserva el archivo original.
- **Gemini:** interpreta el perfil, justifica recomendaciones y distingue evidencia de supuestos.
- **LangChain:** conecta diagnóstico, preparación y estrategia; enruta solicitudes y recupera fallos por paso.
- **Agente:** selecciona entre consultar el perfil y calcular el balance; registra las herramientas utilizadas.

Solo se envían estadísticas agregadas del dataset de demostración. Las herramientas aceptan un identificador registrado y no rutas arbitrarias. Las salidas generativas son recomendaciones: no ejecutan transformaciones ni acreditan modelos entrenados.

## Evaluación

Los bloques 15–17 miden coincidencia léxica de respuestas reales y la contrastan con una revisión cualitativa. Los bloques 18–20 verifican dependencias entre pasos, rutas y recuperación ante fallos. El bloque 21 verifica la selección de dos herramientas y una consulta general sin herramientas.

La evaluación predictiva es distinta: un F1 de texto no mide capacidad para predecir abandono. El [dataset](datos-prueba-iranian-churn.md) y los [límites de la métrica](bloque-17-core-limites-metrica.md) explican esta separación.
