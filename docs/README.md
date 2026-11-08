# Documentación de ModelLab AI

## Producto y datos de prueba

- [Alcance y responsabilidades](intencion-proyecto.md): funciones implementadas y separación entre Python, Gemini y LangChain.
- [Iranian Churn: datos reales de prueba](datos-prueba-iranian-churn.md): origen, controles de calidad y decisiones de uso para la demostración de los bloques 15–21.

## Actividades del curso

| Bloque y actividad | Documento | Contenido |
|---|---|---|
| 13 · Ensayo de rate limit | [Ensayo real](ensayo-bloque-13.md) | HTTP 429, reintentos, esperas y consumo |
| 14 · Core | [Pruebas del cliente](entrega-bloque-14.md) | Requisitos y resultados de la entrega original |
| 15 · Práctica / 16 · Métricas | [Evaluación de texto](bloques-15-16-evaluacion-texto.md) | Limpieza, comparación antes/después y métricas sobre respuestas reales |
| 17 · Core | [Límites de la métrica](bloque-17-core-limites-metrica.md) | Revisión cualitativa de 10 casos entre 20 respuestas |
| 18 · Práctica | [Chain de tres pasos](bloque-18-practica-chain-tres-pasos.md) | Diagnóstico, preparación y estrategia |
| 19 · Enrutamiento | [Rutas según intención](bloque-19-enrutamiento-condicional.md) | Preparación, modelado y aclaración |
| 20 · Core | [Verificación y errores](bloque-20-core-verificacion-orquestacion.md) | Fallbacks, protección general y pruebas |
| 21 · Práctica | [Agente con herramientas](bloque-21-practica-agente-herramientas.md) | Consulta de perfil, balance del objetivo y trazas |

## Evidencias e integración inicial

[Índice de evidencias](evidencias/README.md): identifica el bloque, el dataset y el contenido de cada registro.

La integración inicial y las decisiones de octubre de 2026 se conservan como antecedentes: [petición HTTP exitosa](evidencia_api.md), [selección de Gemini](decision-arquitectura.md) y [benchmark de modelos](comparacion_modelos.md). Los diagramas históricos acompañan a la decisión de arquitectura.
