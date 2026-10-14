# ModelLab AI

Proyecto en desarrollo enfocado en integrar inteligencia artificial generativa con herramientas de Machine Learning para facilitar el análisis e interpretación de modelos y resultados.

## Tecnologías

- Python 3
- Google Gemini API
- Requests
- Git y GitHub
- WSL2 / Ubuntu
- Postman

## Estado actual

- [x] Configuración del entorno de desarrollo.
- [x] Integración con Gemini mediante API REST.
- [x] Manejo de variables de entorno.
- [x] Pruebas de solicitudes HTTP con Postman.
- [ ] Implementación de herramientas de análisis de ML.
- [ ] Integración de agentes y RAG.
- [ ] Desarrollo de interfaz de usuario.

## Uso

Instalar dependencias:

```bash
pip install -r requirements.txt
```

Configurar `GEMINI_API_KEY` y `GEMINI_MODEL` en un archivo `.env`.

Ejecutar:

```bash
python src/main.py
```

## Pruebas

```bash
python -m unittest discover -s tests -v
```

## Documentación

La documentación y las pruebas de integración se encuentran en [`docs/`](docs/).

## Consideraciones

El proyecto se realiza como parte de la evaluación del programa "Especialización en Desarrollo con IA Generativa de Skillnest".

## Autor

Diego Miranda