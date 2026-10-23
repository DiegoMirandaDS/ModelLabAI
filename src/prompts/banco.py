
"""Banco de prompts de ModelLab AI."""

BANCO_DE_PROMPTS = [
    {
        "nombre": "diagnosticar_sobreajuste",

        "system_instruction": (
            "Eres un analista de Machine Learning. "
            "Evalúa las métricas entregadas por el usuario para "
            "identificar señales de sobreajuste o problemas de "
            "generalización. No inventes información. "
            "Si las métricas son insuficientes, indícalo. "
            "Devuelve solo el JSON solicitado. "
            "La confianza debe ser un número entre 0 y 1."
        ),

        "ejemplo_usuario": (
            "Un clasificador obtuvo accuracy de 0.98 en "
            "entrenamiento y 0.71 en validación. "
            "¿Qué problema podría estar ocurriendo?"
        ),

        "response_schema": {
            "type": "OBJECT",
            "properties": {
                "diagnostico": {"type": "STRING"},
                "confianza": {"type": "NUMBER"},
                "explicacion": {"type": "STRING"}
            },
            "required": [
                "diagnostico",
                "confianza",
                "explicacion"
            ]
        }
    },

    {
        "nombre": "recomendar_mejoras",

        "system_instruction": (
            "Eres un especialista en optimización de modelos "
            "de Machine Learning. Analiza el problema presentado "
            "y propone recomendaciones técnicamente justificadas. "
            "No inventes resultados experimentales. "
            "La prioridad debe ser alta, media o baja. "
            "Devuelve únicamente el JSON solicitado."
        ),

        "ejemplo_usuario": (
            "Tengo un Random Forest con excelente rendimiento "
            "en entrenamiento, pero su F1-score disminuye "
            "considerablemente sobre datos nuevos. "
            "¿Qué debería revisar?"
        ),

        "response_schema": {
            "type": "OBJECT",
            "properties": {
                "problema": {"type": "STRING"},
                "recomendaciones": {
                    "type": "ARRAY",
                    "items": {"type": "STRING"}
                },
                "prioridad": {"type": "STRING"}
            },
            "required": [
                "problema",
                "recomendaciones",
                "prioridad"
            ]
        }
    },

    {
        "nombre": "interpretar_metricas",

        "system_instruction": (
            "Eres un asistente educativo especializado en "
            "evaluación de modelos de Machine Learning. "
            "Interpreta las métricas proporcionadas, "
            "explica qué significan y advierte sobre "
            "sus limitaciones. No inventes métricas "
            "ni resultados. Responde exclusivamente en JSON."
        ),

        "ejemplo_usuario": (
            "Un modelo de detección de fraude tiene "
            "precision de 0.92 y recall de 0.58. "
            "¿Cómo debo interpretar estos resultados?"
        ),

        "response_schema": {
            "type": "OBJECT",
            "properties": {
                "metrica": {"type": "STRING"},
                "interpretacion": {"type": "STRING"},
                "advertencia": {"type": "STRING"}
            },
            "required": [
                "metrica",
                "interpretacion",
                "advertencia"
            ]
        }
    }
]
