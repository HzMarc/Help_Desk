from flask import Flask
from flask_bcrypt import Bcrypt
from config import Config
import mysql.connector
from mysql.connector import Error

bcrypt = Bcrypt()

def get_db_connection(app_instance):
    try:
        connection = mysql.connector.connect(
            host=app_instance.config['DB_HOST'],
            user=app_instance.config['DB_USER'],
            password=app_instance.config['DB_PASSWORD'],
            database=app_instance.config['DB_NAME'],
            port=app_instance.config['DB_PORT']
        )
        return connection
    except Error as e:
        print(f"Error conectando a MySQL: {e}")
        return None

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    bcrypt.init_app(app)

    # Registro de rutas principales
    from app.routes import main
    app.register_blueprint(main)

    return app
