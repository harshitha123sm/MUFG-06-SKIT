from datetime import date
from decimal import Decimal

from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required

from . import db
from .models import Amenity, Booking, Tower, Unit, User


api_bp = Blueprint('api', __name__)


def user_payload(user: User):
    return {
        'id': user.id,
        'name': user.name,
        'email': user.email,
        'role': user.role,
    }


def unit_payload(unit: Unit):
    return {
        'id': unit.id,
        'tower': unit.tower.name,
        'number': unit.number,
        'bedrooms': unit.bedrooms,
        'rent': float(unit.rent),
        'occupied': unit.occupied,
        'amenities': [amenity.name for amenity in unit.amenities],
    }


def booking_payload(booking: Booking):
    return {
        'id': booking.id,
        'unit_id': booking.unit_id,
        'unit_number': booking.unit.number,
        'resident': booking.resident.name,
        'resident_email': booking.resident.email,
        'move_in_date': booking.move_in_date.isoformat(),
        'status': booking.status,
        'mock_payment_status': booking.mock_payment_status,
        'created_at': booking.created_at.isoformat(),
    }


@api_bp.post('/auth/register')
def register():
    data = request.get_json() or {}
    required_fields = {'name', 'email', 'password'}
    if not required_fields.issubset(data):
        return jsonify({'message': 'Missing required registration fields'}), 400

    existing = User.query.filter_by(email=data['email'].lower()).first()
    if existing:
        return jsonify({'message': 'Email already registered'}), 409

    user = User(
        name=data['name'],
        email=data['email'].lower(),
        role=data.get('role', 'resident'),
    )
    user.set_password(data['password'])
    db.session.add(user)
    db.session.commit()

    return jsonify({'user': user_payload(user)}), 201


@api_bp.post('/auth/login')
def login():
    data = request.get_json() or {}
    email = data.get('email', '').lower()
    password = data.get('password', '')

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({'message': 'Invalid credentials'}), 401

    access_token = create_access_token(
        identity=str(user.id),
        additional_claims={'role': user.role},
    )
    return jsonify({'access_token': access_token, 'user': user_payload(user)})


@api_bp.get('/amenities')
def list_amenities():
    amenities = Amenity.query.order_by(Amenity.name.asc()).all()
    return jsonify([
        {'id': amenity.id, 'name': amenity.name, 'description': amenity.description}
        for amenity in amenities
    ])


@api_bp.get('/units')
def list_units():
    units = Unit.query.join(Tower).order_by(Tower.name.asc(), Unit.number.asc()).all()
    return jsonify([unit_payload(unit) for unit in units])


@api_bp.post('/bookings')
@jwt_required()
def create_booking():
    data = request.get_json() or {}
    resident_id = int(get_jwt_identity())

    if not {'unit_id', 'move_in_date'}.issubset(data):
        return jsonify({'message': 'unit_id and move_in_date are required'}), 400

    unit = Unit.query.get(data['unit_id'])
    if not unit:
        return jsonify({'message': 'Unit not found'}), 404

    booking = Booking(
        unit_id=unit.id,
        resident_id=resident_id,
        move_in_date=date.fromisoformat(data['move_in_date']),
    )
    db.session.add(booking)
    db.session.commit()

    return jsonify({'booking': booking_payload(booking)}), 201


@api_bp.get('/bookings/me')
@jwt_required()
def my_bookings():
    resident_id = int(get_jwt_identity())
    bookings = (
        Booking.query.filter_by(resident_id=resident_id)
        .order_by(Booking.created_at.desc())
        .all()
    )
    return jsonify([booking_payload(booking) for booking in bookings])


def require_admin(user: User):
    if user.role != 'admin':
        return jsonify({'message': 'Admin role required'}), 403
    return None


@api_bp.get('/admin/dashboard')
@jwt_required()
def admin_dashboard():
    user = User.query.get(int(get_jwt_identity()))
    unauthorized = require_admin(user)
    if unauthorized:
        return unauthorized

    total_units = Unit.query.count()
    occupied_units = Unit.query.filter_by(occupied=True).count()
    pending_bookings = Booking.query.filter_by(status='pending').count()

    occupancy_rate = round((occupied_units / total_units) * 100, 2) if total_units else 0

    return jsonify(
        {
            'total_units': total_units,
            'occupied_units': occupied_units,
            'occupancy_rate': occupancy_rate,
            'pending_bookings': pending_bookings,
        }
    )


@api_bp.get('/admin/bookings')
@jwt_required()
def admin_bookings():
    user = User.query.get(int(get_jwt_identity()))
    unauthorized = require_admin(user)
    if unauthorized:
        return unauthorized

    bookings = Booking.query.order_by(Booking.created_at.desc()).all()
    return jsonify([booking_payload(booking) for booking in bookings])


@api_bp.patch('/admin/bookings/<int:booking_id>')
@jwt_required()
def update_booking_status(booking_id: int):
    user = User.query.get(int(get_jwt_identity()))
    unauthorized = require_admin(user)
    if unauthorized:
        return unauthorized

    data = request.get_json() or {}
    status = data.get('status')
    payment = data.get('mock_payment_status')

    booking = Booking.query.get_or_404(booking_id)
    if status in {'approved', 'declined', 'pending'}:
        booking.status = status
    if payment in {'paid', 'unpaid', 'processing'}:
        booking.mock_payment_status = payment

    if booking.status == 'approved':
        booking.unit.occupied = True

    db.session.commit()
    return jsonify({'booking': booking_payload(booking)})


@api_bp.post('/seed')
def seed_data():
    if Tower.query.count() > 0:
        return jsonify({'message': 'Seed data already present'}), 200

    admin = User(name='Admin User', email='admin@portal.local', role='admin')
    admin.set_password('Admin@123')
    resident = User(name='Demo Resident', email='resident@portal.local', role='resident')
    resident.set_password('Resident@123')

    amenities = [
        Amenity(name='Gym', description='Fully equipped fitness center'),
        Amenity(name='Pool', description='Temperature-controlled lap pool'),
        Amenity(name='Parking', description='Covered parking slots'),
    ]

    tower_a = Tower(name='Tower A', address='100 Main St')
    tower_b = Tower(name='Tower B', address='200 Main St')

    unit_a101 = Unit(tower=tower_a, number='A-101', bedrooms=2, rent=Decimal('1800.00'))
    unit_a102 = Unit(tower=tower_a, number='A-102', bedrooms=3, rent=Decimal('2200.00'))
    unit_b201 = Unit(tower=tower_b, number='B-201', bedrooms=1, rent=Decimal('1500.00'))

    unit_a101.amenities.extend(amenities)
    unit_a102.amenities.extend(amenities[:2])
    unit_b201.amenities.extend([amenities[0], amenities[2]])

    db.session.add_all([admin, resident, *amenities, tower_a, tower_b, unit_a101, unit_a102, unit_b201])
    db.session.commit()

    return jsonify({'message': 'Seed data created'}), 201
