# Entrega de la actividad core — Bloque 14

Fecha de preparación: 29 de octubre de 2026.
Curso: Especialización en Desarrollo con IA Generativa, Skillnest.
Proyecto: ModelLab AI.
Etapa: **primera entrega de Gate 2**. Gate 2 continúa después de este bloque.

## Actividad y alcance

Actividad: «Escribe tus pruebas unitarias y verifica que pasen».
Fuente: [actividad core del bloque 14](https://learning-pro.skillnest.com/mod/page/view.php?id=15643) y respaldo local `E:/Proyectos/SKILLNESTIA/Respaldo-bloques-13-14/index.html`, secciones r3–r5.

Se completó el cliente modular y se probó con pytest y mocks de red y tiempo. Se conserva la estructura `src/` y `tests/`: el equivalente al `cliente.py` de los ejemplos del curso es `src/consumir_gemini.py`, y el checklist está en `tests/test_cliente.py`.

## Matriz de requisitos y pruebas

Todas las pruebas siguientes están en `tests/test_cliente.py`:

| Requisito | Prueba |
|---|---|
| HTTP 401/403 → ValueError | `test_enviar_peticion_credencial_invalida` (parametrizada) |
| HTTP 429/500/503 → TimeoutError | `test_enviar_peticion_error_temporal` (parametrizada) |
| Éxito devuelve el JSON sin alterarlo | `test_enviar_peticion_exito_devuelve_json_sin_alterar` |
| Timeout de transporte normalizado | `test_enviar_peticion_timeout_transporte_es_recuperable` |
| Reintento y recuperación | `test_con_reintento_recupera_y_espera_entre_intentos` |
| Sin reintento ante otras excepciones | `test_con_reintento_no_reintenta_otros_errores` |
| Agotamiento conserva la excepción original y no espera al final | `test_con_reintento_agota_y_propaga_excepcion_original` |
| Tope de espera incluyendo jitter | `test_con_reintento_respeta_tope_con_jitter` |
| Costo correcto desde totalTokenCount | `test_registrar_costo_calcula_desde_total_tokens` |
| Acumulación entre operaciones | `test_registrar_costo_acumula_dos_operaciones` |
| Costo con precios por entrada/salida y razonamiento | `test_registrar_costo_desglosado_incluye_razonamiento` |
| Timeout agotado → RuntimeError | `test_consultar_modelo_convierte_timeout_agotado` |
| ValueError se propaga sin cambios | `test_consultar_modelo_propaga_value_error_sin_cambios` |
| Consulta recuperada registra el éxito una sola vez | `test_consultar_modelo_recupera_y_registra_exito_una_sola_vez` |

Un fixture aísla las credenciales ficticias y el acumulador por prueba. Las pruebas del checklist bloquean cualquier intento de red o espera que no esté expresamente simulado. El jitter se comprueba mediante rangos y un límite, sin comparar un valor aleatorio exacto.

Se mantienen las seis pruebas anteriores (adaptando la entrada de consola al coordinador) y se añaden tres pruebas del ejemplo de ETL en `tests/test_ejemplo_etl.py`. Hay 26 casos del checklist y sus límites, seis de regresión y tres del ejemplo: 35 en total.

## Cómo reproducir

Desde la raíz del repositorio, en Python 3.12:

```bash
python -m pip install -r requirements.txt
python -m pytest -v
python -m pip check
```

Resultado observado:

```text
35 passed in 0.15s
No broken requirements found.
```

Evidencia de la ejecución real de la suite: [salida completa de pytest](evidencias/bloque-14-pytest.txt).

`pytest.ini` limita el descubrimiento a `tests/`, excluyendo la evaluación histórica de consistencia que utiliza la API. No se ejecutó esa evaluación ni una consulta real a Gemini para preparar esta entrega. No se gastaron tokens para estas verificaciones.

## Relación con la intención del producto

ModelLab AI se orienta hacia recibir datos tabulares y recomendar ETL y modelado predictivo, comenzando con clasificación binaria. El cliente probado será la base de la integración con Gemini.

El ejemplo `src/ejemplos/recomendar_etl.py` usa un perfil sintético de abandono de clientes. El prompt pide tratamientos justificados, riesgos, validación, modelos candidatos, métricas y preguntas pendientes. Su integración se verifica con una respuesta simulada; eso acredita el contrato técnico, no la calidad de una recomendación real.

Vista previa local, sin API:

```bash
python -m src.ejemplos.recomendar_etl
```

[Salida de vista previa](evidencias/bloque-14-vista-previa.json).

Excel, bases de datos, perfilado real, ejecución de ETL y entrenamiento siguen pendientes. Su incorporación se decidirá progresivamente al revisar los subbloques de las próximas entregas de Gate 2.

## Costos y alcance de las evidencias

El modo académico usa 0.002 USD por 1000 tokens como tarifa didáctica, no como precio vigente de Gemini. Se conserva la función de cálculo desglosado del proyecto y puede utilizarse proporcionando ambos precios por token.

El acumulador de consola solo registra respuestas que reportan consumo y se reinicia al iniciar un proceso. No representa facturación ni un sistema multiusuario. Las evidencias históricas de API, modelos y benchmarks permanecen intactas y no se presentan como mediciones nuevas.

## Texto preparado para el formulario

> Entrego la actividad core del bloque 14, primera entrega de Gate 2, en el proyecto ModelLab AI. Se completó el cliente modular con clasificación de errores, reintentos con backoff y jitter, registro acumulado de costos estimados y coordinación de consultas a Gemini. La suite cubre los escenarios del checklist usando pytest y mocks de red y tiempo: 35 pruebas aprobadas. El README documenta la orientación del producto hacia recomendación de ETL y modelado para datos tabulares, con clasificación binaria como primer alcance. Se incluye un ejemplo sobre un perfil sintético y evidencia reproducible en docs/entrega-bloque-14.md. Las próximas entregas de Gate 2 se abordarán al revisar el material correspondiente.

Repositorio: [ModelLabAI](https://github.com/DiegoMirandaDS/ModelLabAI).

## Estado del envío a Skillnest

El código y la evidencia están preparados. Al intentar abrir la actividad en el navegador, Skillnest indicó que la sesión había vencido y solicitó iniciar sesión. No se accedió al formulario ni se registró el envío. Se debe retomar ese paso con una sesión activa y verificar la confirmación de recepción antes de considerar la actividad entregada en la plataforma.
