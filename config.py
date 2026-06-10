import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'super-secret-key-helpdesk'
    
    # DB configuration placeholders
    DB_HOST = os.environ.get('DB_HOST') or '127.0.0.1'
    DB_USER = os.environ.get('DB_USER') or 'root'
    DB_PASSWORD = os.environ.get('DB_PASSWORD') or ''
    DB_NAME = os.environ.get('DB_NAME') or 'helpdesk_db'
    DB_PORT = os.environ.get('DB_PORT') or 3308
