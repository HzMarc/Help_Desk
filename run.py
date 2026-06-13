from app import create_app, get_db_connection
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from app.models import obtener_reportes_basicos, obtener_todos_agentes
from app.utils import enviar_email
from app.services.reporte_service import generar_reporte_html

app = create_app()

def enviar_reporte_diario():
    with app.app_context():
        conn = get_db_connection(app)
        if not conn:
            return
        
        reportes = obtener_reportes_basicos(conn)
        agentes = obtener_todos_agentes(conn)
        conn.close()
        
        html_cuerpo = generar_reporte_html(reportes)
        asunto = f"Reporte Diario de Estado HelpDesk - {datetime.now().strftime('%d/%m/%Y')}"
        
        # Enviar a todos los administradores
        for u in agentes:
            if u['rol'] == 'admin' and u['email']:
                enviar_email(u['email'], asunto, html_cuerpo)

# Configurar planificador
scheduler = BackgroundScheduler()
# Tarea diaria a las 08:00 AM
scheduler.add_job(func=enviar_reporte_diario, trigger="cron", hour=8, minute=0)
scheduler.start()

# Opcional: Enviar un correo justo al arrancar la app por primera vez (para demostración de que funciona)
import os
if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
    # Esto previene que se ejecute dos veces en el auto-reload de Flask
    print("Iniciando APScheduler...")
    # Puedes descomentar la siguiente línea para enviar un email instantáneo al encender el servidor:
    # scheduler.add_job(func=enviar_reporte_diario, trigger="date", run_date=datetime.now())

if __name__ == '__main__':
    app.run(debug=True)
