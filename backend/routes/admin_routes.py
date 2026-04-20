"""
Admin API Routes — CropGuard AI
All responses return JSON for the React frontend.
All routes require admin role.

Endpoints:
  GET  /api/admin/dashboard   — Stats + trend + disease breakdown
  GET  /api/admin/predictions — Paginated prediction log
  GET  /api/admin/dataset     — Dataset entries + label counts
  POST /api/admin/dataset/upload
  GET  /api/admin/train       — Model training history
  POST /api/admin/train/start
  GET  /api/admin/users       — All users
  GET  /api/admin/stats       — Live stats (for auto-refresh)
"""

import os
import json
from functools import wraps
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from sqlalchemy import func

from database.db_models import db, User, Prediction, DatasetEntry, ModelMetrics

admin_bp = Blueprint('admin', __name__)


def admin_required(f):
    @wraps(f)
    @login_required
    def decorated(*args, **kwargs):
        if not current_user.is_admin:
            return jsonify({'error': 'Admin access required'}), 403
        return f(*args, **kwargs)
    return decorated


# ── Dashboard ─────────────────────────────────────────────────────────────────
@admin_bp.route('/dashboard', methods=['GET'])
@admin_required
def dashboard():
    total   = Prediction.query.count()
    diseased= Prediction.query.filter_by(is_healthy=False).count()
    healthy = Prediction.query.filter_by(is_healthy=True).count()
    users   = User.query.count()
    avg_c   = db.session.query(func.avg(Prediction.confidence)).scalar() or 0

    today = datetime.utcnow().date()
    today_count = Prediction.query.filter(
        func.date(Prediction.created_at) == today).count()

    # 7-day trend
    trend = []
    for i in range(6, -1, -1):
        day = datetime.utcnow().date() - timedelta(days=i)
        h = Prediction.query.filter(
            func.date(Prediction.created_at)==day, Prediction.is_healthy==True).count()
        d = Prediction.query.filter(
            func.date(Prediction.created_at)==day, Prediction.is_healthy==False).count()
        trend.append({'date': day.strftime('%b %d'), 'healthy': h, 'diseased': d})

    # Disease breakdown top-8
    disease_counts = (db.session
        .query(Prediction.disease_name, func.count(Prediction.id).label('cnt'))
        .filter(Prediction.is_healthy==False)
        .group_by(Prediction.disease_name)
        .order_by(func.count(Prediction.id).desc())
        .limit(8).all())

    # Recent 10
    recent = (Prediction.query
              .order_by(Prediction.created_at.desc())
              .limit(10).all())

    active_model = ModelMetrics.query.filter_by(is_active=True).first()

    return jsonify({
        'metrics': {
            'total': total, 'diseased': diseased, 'healthy': healthy,
            'users': users, 'avg_confidence': round(avg_c*100, 1),
            'today': today_count,
        },
        'trend':          trend,
        'disease_counts': [{'name': r[0], 'count': r[1]} for r in disease_counts],
        'recent':         [p.to_dict() for p in recent],
        'active_model':   active_model.to_dict() if active_model else None,
    }), 200


# ── Live stats ────────────────────────────────────────────────────────────────
@admin_bp.route('/stats', methods=['GET'])
@admin_required
def stats():
    total   = Prediction.query.count()
    today   = datetime.utcnow().date()
    t_count = Prediction.query.filter(func.date(Prediction.created_at)==today).count()
    avg_c   = db.session.query(func.avg(Prediction.confidence)).scalar() or 0
    return jsonify({'total': total, 'today': t_count,
                    'avg_confidence': round(avg_c*100,1)}), 200


# ── Predictions ───────────────────────────────────────────────────────────────
@admin_bp.route('/predictions', methods=['GET'])
@admin_required
def predictions():
    page     = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    crop     = request.args.get('crop', '')
    status   = request.args.get('status', '')

    query = Prediction.query
    if crop:   query = query.filter(Prediction.crop_type.ilike(f'%{crop}%'))
    if status == 'healthy':  query = query.filter_by(is_healthy=True)
    if status == 'diseased': query = query.filter_by(is_healthy=False)

    pag = query.order_by(Prediction.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False)

    return jsonify({
        'predictions': [p.to_dict() for p in pag.items],
        'total':       pag.total,
        'pages':       pag.pages,
        'current_page':pag.page,
    }), 200


# ── Dataset ───────────────────────────────────────────────────────────────────
@admin_bp.route('/dataset', methods=['GET'])
@admin_required
def dataset():
    entries = DatasetEntry.query.order_by(DatasetEntry.created_at.desc()).all()
    counts  = (db.session.query(DatasetEntry.label, func.count(DatasetEntry.id))
               .group_by(DatasetEntry.label).all())
    return jsonify({
        'entries':      [e.to_dict() for e in entries],
        'label_counts': [{'label': r[0], 'count': r[1]} for r in counts],
        'total':        len(entries),
    }), 200


@admin_bp.route('/dataset/upload', methods=['POST'])
@admin_required
def upload_dataset():
    from werkzeug.utils import secure_filename
    import uuid as _uuid

    label = request.form.get('label','').strip()
    split = request.form.get('split', 'train')
    if not label:
        return jsonify({'error': 'Label is required'}), 400

    files = request.files.getlist('images')
    count = 0
    for f in files:
        if f and f.filename:
            ext  = f.filename.rsplit('.','1')[-1].lower()
            name = f"{_uuid.uuid4().hex}.{ext}"
            f.save(os.path.join(current_app.config['UPLOAD_FOLDER'], name))
            e = DatasetEntry(
                filename=name, label=label,
                crop_type=label.split('___')[0] if '___' in label else label,
                split=split, uploaded_by=current_user.id)
            db.session.add(e)
            count += 1

    db.session.commit()
    return jsonify({'message': f'Uploaded {count} images', 'count': count}), 201


# ── Training ──────────────────────────────────────────────────────────────────
@admin_bp.route('/train', methods=['GET'])
@admin_required
def train_history():
    models = ModelMetrics.query.order_by(ModelMetrics.trained_at.desc()).all()
    return jsonify({'models': [m.to_dict() for m in models]}), 200


@admin_bp.route('/train/start', methods=['POST'])
@admin_required
def start_training():
    data       = request.get_json() or {}
    data_dir   = data.get('data_dir','').strip()
    model_type = data.get('model_type','mobilenet')
    epochs     = int(data.get('epochs', 30))
    batch_size = int(data.get('batch_size', 32))

    if not data_dir or not os.path.isdir(data_dir):
        return jsonify({'error': 'Invalid dataset directory path'}), 400

    # In production: queue this with Celery/RQ
    # For now return task info
    return jsonify({
        'message': 'Training queued. Run from terminal for now.',
        'command': f"python model/train.py --data_dir {data_dir} --model_type {model_type} --epochs {epochs} --batch_size {batch_size}",
    }), 202


# ── Users ─────────────────────────────────────────────────────────────────────
@admin_bp.route('/users', methods=['GET'])
@admin_required
def users():
    all_users = User.query.order_by(User.created_at.desc()).all()
    return jsonify({'users': [u.to_dict() for u in all_users]}), 200


@admin_bp.route('/users/<int:user_id>/toggle', methods=['POST'])
@admin_required
def toggle_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        return jsonify({'error': 'Cannot deactivate yourself'}), 400
    user.is_active = not user.is_active
    db.session.commit()
    return jsonify({'message': f'User {"activated" if user.is_active else "deactivated"}',
                    'is_active': user.is_active}), 200
