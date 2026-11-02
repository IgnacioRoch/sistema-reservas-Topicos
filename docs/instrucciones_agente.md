# Registro de Preparación e Instrucciones del Agente

## 1. Entorno y Contexto del Agente
* **Herramienta / Entorno:** Asistente de programación de inteligencia artificial integrado en entorno de desarrollo web.
* **Modelo:** Modelo de lenguaje de gran escala optimizado para asistencia en programación, depuración y arquitectura de software local.
* **Función:** Actuar como agente de programación para la generación de código base, lógica de negocio relacional, suite de pruebas automáticas y estructuración de documentación técnica.

## 2. Instrucciones Saneadas Suministradas al Agente
Las directrices principales proporcionadas al agente para guiar el desarrollo de la solución fueron las siguientes:

> "Desarrollar un sistema local de reservas de laboratorios en Python que cumpla estrictamente con el siguiente alcance:
> 1. **Inventario precargado:** Cargar los 5 equipos físicos requeridos (`MIC-01`, `MIC-02`, `OSC-01`, `MUL-01`, `FUE-01`).
> 2. **Reglas de negocio y superposiciones:** Validar que el solicitante no esté vacío, que las fechas sean válidas (inicio estricamente anterior al fin) y rechazar superposiciones de reservas activas para la misma unidad. Permitir límites consecutivos exactos (ej. fin de una reserva igual al inicio de otra) y reservas simultáneas de unidades distintas.
> 3. **Cancelaciones y Persistencia:** Permitir cancelar reservas manteniendo el identificador y los datos históricos en una base de datos SQLite local, liberando únicamente el intervalo horario. Los datos deben persistir tras reiniciar la aplicación.
> 4. **Pruebas automáticas:** Crear una suite de pruebas con `pytest` que valide la creación, rechazo de solapamientos, límites consecutivos, unidades distintas, entradas inválidas, cancelaciones y persistencia."

## 3. Contexto Excluido e Instrucciones Omitidas
* Se excluyó explícitamente cualquier requisito fuera de alcance, tales como autenticación de usuarios por roles, pasarelas de pago, despliegue en la nube, notificaciones externas o arquitecturas de microservicios distribuidos, priorizando una solución local ligera y reproducible.

## 4. Permisos, Controles y Aprobaciones Humanas
* **Acciones permitidas:** Generación de archivos de código fuente (`main.py`), pruebas (`test_reservas.py`) y documentación (`README.md`).
* **Supervisión humana:** Cada fragmento de código generado por el agente fue revisado, probado mediante ejecución local y validado manualmente antes de registrar los cambios definitivos (commits) en el repositorio.
