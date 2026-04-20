"""
User API Routes — CropGuard AI
All responses return JSON for the React frontend.

Endpoints:
  POST /api/predict          — Upload image, get prediction
  GET  /api/result/<id>      — Get single prediction by ID
  GET  /api/history          — Logged-in user's prediction history
  GET  /api/uploads/<fname>  — Serve uploaded images
  GET  /api/alerts           — User's in-app notifications
  POST /api/alerts/read      — Mark all alerts as read
"""

import os
import json
import uuid
from flask import Blueprint, request, jsonify, send_from_directory, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from database.db_models import db, Prediction, Alert
from model.preprocess import allowed_file, validate_leaf_image

user_bp = Blueprint('user', __name__)


# ── Serve uploaded images ─────────────────────────────────────────────────────
@user_bp.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)


# ── Prediction ────────────────────────────────────────────────────────────────
@user_bp.route('/predict', methods=['POST'])
def predict():
    """
    POST /api/predict
    Body: multipart/form-data  { leaf_image: File }
    Returns: JSON prediction result
    """
    if 'leaf_image' not in request.files:
        return jsonify({'error': 'No image file provided. Use key: leaf_image'}), 400

    file = request.files['leaf_image']
    if not file.filename:
        return jsonify({'error': 'Empty filename'}), 400
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Use JPG, PNG, or WEBP.'}), 400

    # Save file
    ext         = file.filename.rsplit('.', 1)[1].lower()
    unique_name = f"{uuid.uuid4().hex}.{ext}"
    save_path   = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_name)
    file.save(save_path)

    # Validate
    valid, msg = validate_leaf_image(save_path)
    if not valid:
        os.remove(save_path)
        return jsonify({'error': f'Image validation failed: {msg}'}), 400

    # Run prediction
    try:
        from model.predict import predict as run_predict
        result = run_predict(save_path)
    except FileNotFoundError:
        return jsonify({'error': 'Model not trained yet. Ask admin to run training first.'}), 503
    except Exception as e:
        current_app.logger.error(f"Prediction error: {e}")
        return jsonify({'error': 'Prediction failed. Please try again.'}), 500

    # Save to DB
    pred = Prediction(
        user_id         = current_user.id if current_user.is_authenticated else None,
        image_filename  = unique_name,
        original_name   = secure_filename(file.filename),
        crop_type       = result['crop_type'],
        disease_name    = result['disease_name'],
        is_healthy      = result['is_healthy'],
        confidence      = result['confidence'],
        top3_results    = json.dumps(result['top3']),
        recommendation  = result['recommendation'],
        processing_time = result['processing_time'],
        alert_sent      = False,
    )
    db.session.add(pred)
    db.session.commit()

    # ── Fire alert if disease detected with high confidence ───────────────────
    if (not result['is_healthy']
            and current_user.is_authenticated
            and result['confidence'] >= current_app.config.get('ALERT_CONFIDENCE_THRESHOLD', 0.80)):
        try:
            from notifications.alerts import send_disease_alert, log_alert
            # In-app notification (always)
            log_alert(
                user_id=current_user.id,
                disease_name=result['disease_name'],
                crop_type=result['crop_type'],
                confidence=result['confidence'],
                prediction_id=pred.id
            )
            # Email alert (only if mail configured)
            sent = send_disease_alert(
                user_email=current_user.email,
                user_name=current_user.username,
                disease_name=result['disease_name'],
                crop_type=result['crop_type'],
                confidence=result['confidence'],
                recommendation=result['recommendation'],
                prediction_id=pred.id
            )
            pred.alert_sent = sent
            db.session.commit()
        except Exception as e:
            current_app.logger.warning(f"Alert error (non-fatal): {e}")

    return jsonify({**pred.to_dict(), **{'low_confidence': result.get('low_confidence', False)}}), 201


# ── Single result ─────────────────────────────────────────────────────────────
@user_bp.route('/result/<int:prediction_id>', methods=['GET'])
def get_result(prediction_id):
    pred = Prediction.query.get_or_404(prediction_id)
    return jsonify(pred.to_dict()), 200


# ── User history ──────────────────────────────────────────────────────────────
@user_bp.route('/history', methods=['GET'])
@login_required
def history():
    preds = (Prediction.query
             .filter_by(user_id=current_user.id)
             .order_by(Prediction.created_at.desc())
             .all())
    return jsonify([p.to_dict() for p in preds]), 200


# ── Alerts / Notifications ────────────────────────────────────────────────────
@user_bp.route('/alerts', methods=['GET'])
@login_required
def get_alerts():
    alerts = (Alert.query
              .filter_by(user_id=current_user.id)
              .order_by(Alert.created_at.desc())
              .limit(20)
              .all())
    unread = Alert.query.filter_by(user_id=current_user.id, is_read=False).count()
    return jsonify({'alerts': [a.to_dict() for a in alerts], 'unread': unread}), 200


@user_bp.route('/alerts/read', methods=['POST'])
@login_required
def mark_read():
    from notifications.alerts import mark_alerts_read
    mark_alerts_read(current_user.id)
    return jsonify({'status': 'ok'}), 200
