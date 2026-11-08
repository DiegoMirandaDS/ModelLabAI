# ModelLab AI

Asistente de preparación de datos y clasificación binaria, desarrollado en la Especialización en Desarrollo con IA Generativa de Skillnest. Python calcula estadísticas de un CSV real; Gemini las interpreta y recomienda un plan mediante chains y herramientas.

## Alcance implementado — bloques 15–21

- Carga y perfilado del dataset público **Iranian Churn**: 3.150 registros y 14 columnas.
- Evaluación léxica de 20 respuestas reales y revisión cualitativa de 10 casos.
- Chain de diagnóstico → preparación → estrategia de modelado.
- Enrutamiento según la intención, fallbacks y captura general de errores.
- Agente con herramientas de perfilado y balance, con trazas de selección verificadas.
- Pruebas automáticas sin API y evidencias separadas de las corridas reales.

Las recomendaciones no ejecutan ETL ni entrenan modelos. El dataset conserva sus valores originales; las discrepancias se documentan. [Alcance y responsabilidades](docs/intencion-proyecto.md).

## Instalación

Entorno verificado: Python 3.12 en WSL2 / Ubuntu.

```bash
git clone https://github.com/DiegoMirandaDS/ModelLabAI.git
cd ModelLabAI
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m src.demo --modo perfil
```

El CSV de demostración está incluido con [atribución, licencia y huella](data/README.md). `python -m src.datos --descargar` permite recuperarlo de UCI si no está presente y genera el perfil en `docs/evidencias/`.

## Consultas a Gemini

```bash
cp .env.example .env
```

Configurar `GEMINI_API_KEY` y `GEMINI_MODEL` en `.env`. Las evidencias de esta entrega usan `gemini-3.5-flash-lite`. Su disponibilidad y cuota dependen de la cuenta. La clave queda fuera de Git.

```bash
python -m src.demo --modo cadena --consultar
python -m src.demo --modo enrutamiento --mensaje "Revisa la calidad antes del ETL" --consultar
python -m src.demo --modo agente --mensaje "Calcula el balance de Churn en iranian_churn" --consultar
```

Sin `--consultar`, la demostración no llama a Gemini. Las llamadas REST y LangChain registran consumo por separado. La tarifa didáctica histórica del cliente REST no es un precio vigente ni un cargo comprobado.

## Pruebas y evidencias

```bash
python -m pytest -v
```

La suite usa datos locales y modelos simulados: no consume tokens. Comprueba el cliente previo, el CSV original y variantes controladas, las métricas, las dependencias entre pasos, todas las rutas y los fallos simulados.

Para reproducir las verificaciones reales —consumen cuota—:

```bash
python -m src.evaluacion --ejecutar
python -m src.demo --evidencias --consultar
```

Los comandos conservan resultados ya completados para el mismo modelo y entrada. La revisión cualitativa es un registro de la muestra evaluada; no se reemplaza con una puntuación automática.

## Documentación de la entrega

- [Requisitos, implementación y verificación de los bloques 15–21](docs/bloques-15-21.md).
- [Dataset y hallazgos de calidad](docs/dataset.md).
- [Límites de la métrica y revisión de respuestas — core 17](docs/limites_metrica.md).
- [Chains, recuperación y herramientas — core 20 y práctica 21](docs/orquestacion.md).

Se conserva la evidencia previa: [cliente y pruebas del bloque 14](docs/entrega-bloque-14.md), [ensayo de rate limit del bloque 13](docs/ensayo-bloque-13.md) y [comparación histórica de modelos](docs/comparacion_modelos.md). Los diagramas anteriores en `docs/` describen la arquitectura histórica.

## Autor

Diego Miranda
