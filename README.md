
# ModelLab AI

ModelLab AI es un prototipo educativo de inteligencia artificial
generativa orientado a facilitar la comprensión, diagnóstico e
interpretación de modelos de Machine Learning.

Desarrollado durante la Especialización en Desarrollo con IA
Generativa de Skillnest.

## Tecnologías

- Python 3
- Google Gemini API mediante REST
- Requests
- python-dotenv
- Git y GitHub
- Graphviz
- WSL2 / Ubuntu

## Funcionalidades implementadas

- Consumo de la API de Gemini
- Manejo de errores HTTP y de conexión
- Cálculo estimado de costos utilizando tokens
- Comparación experimental de modelos
- Prompts de sistema
- Respuestas JSON estructuradas
- Banco de prompts para Machine Learning
- Pruebas de consistencia

## Instalación

Clonar el repositorio:

```bash
git clone https://github.com/DiegoMirandaDS/ModelLabAI.git
cd ModelLabAI
```

Crear y activar el entorno virtual:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Instalar dependencias:

```bash
python -m pip install -r requirements.txt
```

## Configuración

Crear el archivo de entorno:

```bash
cp .env.example .env
```

Editar `.env` e ingresar una clave personal válida:

```dotenv
GEMINI_API_KEY=TU_CLAVE
GEMINI_MODEL=gemini-3.8-flash
```

Nunca subir `.env` ni compartir la clave privada.

## Ejecutar la aplicación

Desde la raíz del repositorio:

```bash
python -m src.main
```

## Banco de prompts y evaluación de consistencia

ModelLab AI incorpora un banco de tres prompts orientados al análisis de modelos de Machine Learning:

1. **Diagnóstico de sobreajuste:** identifica posibles problemas de generalización.
2. **Recomendaciones de mejora:** propone estrategias para optimizar modelos.
3. **Interpretación de métricas:** explica resultados y sus limitaciones.

Cada prompt dispone de instrucciones de sistema independientes, un ejemplo de entrada y un esquema JSON esperado.

### Ejecutar la evaluación

Desde la raíz del repositorio:

```bash
python -m src.prompts.test_consistencia
```

El sistema utiliza un historial acumulativo en formato JSON Lines (`.jsonl`), registrando cada solicitud individualmente, tanto si es exitosa como si falla.

La evaluación tiene como objetivo obtener **al menos tres respuestas JSON válidas por prompt**, para cada combinación de modelo y versión del prompt.

El programa identifica las pruebas ya completadas y evita repetirlas innecesariamente. Si una prueba queda incompleta por errores de la API, puede continuarse en una ejecución posterior.

Cada ejecución realiza como máximo tres intentos adicionales por prompt pendiente.

### Archivos de resultados

- `src/prompts/registro_intentos.jsonl`: historial acumulativo de solicitudes, respuestas y errores.
- `src/prompts/registro_resultados.json`: resumen regenerado a partir del historial.
- `src/prompts/migrar_registros.py`: herramienta de migración de registros anteriores.

El historial incluye identificadores de intento, fechas, modelo utilizado, versión del prompt, latencia y estado de cada solicitud.

Los errores HTTP se conservan para distinguir fallos de disponibilidad del servicio de problemas de validación JSON.

## Pruebas unitarias

```bash
python -m unittest discover -s tests -v
```

## Documentación

- `docs/diagrama_arquitectura.png`: diagrama de la aplicación
- `docs/diagrama_arquitectura.svg`: versión vectorial
- `docs/arquitectura.dot`: código fuente del diagrama
- `docs/comparacion_modelos.md`: benchmark experimental
- `docs/decision-arquitectura.md`: decisión de modelo

## Seguridad

Las credenciales se administran mediante variables de entorno.
El archivo `.env` se excluye del control de versiones mediante
`.gitignore`.

## Trabajo futuro

- Análisis de métricas de modelos
- Agentes de inteligencia artificial
- RAG
- API con FastAPI
- Interfaz de usuario

## Autor

Diego Miranda
