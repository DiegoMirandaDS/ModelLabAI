# ModelLab AI

ModelLab AI es un proyecto de la Especialización en Desarrollo con IA Generativa de Skillnest. Su dirección de producto es recibir datos tabulares, analizar sus características y recomendar un proceso de ETL y una estrategia de modelado predictivo con ayuda de Gemini.

El primer alcance previsto es **clasificación binaria sobre una tabla**. Python calculará el perfil de los datos, ejecutará las transformaciones y medirá los modelos; Gemini ayudará a interpretar ese perfil y proponer decisiones justificadas.

## Estado actual — primera entrega de Gate 2, bloque 14

Esta entrega corresponde a la actividad core «Escribe tus pruebas unitarias y verifica que pasen». Gate 2 continúa con más bloques y entregas. Sus requisitos se revisarán a partir del material de cada bloque, comenzando por el 15 cuando corresponda.

Implementado:

- Cliente REST de Gemini con instrucciones de sistema y salida JSON estructurada.
- Clasificación de errores HTTP: 401/403 definitivos; 429/5xx temporales.
- Reintentos con backoff exponencial, jitter, límite de espera y de intentos.
- Registro estimado de costo por operación y acumulado de sesión.
- Suite de pruebas con pytest, red y esperas simuladas.
- Ejemplo de recomendación de ETL y clasificación binaria sobre un perfil sintético.
- Banco histórico de prompts, evaluación de consistencia y benchmark experimental.

Pendiente para incrementos posteriores: lectura de Excel/CSV, conexión a bases de datos, perfilado de datos reales, ejecución de ETL, entrenamiento de clasificadores e interfaz integrada. El ejemplo actual no implementa esas capacidades.

## Instalación

Entorno utilizado: Python 3.12 en WSL2 / Ubuntu.

```bash
git clone https://github.com/DiegoMirandaDS/ModelLabAI.git
cd ModelLabAI
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## Pruebas unitarias — bloque 14

Desde la raíz del repositorio:

```bash
python -m pytest -v
```

Solo el checklist del cliente:

```bash
python -m pytest tests/test_cliente.py -v
```

`pytest.ini` limita el descubrimiento a `tests/`. Las pruebas usan credenciales ficticias y mocks: no necesitan una clave real, no consumen tokens y no esperan el backoff real. La evaluación histórica `src/prompts/test_consistencia.py` se ejecuta por separado porque sí consulta la API.

La organización `src/` y `tests/` conserva el proyecto existente. El módulo equivalente al `cliente.py` del curso es `src/consumir_gemini.py`; su checklist está en `tests/test_cliente.py`. Ejecutar siempre desde la raíz con `python -m pytest`.

## Ejemplo orientado al producto

Vista previa local, sin API ni credenciales:

```bash
python -m src.ejemplos.recomendar_etl
```

Muestra un perfil sintético de abandono de clientes, instrucciones y esquema de respuesta. La clase positiva del ejemplo está definida explícitamente. El ejemplo es provisional: no fija el dominio final del producto.

Para consultar realmente a Gemini, configurar primero el entorno y ejecutar:

```bash
python -m src.ejemplos.recomendar_etl --consultar
```

La respuesta se valida contra un esquema JSON y contiene tratamientos sugeridos, riesgos, validación, modelos candidatos, métricas y preguntas pendientes. Estas recomendaciones no ejecutan transformaciones ni entrenan modelos. Las pruebas verifican el contrato con respuestas simuladas; no acreditan calidad semántica de respuestas reales.

## Configuración de llamadas reales

```bash
cp .env.example .env
```

Editar `.env` con una clave personal válida y un modelo disponible en la cuenta:

```dotenv
GEMINI_API_KEY=TU_CLAVE
GEMINI_MODEL=IDENTIFICADOR_DE_MODELO_DISPONIBLE
```

Los identificadores y precios presentes en evidencia histórica no son una verificación de disponibilidad o tarifas actuales. Nunca subir `.env` ni compartir la clave privada.

La entrada histórica sigue disponible y realiza una consulta real:

```bash
python -m src.main
```

## Contratos del cliente

- `enviar_peticion`: recibe URL, encabezados y cuerpo; devuelve el JSON sin alterarlo. HTTP 401/403 produce `ValueError`, HTTP 429/5xx o timeout de transporte produce `TimeoutError`. Otros errores HTTP, conexión y JSON inválido conservan un diagnóstico en `RuntimeError`.
- `con_reintento`: reintenta solo `TimeoutError`. `intentos` incluye la primera llamada. No espera después del último fallo y propaga la última excepción original.
- `registrar_costo`: devuelve el costo de la operación y lo suma a `costo_total_sesion`. Sin precios usa `totalTokenCount` y la tarifa didáctica `COSTO_POR_1000_TOKENS = 0.002 USD`. Con ambos precios por token usa el cálculo desglosado de entrada, salida y razonamiento.
- `consultar_modelo`: coordina petición, reintentos, registro y extracción. Convierte el timeout agotado en `RuntimeError` y propaga `ValueError`. Acepta instrucciones de sistema y esquema de respuesta.

Los costos son estimaciones, no cargos comprobados. La tarifa didáctica no representa precios de Gemini. `src/main.py` conserva los valores históricos del proyecto, etiquetados como tales. El acumulador es local al proceso y cuenta únicamente respuestas con consumo reportado: no estima operaciones fallidas ni consumo ausente. `registrar_costo` directo exige los metadatos necesarios; el coordinador puede entregar texto sin ellos sin inventar un costo. Es una solución para la consola de este bloque; el aislamiento de sesiones concurrentes queda para una futura aplicación multiusuario.

## Ensayo de rate limit — bloque 13

Se realizó un ensayo real con el cliente actualizado: el primer 429 apareció en la petición HTTP 7 y la operación se recuperó tras una espera de 2.002 segundos. Hubo siete operaciones exitosas, ocho peticiones HTTP y 813 tokens reportados. El [informe del ensayo](docs/ensayo-bloque-13.md) incluye la evidencia y el costo referencial.

Para repetirlo con la configuración del entorno (realiza llamadas reales y consume cuota):

```bash
python -m src.ensayo_rate_limit --ejecutar
```

Máximo diez operaciones, tres intentos por operación y 128 tokens de salida por petición; se detiene tras la primera operación que recibe un 429. La ejecución sin `--ejecutar` muestra únicamente la ayuda.

## Banco histórico de prompts

Se conservan los prompts de diagnóstico de sobreajuste, recomendaciones de mejora e interpretación de métricas. Podrán apoyar etapas futuras de evaluación de modelos.

```bash
python -m src.prompts.test_consistencia
```

Este comando **realiza llamadas reales**. Busca al menos tres respuestas estructuralmente válidas por prompt, modelo y versión, con un máximo de tres intentos adicionales por prompt pendiente en cada ejecución. Conserva solicitudes exitosas y fallidas en `src/prompts/registro_intentos.jsonl` y regenera `src/prompts/registro_resultados.json`. Su historial anterior no se reescribe para esta entrega.

## Documentación

- [Intención del producto y separación de responsabilidades](docs/intencion-proyecto.md).
- [Validación técnica del bloque 14](docs/entrega-bloque-14.md).
- [Decisión histórica de arquitectura](docs/decision-arquitectura.md).
- [Comparación histórica de modelos](docs/comparacion_modelos.md).
- Diagramas históricos: `docs/diagrama_arquitectura.png`, `docs/diagrama_arquitectura.svg` y `docs/arquitectura.dot`. Representan el estado previo; la dirección actual se describe en los documentos anteriores.

## Autor

Diego Miranda
