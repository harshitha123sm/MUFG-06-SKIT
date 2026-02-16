from datetime import datetime

from werkzeug.security import check_password_hash, generate_password_hash

from . import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='resident')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    bookings = db.relationship('Booking', backref='resident', lazy=True)

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)


class Tower(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    address = db.Column(db.String(255), nullable=False)

    units = db.relationship('Unit', backref='tower', lazy=True)


unit_amenity = db.Table(
    'unit_amenity',
    db.Column('unit_id', db.Integer, db.ForeignKey('unit.id'), primary_key=True),
    db.Column('amenity_id', db.Integer, db.ForeignKey('amenity.id'), primary_key=True),
)


class Unit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tower_id = db.Column(db.Integer, db.ForeignKey('tower.id'), nullable=False)
    number = db.Column(db.String(30), nullable=False)
    bedrooms = db.Column(db.Integer, nullable=False)
    rent = db.Column(db.Numeric(10, 2), nullable=False)
    occupied = db.Column(db.Boolean, default=False)

    amenities = db.relationship('Amenity', secondary=unit_amenity, lazy='subquery')
    bookings = db.relationship('Booking', backref='unit', lazy=True)


class Amenity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), nullable=False, unique=True)
    description = db.Column(db.String(255), nullable=True)


class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    unit_id = db.Column(db.Integer, db.ForeignKey('unit.id'), nullable=False)
    resident_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    move_in_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default='pending')
    mock_payment_status = db.Column(db.String(20), default='unpaid')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
