import os
import pytest
from datetime import datetime, timedelta
from main import (
    inicializar_base_datos,
    crear_reserva,
    cancelar_reserva,
    consultar_disponibilidad,
    DB_FILE
)

@pytest.fixture(autouse=True)
def limpiar_bd():
    # Limpiar base de datos antes de cada prueba
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
    inicializar_base_datos()

def test_creacion_valida():
    # Creación válida de una reserva
    res_id = crear_reserva("MIC-01", "Ana Pérez", "2026-11-10T10:00:00", "2026-11-10T11:00:00")
    assert res_id is not None
    assert consultar_disponibilidad("MIC-01", "2026-11-10T10:00:00", "2026-11-10T11:00:00") is False

def test_rechazo_superposicion():
    # Reservar de 10:00 a 11:00 y rechazar superposición (ej: 10:30 a 11:30)
    crear_reserva("MIC-01", "Ana Pérez", "2026-11-10T10:00:00", "2026-11-10T11:00:00")
    with pytest.raises(ValueError, match="superpone"):
        crear_reserva("MIC-01", "Carlos Gómez", "2026-11-10T10:30:00", "2026-11-10T11:30:00")

def test_limites_consecutivos():
    # Permitir límites consecutivos (ej: una termina a las 11:00 y otra empieza a las 11:00)
    crear_reserva("MIC-01", "Ana Pérez", "2026-11-10T10:00:00", "2026-11-10T11:00:00")
    res_id_2 = crear_reserva("MIC-01", "Carlos Gómez", "2026-11-10T11:00:00", "2026-11-10T12:00:00")
    assert res_id_2 is not None

def test_unidades_distintas_simultaneas():
    # MIC-02 puede reservarse en el mismo horario que MIC-01
    crear_reserva("MIC-01", "Ana Pérez", "2026-11-10T10:00:00", "2026-11-10T11:00:00")
    res_id_2 = crear_reserva("MIC-02", "Carlos Gómez", "2026-11-10T10:00:00", "2026-11-10T11:00:00")
    assert res_id_2 is not None

def test_entradas_invalidas():
    # Unidad desconocida
    with pytest.raises(ValueError):
        crear_reserva("EQUIPO-FALSO", "Ana Pérez", "2026-11-10T10:00:00", "2026-11-10T11:00:00")
    
    # Solicitante vacío
    with pytest.raises(ValueError):
        crear_reserva("MIC-01", "   ", "2026-11-10T10:00:00", "2026-11-10T11:00:00")
        
    # Inicio posterior o igual al fin
    with pytest.raises(ValueError):
        crear_reserva("MIC-01", "Ana Pérez", "2026-11-10T12:00:00", "2026-11-10T11:00:00")

def test_cancelacion_libera_horario():
    res_id = crear_reserva("MIC-01", "Ana Pérez", "2026-11-10T10:00:00", "2026-11-10T11:00:00")
    cancelar_reserva(res_id)
    
    # Ahora el horario debe estar disponible de nuevo
    disponible = consultar_disponibilidad("MIC-01", "2026-11-10T10:00:00", "2026-11-10T11:00:00")
    assert disponible is True

def test_persistencia_reinicio(tmp_path):
    # Simular persistencia creando una reserva y reabriendo la BD
    res_id = crear_reserva("MIC-01", "Ana Pérez", "2026-11-10T10:00:00", "2026-11-10T11:00:00")
    
    # Volver a inicializar (simula reinicio de aplicación)
    inicializar_base_datos()
    
    # Verificar que la reserva sigue ocupando el horario
    assert consultar_disponibilidad("MIC-01", "2026-11-10T10:00:00", "2026-11-10T11:00:00") is False
