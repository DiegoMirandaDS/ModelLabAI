# Intención del proyecto y decisión de arquitectura

Fecha: 29 de octubre de 2026.

## Producto que queremos construir

ModelLab AI asistirá a una persona que tiene datos tabulares y quiere prepararlos para construir un modelo predictivo. A futuro podrá recibir Excel o consultar una base de datos, reconocer columnas, medir problemas de calidad y recomendar un proceso de ETL y una estrategia de modelado mediante Gemini.

El primer alcance previsto es una tabla y clasificación binaria. El usuario debe confirmar el objetivo de negocio, la columna objetivo, la clase positiva y el contexto de uso. El significado de una columna no puede deducirse con certeza solo de su nombre o de sus valores.

## Decisión: cálculo local y recomendación generativa

1. El código de ingesta y perfilado calculará tipos observados, nulos, duplicados, cardinalidad y distribución del objetivo.
2. Gemini recibirá un perfil revisado y devolverá recomendaciones estructuradas, evidencia usada y preguntas pendientes.
3. El usuario revisará el plan. Su ejecución futura usará transformaciones permitidas y verificables, no código arbitrario generado por el modelo.
4. El entrenamiento y las métricas serán calculados por librerías de Machine Learning. Gemini ayudará a interpretar resultados medidos.

Antes de ajustar imputación, codificación o escalado se definirá la partición adecuada. Si hay tiempo o grupos, se considerarán explícitamente para evitar fuga de información.

El perfil enviado deberá excluir por defecto filas originales y valores sensibles; también se revisarán nombres de columnas y estadísticas que puedan revelar información. En esta entrega se usa únicamente un perfil sintético escrito a mano.

## Qué aporta el bloque 14

Esta es la **primera entrega de Gate 2**. Completa el cliente modular y sus pruebas unitarias, y añade una demostración del contrato de recomendación sobre un perfil sintético. No completa Gate 2.

El ejemplo provisional de abandono de clientes permite mostrar una dirección de producto sin comprometer el caso final. El alcance implementado no incluye carga de Excel, bases de datos, perfilado real, ETL ejecutable ni entrenamiento.

## Continuidad del curso

Cuando corresponda la entrega del bloque 15, se extraerán sus subbloques y se revisarán sus requisitos. El mismo procedimiento continuará en las siguientes entregas de Gate 2. La visión del producto orientará los ejemplos y decisiones, mientras que el alcance de cada entrega se ajustará a su material confirmado.

No se asignan ahora funcionalidades del producto a futuros bloques o gates cuya rúbrica todavía no se ha revisado. Se conservan el cliente, banco de prompts y registros anteriores como base acumulativa del proyecto.
