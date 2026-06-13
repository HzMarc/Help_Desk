from datetime import datetime

def generar_reporte_html(datos_reporte):
    """
    Genera el HTML para el reporte que será enviado por correo.
    """
    fecha_actual = datetime.now().strftime('%d de %B de %Y')
    
    html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f7f6; color: #333; margin: 0; padding: 20px; }}
            .container {{ max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
            .header {{ background-color: #1C3166; color: white; padding: 20px; text-align: center; }}
            .content {{ padding: 30px; }}
            h1 {{ margin: 0; font-size: 24px; }}
            .stats-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-top: 20px; }}
            .stat-box {{ background: #f8f9fa; border-left: 4px solid #00B5C9; padding: 15px; border-radius: 4px; }}
            .stat-value {{ font-size: 28px; font-weight: bold; color: #1C3166; margin-bottom: 5px; }}
            .stat-label {{ font-size: 14px; color: #6c757d; text-transform: uppercase; letter-spacing: 1px; }}
            .footer {{ background-color: #f8f9fa; text-align: center; padding: 15px; font-size: 12px; color: #6c757d; border-top: 1px solid #e9ecef; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Reporte de Sistema HelpDesk</h1>
                <p>Resumen de Tickets - {fecha_actual}</p>
            </div>
            
            <div class="content">
                <p>Hola Administrador,</p>
                <p>Aquí tienes el estado actual de los tickets en la plataforma:</p>
                
                <div style="text-align: center; margin: 30px 0;">
                    <div style="font-size: 48px; font-weight: bold; color: #1C3166;">{datos_reporte.get('total', 0)}</div>
                    <div style="color: #6c757d; text-transform: uppercase; font-weight: bold;">Total Histórico</div>
                </div>
                
                <div class="stats-grid">
                    <div class="stat-box" style="border-color: #0d6efd;">
                        <div class="stat-value">{datos_reporte.get('abiertos', 0)}</div>
                        <div class="stat-label">Abiertos</div>
                    </div>
                    <div class="stat-box" style="border-color: #ffc107;">
                        <div class="stat-value">{datos_reporte.get('en_progreso', 0)}</div>
                        <div class="stat-label">En Progreso</div>
                    </div>
                    <div class="stat-box" style="border-color: #198754;">
                        <div class="stat-value">{datos_reporte.get('resueltos', 0)}</div>
                        <div class="stat-label">Resueltos</div>
                    </div>
                    <div class="stat-box" style="border-color: #6c757d;">
                        <div class="stat-value">{datos_reporte.get('cerrados', 0)}</div>
                        <div class="stat-label">Cerrados</div>
                    </div>
                </div>
            </div>
            
            <div class="footer">
                <p>Este es un mensaje automático del sistema. Por favor no responda a este correo.</p>
                <p>&copy; {datetime.now().year} Sistema HelpDesk Automático.</p>
            </div>
        </div>
    </body>
    </html>
    """
    return html
