"""
Auth API Routes — CropGuard AI
POST /api/auth/login
POST /api/auth/register
POST /api/auth/logout
GET  /api/auth/me
"""

from flask import Blueprint, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from database.db_models import db, User

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['POST'])
def login():
    data     = request.get_json() or {}
    username = data.get('username','').strip()
    password = data.get('password','')
    remember = data.get('remember', False)

    user = User.query.filter_by(username=username).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({'error': 'Invalid username or password'}), 401
    if not user.is_active:
        return jsonify({'error': 'Account is disabled. Contact admin.'}), 403

    login_user(user, remember=remember)
    return jsonify({
        'message': 'Login successful',
        'user': {
            'id':       user.id,
            'username': user.username,
            'email':    user.email,
            'role':     user.role,
        }
    }), 200


@auth_bp.route('/register', methods=['POST'])
def register():
    data     = request.get_json() or {}
    username = data.get('username','').strip()
    email    = data.get('email','').strip().lower()
    password = data.get('password','')

    if len(username) < 3:
        return jsonify({'error': 'Username must be at least 3 characters'}), 400
    if len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters'}), 400
    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Username already taken'}), 409
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already registered'}), 409

    user = User(
        username=username, email=email,
        password_hash=generate_password_hash(password),
        role='user'
    )
    db.session.add(user)
    db.session.commit()
    login_user(user)

    return jsonify({
        'message': 'Account created successfully',
        'user': {'id': user.id, 'username': user.username,
                 'email': user.email, 'role': user.role}
    }), 201


@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'Logged out successfully'}), 200


@auth_bp.route('/me', methods=['GET'])
def me():
    if current_user.is_authenticated:
        return jsonify({
            'authenticated': True,
            'user': {
                'id':       current_user.id,
                'username': current_user.username,
                'email':    current_user.email,
                'role':     current_user.role,
            }
        }), 200
    return jsonify({'authenticated': False, 'user': None}), 200
