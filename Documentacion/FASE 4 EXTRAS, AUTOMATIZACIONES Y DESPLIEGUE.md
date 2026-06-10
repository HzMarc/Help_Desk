## Paso 17: Reportes automáticos por email (para admin)

### 17.1 ¿Qué son y para qué sirven?

El administrador recibe **reportes periódicos** por correo electrónico con información del sistema. Pueden ser:

- **Reporte diario** (resumen del día)
    
- **Reporte semanal** (tendencias)
    
- **Reporte bajo demanda** (el admin lo pide manualmente)
    

### 17.2 Configuración de envío de emails

**En `config.py`:**
```python
# Configuración de correo
MAIL_SERVER = 'smtp.gmail.com'  # o smtp.office365.com, smtp.mail.yahoo.com
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USERNAME = 'tu_correo@gmail.com'
MAIL_PASSWORD = 'tu_contraseña_o_app_password'
MAIL_DEFAULT_SENDER = 'tu_correo@gmail.com'
```

**Para Gmail:** Necesitas crear una "Contraseña de aplicación" (no uses tu contraseña real):

1. Activar verificación en dos pasos en tu cuenta Google
    
2. Ir a "Contraseñas de aplicación" y generar una para "Correo"
    
3. Usar esa contraseña de 16 dígitos en `MAIL_PASSWORD`
    

### 17.3 Función para enviar email (en `app/utils.py`)
```python
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import render_template
from config import MAIL_SERVER, MAIL_PORT, MAIL_USERNAME, MAIL_PASSWORD

def enviar_email(destinatario, asunto, contenido_html, contenido_texto=None):
    """
    Envía un email usando SMTP
    
    Args:
        destinatario (str): Email del destinatario
        asunto (str): Asunto del correo
        contenido_html (str): HTML del cuerpo del correo
        contenido_texto (str): Versión texto plano (opcional)
    """
    try:
        # Crear mensaje
        msg = MIMEMultipart('alternative')
        msg['Subject'] = asunto
        msg['From'] = MAIL_USERNAME
        msg['To'] = destinatario
        
        # Versión texto plano (por si el cliente no soporta HTML)
        if contenido_texto:
            parte_texto = MIMEText(contenido_texto, 'plain')
            msg.attach(parte_texto)
        
        # Versión HTML
        parte_html = MIMEText(contenido_html, 'html')
        msg.attach(parte_html)
        
        # Conectar y enviar
        server = smtplib.SMTP(MAIL_SERVER, MAIL_PORT)
        server.starttls()
        server.login(MAIL_USERNAME, MAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        return True
    except Exception as e:
        print(f"Error al enviar email: {e}")
        return False
```

## 17.4 Generar reporte HTML 
(`app/services/reporte_service.py)
```python
def generar_reporte_html(tickets_filtrados, filtros_aplicados, fecha_generacion):
    """
    Genera el HTML del reporte para enviar por email
    """
    html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; }}
            table {{ border-collapse: collapse; width: 100%; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #4CAF50; color: white; }}
            .badge-abierto {{ background-color: #007bff; color: white; padding: 3px 8px; border-radius: 12px; }}
            .badge-progreso {{ background-color: #ffc107; color: black; padding: 3px 8px; border-radius: 12px; }}
            .badge-resuelto {{ background-color: #28a745; color: white; padding: 3px 8px; border-radius: 12px; }}
            .badge-cerrado {{ background-color: #6c757d; color: white; padding: 3px 8px; border-radius: 12px; }}
        </style>
    </head>
    <body>
        <h1>📊 Reporte del Sistema de Tickets</h1>
        <p><strong>Fecha de generación:</strong> {fecha_generacion}</p>
        
        <h2>📋 Filtros aplicados:</h2>
        <ul>
    """
    
    for clave, valor in filtros_aplicados.items():
        html += f"<li><strong>{clave}:</strong> {valor}</li>"
    
    html += "</ul><h2>🎫 Tickets encontrados:</h2>"
    
    if tickets_filtrados:
        html += """<table>
            <thead>
                <tr>
                    <th>ID</th><th>Título</th><th>Prioridad</th><th>Estado</th>
                    <th>Cliente</th><th>Agente</th><th>Fecha</th>
                </tr>
            </thead>
            <tbody>
        """
        
        for ticket in tickets_filtrados:
            estado_class = {
                'abierto': 'badge-abierto',
                'en_progreso': 'badge-progreso',
                'resuelto': 'badge-resuelto',
                'cerrado': 'badge-cerrado'
            }.get(ticket['estado'], '')
            
            html += f"""
                <tr>
                    <td>{ticket['id']}</td>
                    <td>{ticket['titulo']}</td>
                    <td>{ticket['prioridad'] or 'Sin asignar'}</td>
                    <td><span class="{estado_class}">{ticket['estado'].upper()}</span></td>
                    <td>{ticket['cliente_email']}</td>
                    <td>{ticket['agente_nombre'] or 'Sin asignar'}</td>
                    <td>{ticket['created_at']}</td>
                </tr>
            """
        
        html += "</tbody></table>"
        html += f"<p><strong>Total:</strong> {len(tickets_filtrados)} tickets</p>"
    else:
        html += "<p>✅ No se encontraron tickets con los filtros seleccionados.</p>"
    
    html += """
        <hr>
        <footer>
            <small>Este reporte ha sido generado automáticamente por el Sistema de Tickets HelpDesk.</small>
        </footer>
    </body>
    </html>
    """
    
    return html
```

### 17.5 Vista para que admin envíe reporte bajo demanda

**En `app/routes.py` (sección admin):**
```python
@app.route('/admin/enviar_reporte', methods=['POST'])
@rol_requerido('admin')
def enviar_reporte_bajo_demanda():
    """
    Admin puede enviar un reporte con filtros personalizados
    """
    # Obtener filtros del formulario
    filtros = {
        'estado': request.form.get('estado'),
        'prioridad': request.form.get('prioridad'),
        'fecha_desde': request.form.get('fecha_desde'),
        'fecha_hasta': request.form.get('fecha_hasta')
    }
    
    # Construir consulta SQL según filtros
    query = "SELECT * FROM tickets WHERE 1=1"
    params = []
    
    if filtros['estado'] and filtros['estado'] != 'todos':
        query += " AND estado = %s"
        params.append(filtros['estado'])
    
    if filtros['prioridad'] and filtros['prioridad'] != 'todas':
        query += " AND prioridad = %s"
        params.append(filtros['prioridad'])
    
    if filtros['fecha_desde']:
        query += " AND created_at >= %s"
        params.append(filtros['fecha_desde'])
    
    if filtros['fecha_hasta']:
        query += " AND created_at <= %s"
        params.append(filtros['fecha_hasta'])
    
    # Ejecutar consulta
    tickets = ejecutar_consulta(query, params)
    
    # Generar HTML del reporte
    from services.reporte_service import generar_reporte_html
    html = generar_reporte_html(tickets, filtros, datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    
    # Obtener email del admin (desde sesión o base de datos)
    admin_email = obtener_email_admin()
    
    # Enviar email
    from utils import enviar_email
    exito = enviar_email(
        destinatario=admin_email,
        asunto=f"Reporte de tickets - {datetime.now().strftime('%Y-%m-%d')}",
        contenido_html=html
    )
    
    # Guardar en tabla reportes_enviados
    guardar_reporte_enviado(admin_email, filtros)
    
    if exito:
        flash('Reporte enviado correctamente por email', 'success')
    else:
        flash('Error al enviar el reporte', 'danger')
    
    return redirect(url_for('admin_panel'))
```

### 17.6 Reporte automático diario (con cron o scheduler)

**Opción A: Usando APScheduler (recomendado)**

Instalar: `pip install APScheduler`

**En `app/__init__.py`:**
```python
from apscheduler.schedulers.background import BackgroundScheduler

def iniciar_scheduler():
    scheduler = BackgroundScheduler()
    
    # Programar reporte diario a las 8:00 AM
    scheduler.add_job(
        func=enviar_reporte_diario,
        trigger="cron",
        hour=8,
        minute=0,
        id="reporte_diario"
    )
    
    scheduler.start()

def enviar_reporte_diario():
    """
    Envía reporte automático con tickets del día anterior
    """
    from app.services.reporte_service import generar_reporte_html
    from app.utils import enviar_email
    
    # Tickets creados en las últimas 24 horas
    tickets = obtener_tickets_ultimas_24h()
    
    filtros = {'tipo': 'automático', 'periodo': 'últimas 24 horas'}
    html = generar_reporte_html(tickets, filtros, datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    
    # Enviar a todos los admins
    admins = obtener_emails_admins()
    
    for admin in admins:
        enviar_email(
            destinatario=admin['email'],
            asunto=f"Reporte diario - {datetime.now().strftime('%Y-%m-%d')}",
            contenido_html=html
        )
```

**Opción B: Usando GitHub Actions (gratis, sin servidor)**

Crear archivo `.github/workflows/reporte_diario.yml`:
```yaml
name: Enviar reporte diario

on:
  schedule:
    - cron: '0 8 * * *'  # Todos los días a las 8:00 AM UTC
  workflow_dispatch:  # Para ejecutar manualmente

jobs:
  enviar_reporte:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout código
        uses: actions/checkout@v3
      
      - name: Configurar Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Instalar dependencias
        run: pip install -r requirements.txt
      
      - name: Ejecutar script de reporte
        env:
          MAIL_USERNAME: ${{ secrets.MAIL_USERNAME }}
          MAIL_PASSWORD: ${{ secrets.MAIL_PASSWORD }}
        run: python scripts/enviar_reporte_diario.py
```

## Paso 18: Soft Delete (borrado lógico)

### 18.1 ¿Qué es?

Los tickets no se borran físicamente de la base de datos. Solo se marca un campo `deleted_at` y se ocultan de las vistas normales. Admin puede verlos y restaurarlos.

### 18.2 Modificar tabla tickets
```sql
ALTER TABLE tickets ADD COLUMN deleted_at DATETIME DEFAULT NULL;
ALTER TABLE tickets ADD COLUMN deleted_by INT DEFAULT NULL;
ALTER TABLE tickets ADD FOREIGN KEY (deleted_by) REFERENCES usuarios(id);
```

### 18.3 Funciones para soft delete

**En `app/models.py` o `app/utils.py`:**
```python
def soft_delete_ticket(ticket_id, usuario_id):
    """
    Marca un ticket como eliminado (no lo borra físicamente)
    """
    query = """
        UPDATE tickets 
        SET deleted_at = NOW(), deleted_by = %s 
        WHERE id = %s
    """
    ejecutar_update(query, (usuario_id, ticket_id))

def restaurar_ticket(ticket_id):
    """
    Restaura un ticket eliminado
    """
    query = "UPDATE tickets SET deleted_at = NULL, deleted_by = NULL WHERE id = %s"
    ejecutar_update(query, (ticket_id,))

def obtener_tickets_eliminados():
    """
    Solo para admin: obtiene tickets marcados como eliminados
    """
    query = "SELECT * FROM tickets WHERE deleted_at IS NOT NULL"
    return ejecutar_consulta(query)
```

### 18.4 Modificar consultas normales

Todas las consultas que muestran tickets deben excluir los eliminados:
```sql
SELECT * FROM tickets WHERE deleted_at IS NULL
```

### 18.5 Vista para admin: Papelera

```html
<!-- templates/admin/papelera.html -->
<h2>🗑️ Tickets eliminados</h2>
<table class="table">
    <thead>
        <tr>
            <th>ID</th><th>Título</th><th>Eliminado el</th><th>Acciones</th>
        </tr>
    </thead>
    <tbody>
        {% for ticket in tickets_eliminados %}
        <tr>
            <td>{{ ticket.id }}</td>
            <td>{{ ticket.titulo }}</td>
            <td>{{ ticket.deleted_at }}</td>
            <td>
                <button class="btn btn-sm btn-success btn-restaurar" data-id="{{ ticket.id }}">
                    Restaurar
                </button>
                <button class="btn btn-sm btn-danger btn-borrar-permanente" data-id="{{ ticket.id }}">
                    Borrar definitivamente
                </button>
            </td>
        </tr>
        {% endfor %}
    </tbody>
</table>
```

### 18.6 SweetAlert para confirmar restauración
```js
document.querySelectorAll('.btn-restaurar').forEach(btn => {
    btn.addEventListener('click', async function() {
        const result = await Swal.fire({
            title: '¿Restaurar ticket?',
            text: 'El ticket volverá a aparecer en la lista principal',
            icon: 'question',
            showCancelButton: true,
            confirmButtonText: 'Sí, restaurar'
        });
        
        if (result.isConfirmed) {
            const ticketId = this.dataset.id;
            const response = await fetch(`/admin/ticket/${ticketId}/restaurar`, {
                method: 'POST'
            });
            
            if (response.ok) {
                Swal.fire('Restaurado', 'Ticket restaurado correctamente', 'success');
                location.reload();
            }
        }
    });
});
```

## Paso 19: Búsqueda avanzada en tiempo real

### 19.1 Funcionalidad

Mientras el usuario escribe en un campo de búsqueda, se filtran los tickets sin recargar la página.

### 19.2 HTML del buscador
```html
<div class="mb-3">
    <input type="text" id="buscador" class="form-control" 
           placeholder="🔍 Buscar por ID, título, descripción o cliente...">
</div>
<div id="resultados-busqueda">
    <!-- Aquí se cargan los tickets filtrados -->
</div>
```

### 19.3 JavaScript con fetch
```js
document.getElementById('buscador').addEventListener('input', debounce(async function(e) {
    const termino = e.target.value;
    
    if (termino.length < 2) {
        document.getElementById('resultados-busqueda').innerHTML = '';
        return;
    }
    
    const response = await fetch(`/api/buscar_tickets?q=${encodeURIComponent(termino)}`);
    const tickets = await response.json();
    
    let html = '';
    tickets.forEach(ticket => {
        html += `
            <div class="card mb-2">
                <div class="card-body">
                    <h6>Ticket #${ticket.id} - ${ticket.titulo}</h6>
                    <p>Cliente: ${ticket.cliente_email} | Estado: ${ticket.estado}</p>
                    <a href="/ticket/${ticket.id}" class="btn btn-sm btn-primary">Ver</a>
                </div>
            </div>
        `;
    });
    
    document.getElementById('resultados-busqueda').innerHTML = html || '<p>No se encontraron tickets</p>';
}, 300));

// Función debounce para no hacer muchas peticiones
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func(...args), wait);
    };
}
```

### 19.4 Endpoint de búsqueda en backend
```python
@app.route('/api/buscar_tickets')
@login_requerido
def buscar_tickets():
    termino = request.args.get('q', '')
    usuario_rol = session['rol']
    usuario_id = session['user_id']
    
    query = """
        SELECT t.*, u.email as cliente_email 
        FROM tickets t
        JOIN usuarios u ON t.usuario_id = u.id
        WHERE t.deleted_at IS NULL
        AND (t.titulo LIKE %s OR t.descripcion LIKE %s OR u.email LIKE %s OR t.id LIKE %s)
    """
    like = f"%{termino}%"
    params = [like, like, like, like]
    
    # Si es cliente, solo sus tickets
    if usuario_rol == 'cliente':
        query += " AND t.usuario_id = %s"
        params.append(usuario_id)
    
    tickets = ejecutar_consulta(query, params)
    return jsonify(tickets)
```

## Paso 20: Perfil de usuario y cambio de contraseña

### 20.1 Vista de perfil

```html
<!-- templates/perfil.html -->
<div class="container mt-4">
    <h2>Mi perfil</h2>
    <div class="card">
        <div class="card-body">
            <form id="formPerfil">
                <div class="mb-3">
                    <label>Nombre</label>
                    <input type="text" class="form-control" id="nombre" value="{{ usuario.nombre }}">
                </div>
                <div class="mb-3">
                    <label>Email</label>
                    <input type="email" class="form-control" id="email" value="{{ usuario.email }}">
                </div>
                <button type="submit" class="btn btn-primary">Actualizar perfil</button>
            </form>
            
            <hr>
            
            <h4>Cambiar contraseña</h4>
            <form id="formPassword">
                <div class="mb-3">
                    <label>Contraseña actual</label>
                    <input type="password" class="form-control" id="pass_actual" required>
                </div>
                <div class="mb-3">
                    <label>Nueva contraseña</label>
                    <input type="password" class="form-control" id="pass_nueva" required>
                </div>
                <div class="mb-3">
                    <label>Confirmar nueva contraseña</label>
                    <input type="password" class="form-control" id="pass_confirm" required>
                </div>
                <button type="submit" class="btn btn-warning">Cambiar contraseña</button>
            </form>
        </div>
    </div>
</div>
```

### 20.2 JavaScript con SweetAlert
```js document.getElementById('formPassword').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const nueva = document.getElementById('pass_nueva').value;
    const confirmar = document.getElementById('pass_confirm').value;
    
    if (nueva !== confirmar) {
        Swal.fire('Error', 'Las contraseñas no coinciden', 'error');
        return;
    }
    
    const response = await fetch('/perfil/cambiar_password', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            actual: document.getElementById('pass_actual').value,
            nueva: nueva
        })
    });
    
    const data = await response.json();
    
    if (data.success) {
        Swal.fire('Éxito', 'Contraseña cambiada correctamente', 'success');
        document.getElementById('formPassword').reset();
    } else {
        Swal.fire('Error', data.mensaje, 'error');
    }
});
```

## Paso 21: Despliegue a producción

### 21.1 Preparar archivo `requirements.txt`

```txt
Flask==2.3.0
flask-mysql-connector==1.2.0
bcrypt==4.0.1
APScheduler==3.10.0
mysql-connector-python==8.1.0
python-dotenv==1.0.0
```

### 21.2 Variables de entorno (`.env`)
```env
SECRET_KEY=tu_clave_secreta_muy_larga_aleatoria
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=tu_contraseña
DB_NAME=ticket_system
MAIL_USERNAME=tu_correo@gmail.com
MAIL_PASSWORD=tu_app_password
```

### 21.3 Opciones de hosting gratis
# Plataformas de despliegue

| Plataforma       | ¿Gratis?            | ¿MySQL?              | ¿Tareas programadas? | Dificultad |
|------------------|---------------------|----------------------|----------------------|------------|
| PythonAnywhere   | ✅                  | ✅ (limitado)        | ❌                   | Baja       |
| Render           | ✅                  | ✅ (90 días)         | ✅ (cron)            | Media      |
| Railway          | ✅ ($5 crédito)     | ✅                   | ✅                   | Baja       |
| Koyeb            | ✅                  | ✅                   | ✅                   | Media      |
| VPS Propio       | ❌ (pagas)          | ✅                   | ✅                   | Alta       |

**Recomendación para empezar: PythonAnywhere** (más fácil)

### 21.4 Desplegar en PythonAnywhere (pasos)

1. Crear cuenta en [pythonanywhere.com](https://pythonanywhere.com/)
    
2. Subir código por Git o Web UI
    
3. Crear base de datos MySQL desde el panel
    
4. Configurar WSGI: apuntar a tu `app/__init__.py`
    
5. Ejecutar script SQL para crear tablas
    
6. Configurar variables de entorno
    
7. Probar la app
    

### 21.5 Desplegar en Railway (recomendado para CV)

1. Subir código a GitHub
    
2. Crear cuenta en railway.app
    
3. "Deploy from GitHub repo"
    
4. Añadir MySQL plugin
    
5. Configurar variables de entorno
    
6. Railway genera una URL pública automáticamente
    

---

## Paso 22: Documentación final para GitHub

### 22.1 Estructura del README.md
```markdown
# 🎫 Sistema de Tickets HelpDesk

Sistema completo de gestión de tickets de soporte construido con Flask, MySQL, Bootstrap y SweetAlert.

## ✨ Características

- **Tres roles:** Cliente, Agente, Administrador
- **Gestión de tickets:** Crear, responder, cambiar estado, asignar prioridad
- **Asignación de agentes:** Manual o automática
- **Reportes por email:** Diarios y bajo demanda
- **Soft delete:** Recuperación de tickets eliminados
- **Búsqueda en tiempo real**
- **Interfaz responsive** con Bootstrap 5
- **Alertas y modales** con SweetAlert2

## 🚀 Tecnologías

- Backend: Flask (Python)
- Base de datos: MySQL
- Frontend: Bootstrap 5, SweetAlert2, Fetch API
- Email: SMTP

## 📸 Capturas de pantalla

[Agrega imágenes aquí]

## 🛠️ Instalación local

```bash
git clone https://github.com/tuusuario/ticket-system.git
cd ticket-system
pip install -r requirements.txt
python run.py
```

## 📊 Diagrama de base de datos

[Agrega diagrama]

## 📧 Envío de reportes

Configurar variables de entorno en `.env`

## 👤 Roles y permisos
# Roles y permisos principales

| Rol     | Permisos principales                                                                 |
|---------|---------------------------------------------------------------------------------------|
| Cliente | Crear tickets, ver sus tickets, responder, cancelar (30 min)                          |
| Agente  | Ver todos, asignarse, cambiar estado/prioridad, responder                             |
| Admin   | Todo lo anterior + gestionar agentes, reportes, papelera                              |

## 🧪 Pruebas

Credenciales de prueba:

- Admin: admin@ticketsystem.com / admin123
    
- Agente: agente@ticketsystem.com / agente123
    
- Cliente: cliente@ticketsystem.com / cliente123
    

## 📄 Licencia

MIT
```txt

### 22.2 Archivo `.gitignore`

```gitignore
venv/
__pycache__/
*.pyc
.env
*.db
.DS_Store
*.sql
*.log
```

### 22.3 Crear badge de estado en README
```markdown
![Estado del despliegue](https://img.shields.io/badge/deploy-success-brightgreen)
![Versión](https://img.shields.io/badge/version-1.0-blue)
![Python](https://img.shields.io/badge/python-3.10+-blue)
```
## Paso 23: Testing y validación final

### 23.1 Lista de verificación antes de desplegar

- Registro de usuario funciona y crea cliente
    
- Login funciona y redirige según rol
    
- Cliente puede crear ticket (sin prioridad)
    
- Cliente solo ve sus tickets
    
- Cliente puede cancelar ticket en menos de 30 min
    
- Agente puede ver todos los tickets
    
- Modal de gestión asigna prioridad + estado correctamente
    
- Después de asignar, aparecen botones de acción
    
- Botón "Responder" con SweetAlert funciona
    
- Botón "Cambiar estado" actualiza y guarda log
    
- Admin puede ver panel de reportes
    
- Reporte por email llega correctamente
    
- Soft delete funciona (ticket desaparece de listados)
    
- Admin puede restaurar desde papelera
    
- Búsqueda en tiempo real funciona
    
- Cambio de contraseña funciona
    
- La app es responsive en móvil
    
- README.md está completo
    
- Repositorio GitHub es público
    

---