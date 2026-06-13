# app/models.py
from mysql.connector import Error

# ==================== USUARIOS ====================

def obtener_usuario_por_email(connection, email):
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
        usuario = cursor.fetchone()
        cursor.close()
        return usuario
    except Error as e:
        print(f"Error en obtener_usuario_por_email: {e}")
        return None

def obtener_usuario_por_id(connection, usuario_id):
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuarios WHERE id = %s", (usuario_id,))
        usuario = cursor.fetchone()
        cursor.close()
        return usuario
    except Error as e:
        print(f"Error en obtener_usuario_por_id: {e}")
        return None

def crear_usuario_cliente(connection, nombre, email, password_hash):
    try:
        cursor = connection.cursor()
        query = "INSERT INTO usuarios (nombre, email, password_hash, rol) VALUES (%s, %s, %s, 'cliente')"
        cursor.execute(query, (nombre, email, password_hash))
        connection.commit()
        nuevo_id = cursor.lastrowid
        cursor.close()
        return nuevo_id
    except Error as e:
        print(f"Error en crear_usuario_cliente: {e}")
        connection.rollback()
        return None

def crear_usuario_admin_agente(connection, nombre, email, password_hash, rol):
    try:
        cursor = connection.cursor()
        query = "INSERT INTO usuarios (nombre, email, password_hash, rol) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (nombre, email, password_hash, rol))
        connection.commit()
        nuevo_id = cursor.lastrowid
        cursor.close()
        return nuevo_id
    except Error as e:
        print(f"Error en crear_usuario_admin_agente: {e}")
        connection.rollback()
        return None

def obtener_todos_agentes(connection):
    try:
        cursor = connection.cursor(dictionary=True)
        query = "SELECT id, nombre, email, rol, fecha_registro FROM usuarios WHERE rol IN ('agente', 'admin') ORDER BY fecha_registro DESC"
        cursor.execute(query)
        agentes = cursor.fetchall()
        cursor.close()
        return agentes
    except Error as e:
        return []

def obtener_agentes(connection):
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT id, nombre FROM usuarios WHERE rol IN ('agente', 'admin')")
        agentes = cursor.fetchall()
        cursor.close()
        return agentes
    except Error as e:
        return []

def actualizar_password_usuario(connection, usuario_id, new_password_hash):
    try:
        cursor = connection.cursor()
        query = "UPDATE usuarios SET password_hash = %s WHERE id = %s"
        cursor.execute(query, (new_password_hash, usuario_id))
        connection.commit()
        cursor.close()
        return True
    except Error as e:
        print(f"Error en actualizar_password_usuario: {e}")
        connection.rollback()
        return False

# ==================== TICKETS ====================

def soft_delete_ticket(connection, ticket_id, usuario_id):
    try:
        cursor = connection.cursor()
        query = "UPDATE tickets SET deleted_at = NOW(), deleted_by = %s WHERE id = %s"
        cursor.execute(query, (usuario_id, ticket_id))
        connection.commit()
        cursor.close()
        return True
    except Error as e:
        print(f"Error en soft_delete_ticket: {e}")
        connection.rollback()
        return False

def restaurar_ticket(connection, ticket_id):
    try:
        cursor = connection.cursor()
        query = "UPDATE tickets SET deleted_at = NULL, deleted_by = NULL WHERE id = %s"
        cursor.execute(query, (ticket_id,))
        connection.commit()
        cursor.close()
        return True
    except Error as e:
        print(f"Error en restaurar_ticket: {e}")
        connection.rollback()
        return False

def obtener_tickets_eliminados(connection):
    try:
        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM tickets WHERE deleted_at IS NOT NULL ORDER BY deleted_at DESC"
        cursor.execute(query)
        tickets = cursor.fetchall()
        cursor.close()
        return tickets
    except Error as e:
        print(f"Error en obtener_tickets_eliminados: {e}")
        return []

def borrar_ticket_permanente(connection, ticket_id):
    try:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM respuestas WHERE ticket_id = %s", (ticket_id,))
        cursor.execute("DELETE FROM logs_estados WHERE ticket_id = %s", (ticket_id,))
        cursor.execute("DELETE FROM tickets WHERE id = %s", (ticket_id,))
        connection.commit()
        cursor.close()
        return True
    except Error as e:
        print(f"Error en borrar_ticket_permanente: {e}")
        connection.rollback()
        return False

def obtener_tickets_sin_asignar(connection):
    try:
        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM tickets WHERE agente_asignado_id IS NULL AND deleted_at IS NULL ORDER BY created_at DESC"
        cursor.execute(query)
        tickets = cursor.fetchall()
        cursor.close()
        return tickets
    except Error as e:
        print(f"Error en obtener_tickets_sin_asignar: {e}")
        return []

def crear_ticket(connection, titulo, descripcion, usuario_id):
    try:
        cursor = connection.cursor()
        query = """
            INSERT INTO tickets (titulo, descripcion, estado, usuario_id) 
            VALUES (%s, %s, 'abierto', %s)
        """
        cursor.execute(query, (titulo, descripcion, usuario_id))
        connection.commit()
        nuevo_id = cursor.lastrowid
        cursor.close()
        return nuevo_id
    except Error as e:
        print(f"Error en crear_ticket: {e}")
        connection.rollback()
        return None

def obtener_tickets(connection, usuario_id=None, rol='cliente'):
    try:
        cursor = connection.cursor(dictionary=True)
        if rol == 'cliente':
            query = "SELECT * FROM tickets WHERE usuario_id = %s AND deleted_at IS NULL ORDER BY created_at DESC"
            cursor.execute(query, (usuario_id,))
        else:
            query = "SELECT * FROM tickets WHERE deleted_at IS NULL ORDER BY created_at DESC"
            cursor.execute(query)
        tickets = cursor.fetchall()
        cursor.close()
        return tickets
    except Error as e:
        print(f"Error en obtener_tickets: {e}")
        return []

def obtener_ticket_por_id(connection, ticket_id):
    try:
        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM tickets WHERE id = %s AND deleted_at IS NULL"
        cursor.execute(query, (ticket_id,))
        ticket = cursor.fetchone()
        cursor.close()
        return ticket
    except Error as e:
        print(f"Error en obtener_ticket_por_id: {e}")
        return None

def cancelar_ticket(connection, ticket_id):
    try:
        cursor = connection.cursor()
        query = "UPDATE tickets SET estado = 'cancelado', cancelado_por_cliente = TRUE WHERE id = %s AND estado = 'abierto'"
        cursor.execute(query, (ticket_id,))
        connection.commit()
        filas = cursor.rowcount
        cursor.close()
        return filas > 0
    except Error as e:
        print(f"Error en cancelar_ticket: {e}")
        connection.rollback()
        return False

def actualizar_ticket_prioridad_estado(connection, ticket_id, prioridad, estado, agente_id=None):
    try:
        cursor = connection.cursor()
        query = "UPDATE tickets SET prioridad = %s, estado = %s, agente_asignado_id = %s WHERE id = %s"
        cursor.execute(query, (prioridad, estado, agente_id, ticket_id))
        connection.commit()
        cursor.close()
        return True
    except Error as e:
        print(f"Error al actualizar ticket: {e}")
        connection.rollback()
        return False

def cambiar_estado_ticket(connection, ticket_id, nuevo_estado):
    try:
        cursor = connection.cursor()
        query = "UPDATE tickets SET estado = %s WHERE id = %s"
        cursor.execute(query, (nuevo_estado, ticket_id))
        connection.commit()
        cursor.close()
        return True
    except Error as e:
        connection.rollback()
        return False

def reabrir_ticket(connection, ticket_id):
    try:
        cursor = connection.cursor()
        query = "UPDATE tickets SET estado = 'abierto' WHERE id = %s AND estado IN ('resuelto', 'cerrado')"
        cursor.execute(query, (ticket_id,))
        connection.commit()
        cursor.close()
        return True
    except Error as e:
        print(f"Error al reabrir ticket: {e}")
        connection.rollback()
        return False

# ==================== RESPUESTAS ====================

def agregar_respuesta(connection, ticket_id, usuario_id, mensaje):
    try:
        cursor = connection.cursor()
        query = "INSERT INTO respuestas (ticket_id, usuario_id, mensaje) VALUES (%s, %s, %s)"
        cursor.execute(query, (ticket_id, usuario_id, mensaje))
        connection.commit()
        
        # Actualizar updated_at en tickets (MySql hace on update autom, pero podemos forzar con UPDATE)
        query_update = "UPDATE tickets SET updated_at = CURRENT_TIMESTAMP WHERE id = %s"
        cursor.execute(query_update, (ticket_id,))
        connection.commit()
        
        cursor.close()
        return True
    except Error as e:
        print(f"Error en agregar_respuesta: {e}")
        connection.rollback()
        return False

def obtener_respuestas_ticket(connection, ticket_id):
    try:
        cursor = connection.cursor(dictionary=True)
        query = """
            SELECT r.*, u.nombre, u.rol 
            FROM respuestas r
            JOIN usuarios u ON r.usuario_id = u.id
            WHERE r.ticket_id = %s 
            ORDER BY r.created_at ASC
        """
        cursor.execute(query, (ticket_id,))
        respuestas = cursor.fetchall()
        cursor.close()
        return respuestas
    except Error as e:
        print(f"Error en obtener_respuestas_ticket: {e}")
        return []

# ==================== LOGS ESTADOS ====================

def registrar_log_estado(connection, ticket_id, estado_anterior, estado_nuevo, cambiado_por):
    try:
        cursor = connection.cursor()
        query = """
            INSERT INTO logs_estados (ticket_id, estado_anterior, estado_nuevo, cambiado_por) 
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(query, (ticket_id, estado_anterior, estado_nuevo, cambiado_por))
        connection.commit()
        cursor.close()
        return True
    except Error as e:
        print(f"Error en registrar_log_estado: {e}")
        connection.rollback()
        return False

def obtener_historial_ticket(connection, ticket_id):
    try:
        cursor = connection.cursor(dictionary=True)
        query = """
            SELECT l.*, u.nombre as nombre_usuario
            FROM logs_estados l
            JOIN usuarios u ON l.cambiado_por = u.id
            WHERE l.ticket_id = %s
            ORDER BY l.fecha_cambio DESC
        """
        cursor.execute(query, (ticket_id,))
        historial = cursor.fetchall()
        cursor.close()
        return historial
    except Error as e:
        print(f"Error en obtener_historial: {e}")
        return []

# ==================== REPORTES ====================

def obtener_reportes_basicos(connection):
    try:
        cursor = connection.cursor(dictionary=True)
        # 1. Estados
        query_estados = """
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN estado = 'abierto' THEN 1 ELSE 0 END) as abiertos,
                SUM(CASE WHEN estado = 'resuelto' THEN 1 ELSE 0 END) as resueltos,
                SUM(CASE WHEN estado = 'en_progreso' THEN 1 ELSE 0 END) as en_progreso,
                SUM(CASE WHEN estado = 'cerrado' THEN 1 ELSE 0 END) as cerrados
            FROM tickets WHERE deleted_at IS NULL
        """
        cursor.execute(query_estados)
        res = cursor.fetchone()
        
        if res:
            for k in res:
                res[k] = int(res[k]) if res[k] is not None else 0
        else:
            res = {'total':0, 'abiertos':0, 'resueltos':0, 'en_progreso':0, 'cerrados':0}
            
        # 2. Prioridades
        query_prioridades = """
            SELECT prioridad, COUNT(*) as cantidad 
            FROM tickets 
            WHERE deleted_at IS NULL 
            GROUP BY prioridad
        """
        cursor.execute(query_prioridades)
        prioridades_raw = cursor.fetchall()
        
        # Formatear prioridades
        res['prioridades'] = {
            'baja': 0, 'media': 0, 'alta': 0, 'urgente': 0, 'sin_asignar': 0
        }
        for p in prioridades_raw:
            clave = p['prioridad'] if p['prioridad'] else 'sin_asignar'
            if clave in res['prioridades']:
                res['prioridades'][clave] = p['cantidad']
                
        # 3. Agentes
        query_agentes = """
            SELECT u.nombre as agente, COUNT(t.id) as cantidad
            FROM tickets t
            JOIN usuarios u ON t.agente_asignado_id = u.id
            WHERE t.deleted_at IS NULL
            GROUP BY u.id
            ORDER BY cantidad DESC
            LIMIT 5
        """
        cursor.execute(query_agentes)
        res['agentes'] = cursor.fetchall()

        cursor.close()
        return res
    except Error as e:
        print(f"Error en obtener_reportes_basicos: {e}")
        return {
            'total':0, 'abiertos':0, 'resueltos':0, 'en_progreso':0, 'cerrados':0,
            'prioridades': {'baja': 0, 'media': 0, 'alta': 0, 'urgente': 0, 'sin_asignar': 0},
            'agentes': []
        }
