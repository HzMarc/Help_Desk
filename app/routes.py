from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app, jsonify
from app.models import (
    obtener_usuario_por_email, obtener_usuario_por_id, crear_usuario_cliente, obtener_tickets, 
    crear_ticket, obtener_ticket_por_id, cancelar_ticket, actualizar_ticket_prioridad_estado,
    cambiar_estado_ticket, reabrir_ticket, agregar_respuesta, obtener_respuestas_ticket,
    registrar_log_estado, obtener_historial_ticket, obtener_agentes,
    obtener_tickets_sin_asignar, crear_usuario_admin_agente, obtener_todos_agentes, obtener_reportes_basicos,
    actualizar_password_usuario, soft_delete_ticket, restaurar_ticket, obtener_tickets_eliminados, borrar_ticket_permanente
)
from app.utils import login_requerido, rol_requerido
from app import bcrypt, get_db_connection
from datetime import datetime, timedelta

main = Blueprint('main', __name__)

@main.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('main.login'))

# ======================= AUTH =======================

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        conn = get_db_connection(current_app)
        if not conn:
            flash("Error crítico: No se pudo conectar a la base de datos.", "danger")
            return render_template('login/login.html')
            
        usuario = obtener_usuario_por_email(conn, email)
        conn.close()
        
        if usuario:
            es_valido = False
            try:
                es_valido = bcrypt.check_password_hash(usuario['password_hash'], password)
            except ValueError:
                if usuario['password_hash'] == password:
                    es_valido = True
                    
            if es_valido:
                session['user_id'] = usuario['id']
                session['nombre'] = usuario['nombre']
                session['rol'] = usuario['rol']
                return redirect(url_for('main.dashboard'))
            else:
                flash("Contraseña incorrecta.", "danger")
        else:
            flash("Usuario no encontrado.", "danger")
            
    return render_template('login/login.html')

@main.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        email = request.form.get('email')
        password = request.form.get('password')
        
        password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        
        conn = get_db_connection(current_app)
        if not conn:
            flash("Error crítico: No se pudo conectar a la base de datos.", "danger")
            return render_template('login/registro.html')
            
        nuevo_id = crear_usuario_cliente(conn, nombre, email, password_hash)
        conn.close()
        
        if nuevo_id:
            flash("Registro exitoso. Ahora puedes iniciar sesión.", "success")
            return redirect(url_for('main.login'))
        else:
            flash("Error en el registro. El correo podría ya estar en uso.", "danger")
            
    return render_template('login/registro.html')

@main.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main.login'))

# ======================= TICKETS CRUD =======================

@main.route('/dashboard')
@login_requerido
def dashboard():
    conn = get_db_connection(current_app)
    if not conn:
        flash("Error de conexión a la base de datos.", "danger")
        return render_template('dashboard.html', tickets=[])
        
    rol = session.get('rol')
    usuario_id = session.get('user_id')
    
    tickets = obtener_tickets(conn, usuario_id, rol)
    conn.close()
    
    return render_template('dashboard.html', tickets=tickets)

@main.route('/ticket/nuevo', methods=['GET', 'POST'])
@login_requerido
def nuevo_ticket():
    if request.method == 'POST':
        titulo = request.form.get('titulo')
        descripcion = request.form.get('descripcion')
        usuario_id = session.get('user_id')
        
        conn = get_db_connection(current_app)
        if not conn:
            flash("Error de conexión a la base de datos.", "danger")
            return render_template('crear_ticket.html')
            
        ticket_id = crear_ticket(conn, titulo, descripcion, usuario_id)
        conn.close()
        
        if ticket_id:
            flash("Ticket creado correctamente.", "success")
            return redirect(url_for('main.dashboard'))
        else:
            flash("Error al crear el ticket.", "danger")
            
    return render_template('crear_ticket.html')

@main.route('/ticket/<int:id>')
@login_requerido
def ticket_detalle(id):
    conn = get_db_connection(current_app)
    if not conn:
        flash("Error de conexión a la base de datos.", "danger")
        return redirect(url_for('main.dashboard'))
        
    ticket = obtener_ticket_por_id(conn, id)
    
    if not ticket:
        conn.close()
        flash("El ticket no existe.", "danger")
        return redirect(url_for('main.dashboard'))
        
    if session.get('rol') == 'cliente' and ticket['usuario_id'] != session.get('user_id'):
        conn.close()
        flash("No tienes permiso para ver este ticket.", "danger")
        return redirect(url_for('main.dashboard'))
        
    respuestas = obtener_respuestas_ticket(conn, id)
    agentes = []
    if session.get('rol') in ['admin', 'agente']:
        agentes = obtener_agentes(conn)
        
    conn.close()
    
    puede_cancelar = False
    if session.get('rol') == 'cliente' and ticket['estado'] == 'abierto':
        tiempo_creacion = ticket['created_at']
        if datetime.now() - tiempo_creacion < timedelta(minutes=30):
            puede_cancelar = True

    return render_template('ticket_detalle.html', ticket=ticket, respuestas=respuestas, puede_cancelar=puede_cancelar, agentes=agentes)

@main.route('/ticket/<int:id>/cancelar', methods=['POST'])
@login_requerido
def cancelar(id):
    if session.get('rol') != 'cliente':
        flash("Solo los clientes pueden cancelar tickets.", "danger")
        return redirect(url_for('main.ticket_detalle', id=id))
        
    conn = get_db_connection(current_app)
    if not conn:
        flash("Error de conexión a la BDD.", "danger")
        return redirect(url_for('main.dashboard'))
        
    ticket = obtener_ticket_por_id(conn, id)
    if not ticket or ticket['usuario_id'] != session.get('user_id'):
        conn.close()
        return redirect(url_for('main.dashboard'))
        
    if ticket['estado'] == 'abierto':
        if datetime.now() - ticket['created_at'] < timedelta(minutes=30):
            exito = cancelar_ticket(conn, id)
            if exito:
                registrar_log_estado(conn, id, 'abierto', 'cancelado', session.get('user_id'))
                flash("Ticket cancelado exitosamente.", "success")
            else:
                flash("Error al cancelar.", "danger")
        else:
            flash("Ha expirado el tiempo de 30 minutos para cancelar el ticket.", "danger")
    else:
        flash("El ticket ya no se puede cancelar.", "danger")
        
    conn.close()
    return redirect(url_for('main.ticket_detalle', id=id))

# ======================= RESPUESTAS (Paso 7) =======================

@main.route('/ticket/<int:id>/responder', methods=['POST'])
@login_requerido
def responder_ticket(id):
    mensaje = request.form.get('mensaje') or request.json.get('mensaje')
    if not mensaje:
        if request.is_json:
            return jsonify({"error": "Mensaje vacío"}), 400
        else:
            flash("El mensaje no puede estar vacío.", "danger")
            return redirect(url_for('main.ticket_detalle', id=id))
        
    conn = get_db_connection(current_app)
    if not conn:
        if request.is_json: return jsonify({"error": "Error de BD"}), 500
        flash("Error conectando a BDD.", "danger")
        return redirect(url_for('main.ticket_detalle', id=id))
        
    ticket = obtener_ticket_por_id(conn, id)
    
    if not ticket:
        conn.close()
        if request.is_json:
            return jsonify({"error": "Ticket no encontrado"}), 404
        return redirect(url_for('main.dashboard'))
        
    if session.get('rol') == 'cliente' and ticket['usuario_id'] != session.get('user_id'):
        conn.close()
        if request.is_json:
            return jsonify({"error": "No tienes permiso"}), 403
        return redirect(url_for('main.dashboard'))
        
    if ticket['estado'] in ['resuelto', 'cerrado', 'cancelado']:
        conn.close()
        if request.is_json:
            return jsonify({"error": "El ticket está cerrado/resuelto y no admite respuestas"}), 403
        flash("El ticket está cerrado o resuelto y no admite más respuestas.", "danger")
        return redirect(url_for('main.dashboard'))
        
    exito = agregar_respuesta(conn, id, session.get('user_id'), mensaje)
    conn.close()
    
    if request.is_json:
        if exito:
            return jsonify({"success": True})
        return jsonify({"error": "Error al guardar la respuesta"}), 500
    return redirect(url_for('main.ticket_detalle', id=id))

# ======================= GESTIÓN ESTADOS (Paso 8 API) =======================

@main.route('/api/ticket/<int:id>/gestionar', methods=['POST'])
@login_requerido
@rol_requerido('agente', 'admin')
def gestionar_ticket(id):
    datos = request.json
    prioridad = datos.get('prioridad')
    nuevo_estado = datos.get('estado')
    agente_id = datos.get('agente_id')
    
    conn = get_db_connection(current_app)
    if not conn: return jsonify({"error": "Error de BD"}), 500
    
    ticket = obtener_ticket_por_id(conn, id)
    estado_anterior = ticket['estado'] if ticket else None
    
    exito = actualizar_ticket_prioridad_estado(conn, id, prioridad, nuevo_estado, agente_id)
    if exito and estado_anterior != nuevo_estado:
        registrar_log_estado(conn, id, estado_anterior, nuevo_estado, session.get('user_id'))
        
    conn.close()
    return jsonify({"success": exito})

@main.route('/api/ticket/<int:id>/cambiar_estado', methods=['POST'])
@login_requerido
@rol_requerido('agente', 'admin')
def api_cambiar_estado(id):
    datos = request.json
    nuevo_estado = datos.get('nuevo_estado')
    
    conn = get_db_connection(current_app)
    if not conn: return jsonify({"error": "Error de BD"}), 500
    
    ticket = obtener_ticket_por_id(conn, id)
    estado_anterior = ticket['estado'] if ticket else None
    
    exito = cambiar_estado_ticket(conn, id, nuevo_estado)
    if exito and estado_anterior != nuevo_estado:
        registrar_log_estado(conn, id, estado_anterior, nuevo_estado, session.get('user_id'))
        
    conn.close()
    return jsonify({"success": exito})

@main.route('/api/ticket/<int:id>/historial', methods=['GET'])
@login_requerido
@rol_requerido('agente', 'admin')
def historial_ticket(id):
    conn = get_db_connection(current_app)
    if not conn: return jsonify({"error": "Error de BD"}), 500
    historial = obtener_historial_ticket(conn, id)
    conn.close()
    return jsonify(historial)

@main.route('/api/ticket/<int:id>/completo', methods=['GET'])
@login_requerido
def ticket_completo(id):
    conn = get_db_connection(current_app)
    if not conn: return jsonify({"error": "Error de BD"}), 500
    
    ticket = obtener_ticket_por_id(conn, id)
    if not ticket:
        conn.close()
        return jsonify({"error": "Ticket no encontrado"}), 404
        
    if session.get('rol') == 'cliente' and ticket['usuario_id'] != session.get('user_id'):
        conn.close()
        return jsonify({"error": "No tienes permiso"}), 403
        
    respuestas = obtener_respuestas_ticket(conn, id)
    
    puede_cancelar = False
    if session.get('rol') == 'cliente' and ticket['estado'] == 'abierto':
        tiempo_creacion = ticket['created_at']
        if datetime.now() - tiempo_creacion < timedelta(minutes=30):
            puede_cancelar = True
            
    agentes = []
    if session.get('rol') in ['admin', 'agente']:
        agentes = obtener_agentes(conn)
        
    conn.close()
    
    # Convertir datetimes a strings para JSON
    if ticket.get('created_at'):
        ticket['created_at'] = ticket['created_at'].strftime('%d/%m/%Y %H:%M')
    if ticket.get('updated_at'):
        ticket['updated_at'] = ticket['updated_at'].strftime('%d/%m/%Y %H:%M')
        
    for r in respuestas:
        if r.get('created_at'):
            r['created_at'] = r['created_at'].strftime('%d/%m/%Y %H:%M')
            
    return jsonify({
        "ticket": ticket,
        "respuestas": respuestas,
        "puede_cancelar": puede_cancelar,
        "agentes": agentes
    })

# ======================= RUTAS ADMIN Y AGENTES =======================

@main.route('/tickets/sin_asignar')
@login_requerido
@rol_requerido('agente', 'admin')
def tickets_sin_asignar():
    conn = get_db_connection(current_app)
    if not conn:
        flash("Error de BD.", "danger")
        return render_template('dashboard.html', tickets=[])
    tickets = obtener_tickets_sin_asignar(conn)
    conn.close()
    return render_template('dashboard.html', tickets=tickets, subtitulo="Tickets Sin Asignar")

@main.route('/admin/agentes', methods=['GET', 'POST'])
@login_requerido
@rol_requerido('admin')
def admin_agentes():
    conn = get_db_connection(current_app)
    if not conn:
        flash("Error de BD.", "danger")
        return redirect(url_for('main.dashboard'))
        
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        email = request.form.get('email')
        password = request.form.get('password')
        rol = request.form.get('rol') # agente o admin
        
        password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        
        nuevo_id = crear_usuario_admin_agente(conn, nombre, email, password_hash, rol)
        if nuevo_id:
            flash(f"Usuario '{nombre}' creado exitosamente como {rol}.", "success")
        else:
            flash("Error al crear. Posiblemente el correo ya existe.", "danger")
            
        return redirect(url_for('main.admin_agentes'))
        
    agentes = obtener_todos_agentes(conn)
    conn.close()
    return render_template('admin/agentes.html', agentes=agentes)

@main.route('/admin/reportes')
@login_requerido
@rol_requerido('admin')
def admin_reportes():
    conn = get_db_connection(current_app)
    if not conn:
        flash("Error de BD.", "danger")
        return redirect(url_for('main.dashboard'))
    reportes = obtener_reportes_basicos(conn)
    conn.close()
    return render_template('admin/reportes.html', reportes=reportes)

# ======================= FASE 4: PERFIL Y BÚSQUEDA =======================

@main.route('/perfil', methods=['GET'])
@login_requerido
def perfil():
    conn = get_db_connection(current_app)
    if not conn:
        flash("Error de conexión a la base de datos.", "danger")
        return redirect(url_for('main.dashboard'))
    usuario = obtener_usuario_por_id(conn, session['user_id'])
    conn.close()
    return render_template('perfil.html', usuario=usuario)

@main.route('/perfil/cambiar_password', methods=['POST'])
@login_requerido
def cambiar_password():
    datos = request.json
    actual = datos.get('actual')
    nueva = datos.get('nueva')
    
    conn = get_db_connection(current_app)
    usuario = obtener_usuario_por_id(conn, session['user_id'])
    
    if not bcrypt.check_password_hash(usuario['password_hash'], actual):
        conn.close()
        return jsonify({"success": False, "mensaje": "La contraseña actual es incorrecta."}), 400
        
    nueva_hash = bcrypt.generate_password_hash(nueva).decode('utf-8')
    exito = actualizar_password_usuario(conn, session['user_id'], nueva_hash)
    conn.close()
    
    if exito:
        return jsonify({"success": True})
    return jsonify({"success": False, "mensaje": "Error en el servidor al actualizar la contraseña."}), 500

@main.route('/api/buscar_tickets')
@login_requerido
def buscar_tickets():
    termino = request.args.get('q', '')
    usuario_rol = session['rol']
    usuario_id = session['user_id']
    
    conn = get_db_connection(current_app)
    cursor = conn.cursor(dictionary=True)
    
    query = """
        SELECT t.id, t.titulo, t.estado, t.prioridad, u.email as cliente_email 
        FROM tickets t
        JOIN usuarios u ON t.usuario_id = u.id
        WHERE t.deleted_at IS NULL
        AND (t.titulo LIKE %s OR t.descripcion LIKE %s OR u.email LIKE %s OR CAST(t.id AS CHAR) LIKE %s)
    """
    like_term = f"%{termino}%"
    params = [like_term, like_term, like_term, like_term]
    
    if usuario_rol == 'cliente':
        query += " AND t.usuario_id = %s"
        params.append(usuario_id)
        
    cursor.execute(query, params)
    tickets = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return jsonify(tickets)

# ======================= FASE 4: PAPELERA (SOFT DELETE) =======================

@main.route('/admin/papelera')
@rol_requerido('admin')
def admin_papelera():
    conn = get_db_connection(current_app)
    if not conn:
        return "Error de conexión", 500
    
    tickets_eliminados = obtener_tickets_eliminados(conn)
    conn.close()
    return render_template('admin/papelera.html', tickets=tickets_eliminados)

# ======================= FASE 4: EMAIL REPORTES =======================
from app.utils import enviar_email
from app.services.reporte_service import generar_reporte_html

@main.route('/admin/enviar_reporte', methods=['POST'])
@rol_requerido('admin')
def admin_enviar_reporte():
    conn = get_db_connection(current_app)
    if not conn:
        return jsonify({'success': False, 'message': 'Error de conexión a la BD.'})
    
    # Obtener el reporte actual
    reportes = obtener_reportes_basicos(conn)
    # Obtener el correo del admin que hizo la petición
    admin = obtener_usuario_por_id(conn, session['user_id'])
    conn.close()
    
    if admin and admin.get('email'):
        html_cuerpo = generar_reporte_html(reportes)
        enviado = enviar_email(
            destinatario=admin['email'],
            asunto=f"Reporte de Estado HelpDesk - {datetime.now().strftime('%d/%m/%Y')}",
            cuerpo_html=html_cuerpo
        )
        
        if enviado:
            return jsonify({'success': True, 'message': 'Reporte enviado con éxito a tu correo.'})
        else:
            return jsonify({'success': False, 'message': 'Fallo al enviar el correo. Revisa la configuración SMTP.'})
    
    return jsonify({'success': False, 'message': 'No se encontró correo para este usuario.'})

@main.route('/admin/ticket/<int:id>/eliminar_soft', methods=['POST'])
@login_requerido
@rol_requerido('admin')
def eliminar_ticket_soft(id):
    conn = get_db_connection(current_app)
    exito = soft_delete_ticket(conn, id, session['user_id'])
    conn.close()
    if exito:
        return jsonify({"success": True})
    return jsonify({"success": False, "mensaje": "Error al eliminar"}), 500

@main.route('/admin/ticket/<int:id>/restaurar', methods=['POST'])
@login_requerido
@rol_requerido('admin')
def restaurar_ticket_route(id):
    conn = get_db_connection(current_app)
    exito = restaurar_ticket(conn, id)
    conn.close()
    if exito:
        return jsonify({"success": True})
    return jsonify({"success": False, "mensaje": "Error al restaurar"}), 500

@main.route('/admin/ticket/<int:id>/borrar_permanente', methods=['POST'])
@login_requerido
@rol_requerido('admin')
def borrar_permanente_route(id):
    conn = get_db_connection(current_app)
    exito = borrar_ticket_permanente(conn, id)
    conn.close()
    if exito:
        return jsonify({"success": True})
    return jsonify({"success": False, "mensaje": "Error al borrar definitivamente"}), 500
