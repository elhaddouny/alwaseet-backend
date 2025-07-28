from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from src.models.user import db

class Craftsman(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    service_type = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    experience_years = db.Column(db.Integer, default=0)
    rating = db.Column(db.Float, default=0.0)
    reviews_count = db.Column(db.Integer, default=0)
    completed_jobs = db.Column(db.Integer, default=0)
    price_range = db.Column(db.String(50))
    availability = db.Column(db.String(200))
    is_verified = db.Column(db.Boolean, default=False)
    profile_image = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    services = db.relationship('CraftsmanService', backref='craftsman', lazy=True, cascade='all, delete-orphan')
    portfolio = db.relationship('PortfolioItem', backref='craftsman', lazy=True, cascade='all, delete-orphan')
    reviews = db.relationship('Review', backref='craftsman', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Craftsman {self.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'service_type': self.service_type,
            'location': self.location,
            'description': self.description,
            'experience_years': self.experience_years,
            'rating': self.rating,
            'reviews_count': self.reviews_count,
            'completed_jobs': self.completed_jobs,
            'price_range': self.price_range,
            'availability': self.availability,
            'is_verified': self.is_verified,
            'profile_image': self.profile_image,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class CraftsmanService(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    craftsman_id = db.Column(db.Integer, db.ForeignKey('craftsman.id'), nullable=False)
    service_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.String(50))

    def to_dict(self):
        return {
            'id': self.id,
            'service_name': self.service_name,
            'description': self.description,
            'price': self.price
        }

class PortfolioItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    craftsman_id = db.Column(db.Integer, db.ForeignKey('craftsman.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    image_url = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'image_url': self.image_url,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    craftsman_id = db.Column(db.Integer, db.ForeignKey('craftsman.id'), nullable=False)
    customer_name = db.Column(db.String(100), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'customer_name': self.customer_name,
            'rating': self.rating,
            'comment': self.comment,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

