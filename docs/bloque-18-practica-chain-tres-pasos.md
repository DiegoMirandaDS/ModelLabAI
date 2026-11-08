# Chain de tres pasos — práctica del bloque 18

La [actividad](https://learning-pro.skillnest.com/mod/page/view.php?id=15655) se implementa en `src/orquestacion.py` con tres `PromptTemplate`, el operador LCEL `|` y `StrOutputParser`:

1. **Diagnóstico:** identifica problemas y riesgos del perfil local.
2. **Preparación:** usa el diagnóstico para justificar tratamientos.
3. **Estrategia:** usa ambos resultados para proponer partición, baseline y métricas.

El perfil original acompaña a los tres pasos. El modelo se inyecta en `construir_cadena`; la prueba `test_tres_pasos_consumen_salida_anterior_y_preservan_perfil` verifica tres llamadas y el paso de información entre ellas. Una respuesta truncada se rechaza antes del siguiente paso.

```bash
python -m src.demo --modo cadena --consultar
```

Realiza llamadas a Gemini. La corrida completa sobre [Iranian Churn](datos-prueba-iranian-churn.md) está en el registro `cadena` de las [evidencias de orquestación](evidencias/orquestacion_agente.json). Conserva las tres salidas y los tokens reportados, sin inventar precios.

La chain produce recomendaciones; no ejecuta transformaciones ni entrenamientos. [Referencia de la integración Gemini](https://docs.langchain.com/oss/python/integrations/chat/google_generative_ai).
