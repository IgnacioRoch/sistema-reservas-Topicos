# sistema-reservas-RochIgnacio

# Sistema de Reservas de Equipos de Laboratorio con Agente

Solución local y verificable desarrollada para gestionar reservas de equipos de laboratorio físico, evitando superposiciones y manteniendo el historial de cancelaciones[cite: 1, 2].

---

## 1. Especificación breve
* **Problema:** La coordinación de un laboratorio registraba pedidos en mensajes y planillas, lo que generaba horarios superpuestos para una misma unidad y bloqueos permanentes tras cancelaciones[cite: 1].
* **Alcance:** 
  * Lectura de inventario precargado (5 unidades físicas identificadas: `MIC-01`, `MIC-02`, `OSC-01`, `MUL-01`, `FUE-01`)[cite: 1].
  * Creación de reservas con unidad, solicitante no vacío, fecha/hora de inicio y fin[cite: 2].
  * Cancelación de reservas manteniendo el identificador y liberando el intervalo horario[cite: 2].
  * Persistencia de datos para recuperarlos tras reiniciar la aplicación[cite: 2].
* **Reglas y Criterios de Aceptación:**
  * Validación de unidades conocidas y solicitantes no vacíos[cite: 2].
  * Inicio estrictamente anterior al fin[cite: 2].
  * Rechazo de superposiciones de reservas activas para la misma unidad, permitiendo límites consecutivos (ej. fin de una = inicio de otra) y reservas simultáneas de unidades distintas[cite: 2].

---

## 2. Solución
* **Estructura:**
  * `main.py`: Lógica central de negocio, inicialización de base de datos SQLite y gestión de reservas.
  * `test_reservas.py`: Suite de pruebas automáticas con `pytest`.
  * `reservas.db`: Archivo de base de datos local para la persistencia.
* **Decisiones técnicas:** Se utilizó **Python** junto con **SQLite** por su ligereza, soporte nativo de transacciones y facilidad de persistencia en archivo local sin requerir servicios externos[cite: 2].

* ## 🧠 Desafíos Técnicos y Decisiones de Diseño

Durante el desarrollo de la aplicación, se resolvieron diversos retos arquitectónicos y de lógica de negocio que garantizan la robustez y previsibilidad del sistema:

### 1. Gestión de Intervalos Semiabiertos y Límites Consecutivos
* **El reto:** Evitar falsos positivos en las superposiciones temporales permitiendo al mismo tiempo que una unidad pueda ser reservada de forma consecutiva (por ejemplo, que una reserva finalice exactamente a las 11:00 y otra comience a las 11:00 del mismo día).
* **La solución:** Se implementó una lógica de intervalos semiabiertos matemáticos tipo $[inicio, fin)$, evaluando la condición estricta:
  $$\text{inicio}_A < \text{fin}_B \quad \text{y} \quad \text{inicio}_B < \text{fin}_A$$
  Esto permite que los límites colindantes coexistan sin que el sistema bloquee el traspaso de turnos entre usuarios.

### 2. Cancelación Lógica vs. Eliminación Física
* **El reto:** Cumplir con la regla de negocio que exige liberar los intervalos horarios de una unidad cancelada, pero preservando de manera inalterable la trazabilidad y el identificador único del registro histórico.
* **La solución:** En lugar de ejecutar una sentencia `DELETE` en la base de datos, las cancelaciones operan mediante una **actualización de estado** (`ACTIVA` $\rightarrow$ `CANCELADA`). De este modo, las consultas de disponibilidad y superposición filtran únicamente las reservas activas, mientras que el historial general permanece intacto para auditorías futuras.

### 3. Persistencia Transaccional con SQLite
* **El reto:** Garantizar que los datos de inventario y reservas no se pierdan ante cierres inesperados de la aplicación, manteniendo una arquitectura ligera sin depender de servicios externos pesados.
* **La solución:** Se integró el motor estándar `sqlite3` con un manejo controlado de conexiones transaccionales (`commit`/`rollback`). Esto asegura la atomicidad en la inserción de registros y permite que la base de datos se autogenere localmente de forma limpia en la primera ejecución.
  
* * **Ejemplo de uso (Entrada y Salida):**
  * *Creación válida:* `crear_reserva("MIC-01", "Ana Pérez", "2026-11-10T10:00:00", "2026-11-10T11:00:00")` -> Retorna ID de reserva `1`.
  * *Intento de superposición:* `crear_reserva("MIC-01", "Carlos Gómez", "2026-11-10T10:30:00", "2026-11-10T11:30:00")` -> Lanza `ValueError: El intervalo se superpone...`.
  * *Límite consecutivo (Permitido):* `crear_reserva("MIC-01", "Carlos Gómez", "2026-11-10T11:00:00", "2026-11-10T12:00:00")` -> Retorna ID de reserva `2`.
     
* **Instrucciones de instalación y ejecución:**
  1. Instalar dependencias necesarias (ej. `pytest`):
     ```bash
     pip install pytest
     ```
  2. Ejecutar las pruebas automáticas:
     ```bash
     pytest test_reservas.py
     ```
* **Persistencia:** Los datos se almacenan en `reservas.db`. Eliminar este archivo borra el historial de reservas (equivalente a reiniciar el almacenamiento de datos).
* **Limitaciones y pendientes:** Fuera de alcance autenticación por roles, interfaces gráficas complejas y concurrencia distribuida[cite: 2].

---

## 3. Preparación del agente
* **Entorno y Modelo:** Asistente de programación de inteligencia artificial integrado en entorno de desarrollo web.
* **Instrucciones y contexto:** Se suministraron las reglas de negocio estrictas del archivo de consigna (inventario de 5 equipos, validación de solapamientos con límites consecutivos, persistencia local y pruebas automáticas).
* **Permisos y controles:** Toda modificación de código y estructura fue revisada y aprobada manualmente antes de su integración definitiva en el repositorio.

---

## 4. Registro de decisiones y delegación

### Episodio 1: Lógica de superposición y límites consecutivos
* **Objetivo y contexto:** Asegurar que el sistema rechace solapamientos pero permita límites consecutivos exactos (ej. una reserva terminando a las 11:00 y otra iniciando a las 11:00).
* **Instrucción al agente:** *"Ajusta la consulta SQL de validación en `crear_reserva` para que utilice operadores estrictos que permitan límites consecutivos sin generar falsos positivos de superposición"*.
* **Resultado del agente:** Implementación de la condición `? < fin AND ? > inicio`.
* **Decisión humana:** Aceptado tras comprobar que las pruebas unitarias de límites consecutivos pasaban exitosamente.

### Episodio 2: Manejo de estados en cancelaciones
* **Objetivo y contexto:** Permitir cancelar reservas conservando el identificador y los datos históricos, pero liberando el intervalo para futuras reservas[cite: 2].
* **Instrucción al agente:** *"Modifica la función de cancelación para que en lugar de eliminar el registro de la base de datos, actualice su estado a 'CANCELADA' y asegúrate de que las consultas de disponibilidad y superposición solo consideren reservas con estado 'ACTIVA'"*.
* **Resultado del agente:** Actualización de las consultas SQL filtrando por `estado = 'ACTIVA'`.
* **Decisión humana:** Aceptado por cumplir exactamente con la regla de negocio de auditoría e historial[cite: 3].

### Episodio 3: Pruebas de persistencia ante reinicios
* **Objetivo y contexto:** Verificar que las reservas persistan tras detener y reiniciar la aplicación[cite: 2].
* **Instrucción al agente:** *"Diseña una prueba en `test_reservas.py` que simule el reinicio de la aplicación reabriendo la conexión o reinicializando el flujo para comprobar que las reservas activas siguen bloqueando el horario"*.
* **Resultado del agente:** Creación de la prueba `test_persistencia_reinicio`.
* **Decisión humana:** Aceptado al verificar el correcto funcionamiento del almacenamiento en archivo SQLite[cite: 3].
