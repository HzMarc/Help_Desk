from functools import wraps
from flask import session, redirect, url_for, flash

def login_requerido(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            # flash('Por favor, inicia sesión para acceder a esta página.', 'warning')
            return redirect(url_for('main.login'))
        return f(*args, **kwargs)
    return decorated_function

def rol_requerido(*roles_permitidos):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                return redirect(url_for('main.login'))
            
            rol_actual = session.get('rol')
            if rol_actual == 'admin':
                # admin siempre puede hacer todo
                return f(*args, **kwargs)
                
            if rol_actual not in roles_permitidos:
                # flash('No tienes permisos para realizar esta acción.', 'danger')
                return redirect(url_for('main.index'))
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# ==================== UTILIDADES DE CORREO ====================
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app

def enviar_email(destinatario, asunto, cuerpo_html):
    """
    Envía un correo electrónico utilizando la configuración SMTP actual.
    """
    # Usar current_app para acceder a la configuración
    remitente = current_app.config['MAIL_USERNAME']
    password = current_app.config['MAIL_PASSWORD']
    servidor = current_app.config['MAIL_SERVER']
    puerto = current_app.config['MAIL_PORT']

    msg = MIMEMultipart()
    msg['From'] = remitente
    msg['To'] = destinatario
    msg['Subject'] = asunto

    msg.attach(MIMEText(cuerpo_html, 'html'))

    try:
        server = smtplib.SMTP(servidor, puerto)
        server.starttls()
        server.login(remitente, password)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Error al enviar correo: {e}")
        return False
