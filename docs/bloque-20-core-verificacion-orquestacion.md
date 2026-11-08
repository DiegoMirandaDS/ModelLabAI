# Verificación de la orquestación — core del bloque 20

La [actividad core](https://learning-pro.skillnest.com/mod/page/view.php?id=15700) verifica el flujo del bloque 18, extendido con las rutas del 19 y manejo de errores por paso.

| Entregable | Ubicación |
|---|---|
| Flujo, clasificación y manejo de errores (`enrutamiento.py` en el ejemplo del curso) | [src/orquestacion.py](../src/orquestacion.py) |
| Pruebas del checklist completo | [tests/test_orquestacion.py](../tests/test_orquestacion.py) |
| Resultado de la verificación | [docs/evidencias/bloque-20-core-verificacion-pytest.txt](evidencias/bloque-20-core-verificacion-pytest.txt) |

Cada destino de `src/orquestacion.py` usa `with_fallbacks`. Si falla, devuelve una orientación para revisar el perfil local y registra la clase del error. `procesar_seguro` captura fallos anteriores a las rutas, incluida la clasificación. Las respuestas de recuperación se identifican con `estado`; los registros excluyen claves y cuerpos HTTP.

| Verificación | Evidencia en `tests/test_orquestacion.py` |
|---|---|
| Normalización y todos los destinos | `test_normalizacion_y_cada_ruta_incluida_predeterminada` |
| Clasificador completo y categorías válidas | `test_clasificador_completo_normaliza_y_limita_categorias` |
| Entrada vacía y ruta de aclaración | `test_entrada_vacia_usa_aclaracion_sin_clasificar` |
| Entrada ambigua sin categoría reconocida | `test_entrada_ambigua_se_aclara_con_clasificacion_completa` |
| Fallo de ruta y ejecución del fallback | `test_fallo_de_ruta_ejecuta_fallback_y_registra` |
| Fallo de clasificación y protección general | `test_fallo_clasificacion_cubierto_por_entrada_general` |
| Corte por límite de salida | `test_paso_truncado_no_alimenta_siguiente` |

```bash
python -m pytest tests/test_orquestacion.py -v
```

Las pruebas usan modelos simulados y no consumen API. La [verificación completa](evidencias/bloque-20-core-verificacion-pytest.txt) pasó con **86 pruebas**; se conserva el [registro anterior de 77 pruebas](evidencias/bloques-15-21-pytest.txt). Las [corridas reales](evidencias/orquestacion_agente.json) verifican la chain y las tres rutas; los fallos y los nuevos casos límite se fuerzan de manera controlada en la suite.

Estas verificaciones acreditan el recorrido y la recuperación del flujo. La calidad de las recomendaciones conserva los [límites de la evaluación](bloque-17-core-limites-metrica.md).
