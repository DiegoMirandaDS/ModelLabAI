# Verificación de la orquestación — core del bloque 20

La [actividad core](https://learning-pro.skillnest.com/mod/page/view.php?id=15700) verifica el flujo del bloque 18, extendido con las rutas del 19 y manejo de errores por paso.

Cada destino de `src/orquestacion.py` usa `with_fallbacks`. Si falla, devuelve una orientación para revisar el perfil local y registra la clase del error. `procesar_seguro` captura fallos anteriores a las rutas, incluida la clasificación. Las respuestas de recuperación se identifican con `estado`; los registros excluyen claves y cuerpos HTTP.

| Verificación | Evidencia en `tests/test_orquestacion.py` |
|---|---|
| Normalización y todos los destinos | `test_normalizacion_y_cada_ruta_incluida_predeterminada` |
| Fallo de ruta y ejecución del fallback | `test_fallo_de_ruta_ejecuta_fallback_y_registra` |
| Fallo de clasificación y protección general | `test_fallo_clasificacion_cubierto_por_entrada_general` |
| Corte por límite de salida | `test_paso_truncado_no_alimenta_siguiente` |

```bash
python -m pytest tests/test_orquestacion.py -v
```

Las pruebas usan modelos simulados y no consumen API. La [suite completa registrada](evidencias/bloques-15-21-pytest.txt) pasó con **77 pruebas**. Las [corridas reales](evidencias/orquestacion_agente.json) verifican la chain y las tres rutas; los fallos se fuerzan de manera controlada en la suite.

Estas verificaciones acreditan el recorrido y la recuperación del flujo. La calidad de las recomendaciones conserva los [límites de la evaluación](bloque-17-core-limites-metrica.md).
