import sqlite3
from datetime import datetime

DB_FILE = "reservas.db"

INVENTARIO_INICIAL = [
    ("MIC-01", "Microscopio digital"),
    ("MIC-02", "Microscopio digital"),
    ("OSC-01", "Osciloscopio"),
    ("MUL-01", "Multímetro"),
    ("FUE-01", "Fuente de alimentación"),
]

def inicializar_base_datos():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Tabla de inventario
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventario (
            id TEXT PRIMARY KEY,
            equipo TEXT NOT NULL
        )
    """)
    
    # Tabla de reservas (estado: 'ACTIVA' o 'CANCELADA')
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reservas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            unidad_id TEXT NOT NULL,
            solicitante TEXT NOT NULL,
            inicio TEXT NOT NULL,
            fin TEXT NOT NULL,
            estado TEXT NOT NULL,
            FOREIGN KEY (unidad_id) REFERENCES inventario (id)
        )
    """)
    
    # Cargar inventario inicial si está vacío
    cursor.execute("SELECT COUNT(*) FROM inventario")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("INSERT INTO inventario (id, equipo) VALUES (?, ?)", INVENTARIO_INICIAL)
        
    conn.commit()
    conn.close()

def validar_unidad(unidad_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM inventario WHERE id = ?", (unidad_id,))
    existe = cursor.fetchone() is not None
    conn.close()
    return existe

def crear_reserva(unidad_id, solicitante, inicio_str, fin_str):
    # Validaciones básicas
    if not validar_unidad(unidad_id):
        raise ValueError(f"Unidad desconocida: {unidad_id}")
    
    if not solicitante or not solicitante.strip():
        raise ValueError("El solicitante no puede estar vacío ni compuesto solo por espacios.")
    
    try:
        inicio = datetime.fromisoformat(inicio_str)
        fin = datetime.fromisoformat(fin_str)
    except ValueError:
        raise ValueError("Formato de fecha y hora inválido. Use AAAA-MM-DDTHH:MM:SS")
    
    if inicio >= fin:
        raise ValueError("La fecha de inicio debe ser estrictamente anterior a la de fin.")
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Verificar superposiciones con reservas ACTIVAS de la misma unidad
    # Regla: Se permiten límites consecutivos (ej: fin de una == inicio de otra)
    # Hay solapamiento si: (inicio < fin_existente) AND (fin > inicio_existente)
    cursor.execute("""
        SELECT id FROM reservas 
        WHERE unidad_id = ? AND estado = 'ACTIVA'
        AND ? < fin AND ? > inicio
    """, (unidad_id, inicio_str, fin_str))
    
    superposicion = cursor.fetchone()
    if superposicion:
        conn.close()
        raise ValueError("El intervalo se superpone con una reserva activa existente para esta unidad.")
    
    cursor.execute("""
        INSERT INTO reservas (unidad_id, solicitante, inicio, fin, estado)
        VALUES (?, ?, ?, ?, 'ACTIVA')
    """, (unidad_id, solicitante.strip(), inicio_str, fin_str))
    
    reserva_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return reserva_id

def cancelar_reserva(reserva_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT estado FROM reservas WHERE id = ?", (reserva_id,))
    row = cursor.fetchone()
    
    if not row:
        conn.close()
        raise ValueError(f"No se encontró la reserva con ID {reserva_id}")
    
    cursor.execute("UPDATE reservas SET estado = 'CANCELADA' WHERE id = ?", (reserva_id,))
    conn.commit()
    conn.close()

def consultar_disponibilidad(unidad_id, inicio_str, fin_str):
    if not validar_unidad(unidad_id):
        raise ValueError(f"Unidad desconocida: {unidad_id}")
    
    try:
        inicio = datetime.fromisoformat(inicio_str)
        fin = datetime.fromisoformat(fin_str)
    except ValueError:
        raise ValueError("Formato de fecha y hora inválido.")
        
    if inicio >= fin:
        raise ValueError("El inicio debe ser anterior al fin.")
        
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT COUNT(*) FROM reservas 
        WHERE unidad_id = ? AND estado = 'ACTIVA'
        AND ? < fin AND ? > inicio
    """, (unidad_id, inicio_str, fin_str))
    
    ocupado = cursor.fetchone()[0] > 0
    conn.close()
    return not ocupado

if __name__ == "__main__":
    inicializar_base_datos()
    print("Base de datos inicializada correctamente.")
