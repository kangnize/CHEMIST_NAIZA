from flask import Flask
from flask_mysqldb import MySQL
from dotenv import load_dotenv

import os

app = Flask(__name__)
load_dotenv()

# MySQL Configuration
app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB')
app.secret_key = os.getenv('SECRET_KEY')

mysql = MySQL(app)

if __name__ == '__main__':
    from auth import auth_bp
    from products import products_bp
    from dashboard import dashboard_bp

    # Register routes
    # app.register_blueprint(auth_bp, url_prefix='/auth')
    # app.register_blueprint(products_bp, url_prefix='/products')

    app.register_blueprint(auth_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(dashboard_bp)

    app.run(debug=True)
