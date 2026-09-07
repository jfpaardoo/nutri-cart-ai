# Guía de Contribución

Agradecemos tu interés en contribuir a ComeYCuadra.

## Flujo de Trabajo

1. Fork del Repositorio: Crear una copia del proyecto en GitHub.
2. Crear una Rama de Característica:
   ```bash
   git checkout -b feature/nueva-funcionalidad
   ```
3. Buenas Prácticas de Código:
   - Respetar los principios SOLID y la separación de capas de Clean Architecture.
   - No introducir dependencias directas de frameworks en `app/domain/`.
   - Si se agrega un nuevo supermercado, implementar la interfaz `SupermarketStrategy` y registrarlo en `SupermarketFactory`.
4. Ejecutar Pruebas Unitarias:
   ```bash
   cd backend
   .venv\Scripts\python -m pytest -v
   ```
   Asegurarse de que todos los tests pasen y añadir pruebas unitarias para cualquier nueva funcionalidad.
5. Pull Request: Abrir un PR detallando los cambios introducidos y la salida de los tests.
