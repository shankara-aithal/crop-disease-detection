"""
CropGuard AI — Flask Backend
BCA AIML Final Year Project


Serves as a REST API for the React frontend.
Run: python app.py
API base: http://localhost:5000/api
"""


from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_cors import CORS
from flask_mail import Mail
from config import Config
from database.db_models import db, User
import os


login_manager = LoginManager()
mail = Mail()



def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    @app.route("/")
    def home():
        return "Server is running"

    # ── Extensions ────────────────────────────────────────────────────────────
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)


    # Allow React dev server (port 3000) and production build
    CORS(app, origins=[
        "http://localhost:3000",   # React dev server
        "http://localhost:5173",   # Vite dev server
        "http://127.0.0.1:3000",
    ], supports_credentials=True)


    # Ensure upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


    # ── Blueprints ────────────────────────────────────────────────────────────
    from routes.user_routes  import user_bp
    from routes.admin_routes import admin_bp
    from routes.auth_routes  import auth_bp


    app.register_blueprint(user_bp,  url_prefix='/api')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(auth_bp,  url_prefix='/api/auth')


    # ── DB Init ───────────────────────────────────────────────────────────────
    with app.app_context():
        db.create_all()
        _seed_admin(app)


    return app



@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))



def _seed_admin(app):
    with app.app_context():
        if not User.query.filter_by(role='admin').first():
            from werkzeug.security import generate_password_hash
            admin = User(
                username='admin',
                email='admin@cropguard.ai',
                password_hash=generate_password_hash('Admin@123'),
                role='admin'
            )
            db.session.add(admin)
            db.session.commit()
            print("[SEED] Admin created  →  admin / Admin@123")

    
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)