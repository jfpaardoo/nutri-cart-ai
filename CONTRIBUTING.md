# Guía de Contribución 🤝

¡Agradecemos tu interés en contribuir a **NutriSuper Planner**!

## Flujo de Trabajo

1. **Fork del Repositorio**: Crea tu copia del proyecto en GitHub.
2. **Crear una Rama de Característica**:
   ```bash
   git checkout -b feature/nueva-funcionalidad
   ```
3. **Buenas Prácticas de Código**:
   - Respeta los principios **SOLID** y la separación de capas de **Clean Architecture**.
   - No introduzcas dependencias directas de frameworks en `app/domain/`.
   - Si agregas un nuevo supermercado, implementa la interfaz `SupermarketStrategy` y regístralo en `SupermarketFactory`.
4. **Ejecutar Pruebas Unitarias**:
   ```bash
   cd backend
   .venv\Scripts\python -m pytest -v
   ```
   Asegúrate de que todos los tests pasen y añade tests nuevos para cualquier funcionalidad nueva.
5. **Pull Request**: Abre un PR describiendo el problema resuelto y adjuntando la salida de los tests.
