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
