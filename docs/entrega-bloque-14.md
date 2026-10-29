# Entrega de la actividad core — Bloque 14

Fecha de validación: 29 de octubre de 2026.
Curso: Especialización en Desarrollo con IA Generativa, Skillnest.
Proyecto: ModelLab AI.
Etapa: **primera entrega de Gate 2**.

## Actividad y alcance

Actividad: «Escribe tus pruebas unitarias y verifica que pasen».
Fuente: [actividad core del bloque 14](https://learning-pro.skillnest.com/mod/page/view.php?id=15643).

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

Se mantienen las seis pruebas anteriores (adaptando la entrada de consola al coordinador) y se añaden tres pruebas del ejemplo de ETL en `tests/test_ejemplo_etl.py`. La suite original comprende 26 casos del checklist y sus límites, seis de regresión y tres del ejemplo: 35. Con las tres pruebas del ensayo de rate limit del bloque 13, la suite actual suma 38.

## Cómo reproducir

Desde la raíz del repositorio, en Python 3.12:

```bash
python -m pip install -r requirements.txt
python -m pytest -v
python -m pip check
```

Resultado observado:

```text
38 passed
No broken requirements found.
```

Evidencia de la ejecución real de la suite: [salida completa de pytest](evidencias/bloque-14-pytest.txt).

`pytest.ini` limita el descubrimiento a `tests/`, excluyendo la evaluación histórica de consistencia que utiliza la API. Las pruebas unitarias utilizan respuestas simuladas y no consumen tokens de la API.

## Relación con la intención del producto

ModelLab AI se orienta hacia recibir datos tabulares y recomendar ETL y modelado predictivo, comenzando con clasificación binaria. El cliente probado será la base de la integración con Gemini.

El ejemplo `src/ejemplos/recomendar_etl.py` usa un perfil sintético de abandono de clientes. El prompt pide tratamientos justificados, riesgos, validación, modelos candidatos, métricas y preguntas pendientes. Su integración se verifica con una respuesta simulada; eso acredita el contrato técnico, no la calidad de una recomendación real.

Vista previa local, sin API:

```bash
python -m src.ejemplos.recomendar_etl
```

[Salida de vista previa](evidencias/bloque-14-vista-previa.json).

El alcance validado comprende el cliente modular y el contrato de recomendación sobre un perfil sintético. La ingesta de Excel, las conexiones a bases de datos, el perfilado real, la ejecución de ETL y el entrenamiento pertenecen al alcance futuro del producto.

## Costos y alcance de las evidencias

El modo académico usa 0.002 USD por 1000 tokens como tarifa didáctica, no como precio vigente de Gemini. Se conserva la función de cálculo desglosado del proyecto y puede utilizarse proporcionando ambos precios por token.

El acumulador de consola solo registra respuestas que reportan consumo y se reinicia al iniciar un proceso. No representa facturación ni un sistema multiusuario. Las evidencias históricas de API, modelos y benchmarks permanecen intactas y no se presentan como mediciones nuevas.

## Ensayo previo del bloque 13

El [informe del ensayo real](ensayo-bloque-13.md) documenta el HTTP 429, la espera, la recuperación y los costos reportados del cliente actualizado.
