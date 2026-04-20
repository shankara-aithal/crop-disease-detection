"""
Database Models — CropGuard AI
Tables: User, Prediction, DatasetEntry, ModelMetrics, Alert
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(80),  unique=True, nullable=False)
    email         = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role          = db.Column(db.String(20),  default='user')
    created_at    = db.Column(db.DateTime,    default=datetime.utcnow)
    is_active     = db.Column(db.Boolean,     default=True)

    predictions   = db.relationship('Prediction', backref='user',  lazy=True)
    alerts        = db.relationship('Alert',      backref='user',  lazy=True)

    @property
    def is_admin(self):
        return self.role == 'admin'

    def to_dict(self):
        return {
            'id':         self.id,
            'username':   self.username,
            'email':      self.email,
            'role':       self.role,
            'created_at': self.created_at.strftime('%Y-%m-%d'),
            'is_active':  self.is_active,
            'pred_count': len(self.predictions),
        }


class Prediction(db.Model):
    __tablename__ = 'predictions'
    id              = db.Column(db.Integer, primary_key=True)
    user_id         = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    image_filename  = db.Column(db.String(255), nullable=False)
    original_name   = db.Column(db.String(255))
    crop_type       = db.Column(db.String(100))
    disease_name    = db.Column(db.String(200), nullable=False)
    is_healthy      = db.Column(db.Boolean, default=False)
    confidence      = db.Column(db.Float,   nullable=False)
    top3_results    = db.Column(db.Text)
    recommendation  = db.Column(db.Text)
    processing_time = db.Column(db.Float)
    alert_sent      = db.Column(db.Boolean, default=False)
    created_at      = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        import json
        return {
            'id':             self.id,
            'image_url':      f'/api/uploads/{self.image_filename}',
            'crop_type':      self.crop_type,
            'disease_name':   self.disease_name,
            'is_healthy':     self.is_healthy,
            'confidence':     round(self.confidence * 100, 1),
            'top3':           json.loads(self.top3_results) if self.top3_results else [],
            'recommendation': self.recommendation,
            'processing_time':self.processing_time,
            'alert_sent':     self.alert_sent,
            'created_at':     self.created_at.strftime('%Y-%m-%d %H:%M'),
        }


class Alert(db.Model):
    __tablename__ = 'alerts'
    id            = db.Column(db.Integer, primary_key=True)
    user_id       = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    disease_name  = db.Column(db.String(200))
    crop_type     = db.Column(db.String(100))
    confidence    = db.Column(db.Float)
    prediction_id = db.Column(db.Integer, db.ForeignKey('predictions.id'))
    message       = db.Column(db.Text)
    is_read       = db.Column(db.Boolean, default=False)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id':            self.id,
            'message':       self.message,
            'is_read':       self.is_read,
            'prediction_id': self.prediction_id,
            'created_at':    self.created_at.strftime('%Y-%m-%d %H:%M'),
        }


class DatasetEntry(db.Model):
    __tablename__ = 'dataset_entries'
    id          = db.Column(db.Integer, primary_key=True)
    filename    = db.Column(db.String(255), nullable=False)
    label       = db.Column(db.String(200), nullable=False)
    crop_type   = db.Column(db.String(100))
    split       = db.Column(db.String(20), default='train')
    uploaded_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id, 'filename': self.filename,
            'label': self.label, 'split': self.split,
            'created_at': self.created_at.strftime('%Y-%m-%d'),
        }


class ModelMetrics(db.Model):
    __tablename__ = 'model_metrics'
    id             = db.Column(db.Integer, primary_key=True)
    model_version  = db.Column(db.String(50), nullable=False)
    train_accuracy = db.Column(db.Float)
    val_accuracy   = db.Column(db.Float)
    train_loss     = db.Column(db.Float)
    val_loss       = db.Column(db.Float)
    epochs         = db.Column(db.Integer)
    dataset_size   = db.Column(db.Integer)
    notes          = db.Column(db.Text)
    trained_at     = db.Column(db.DateTime, default=datetime.utcnow)
    is_active      = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return {
            'id':            self.id,
            'model_version': self.model_version,
            'train_accuracy':round((self.train_accuracy or 0)*100, 2),
            'val_accuracy':  round((self.val_accuracy or 0)*100, 2),
            'epochs':        self.epochs,
            'is_active':     self.is_active,
            'trained_at':    self.trained_at.strftime('%Y-%m-%d'),
        }
