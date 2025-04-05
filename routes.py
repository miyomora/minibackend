from flask import request, jsonify
from app import app, db
from models import User, Pet, Booking, Boarding
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from datetime import datetime

jwt = JWTManager(app)

@app.route('/register', methods=['POST'])
def register_user():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
        
    if not all(k in data for k in ['name', 'email', 'password']):
        return jsonify({'error': 'Missing required fields'}), 400
        
    try:
        hashed_password = generate_password_hash(data['password'])
        new_user = User(
            name=data['name'],
            email=data['email'],
            password_hash=hashed_password,
            role=data.get('role', 'adopter')
        )
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'message': 'User registered successfully!'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()
    
    if user and check_password_hash(user.password_hash, data['password']):
        access_token = create_access_token(identity=str(user.id))
        return jsonify({'token': access_token})
    
    return jsonify({'message': 'Invalid credentials'}), 401

@app.route('/pets', methods=['POST'])
@jwt_required()
def add_pet():
    data = request.get_json()

    if not all(k in data for k in ['name', 'species', 'breed', 'contact_email']):
        return jsonify({'error': 'Missing required fields'}), 400

    try:
        new_pet = Pet(
            name=data['name'],
            species=data['species'],
            breed=data['breed'],
            age=data.get('age'),
            description=data.get('description'),
            contact_email=data['contact_email'],
            contact_phone=data.get('contact_phone')
        )

        db.session.add(new_pet)
        db.session.commit()

        return jsonify({'message': 'Pet added successfully!'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/pets', methods=['GET'])
def get_pets():
    pets = Pet.query.all()
    pets_data = [
        {
            "id": pet.id,
            "name": pet.name,
            "species": pet.species,
            "breed": pet.breed,
            "age": pet.age,
            "description": pet.description,
            "contact_email": pet.contact_email,
            "contact_phone": pet.contact_phone
        }
        for pet in pets
    ]
    return jsonify(pets_data), 200

@app.route('/pets/<int:pet_id>', methods=['DELETE'])
@jwt_required()
def delete_pet(pet_id):
    pet = Pet.query.get(pet_id)

    if not pet:
        return jsonify({'error': 'Pet not found'}), 404

    try:
        db.session.delete(pet)
        db.session.commit()
        return jsonify({'message': 'Pet deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/api/bookings', methods=['POST'])
def create_booking():
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['petName', 'service', 'date', 'time']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400

        # Convert date string to date object
        booking_date = datetime.strptime(data['date'], '%Y-%m-%d').date()

        booking = Booking(
            id=data.get('id', int(datetime.now().timestamp() * 1000)),  # Use provided ID or generate new
            pet_name=data['petName'],
            service=data['service'],
            date=booking_date,
            time=data['time'],
            notes=data.get('notes', '')
        )
        
        db.session.add(booking)
        db.session.commit()
        
        return jsonify(booking.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/bookings', methods=['GET'])
def get_bookings():
    try:
        bookings = Booking.query.order_by(Booking.date.asc(), Booking.time.asc()).all()
        return jsonify([booking.to_dict() for booking in bookings]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/bookings/<int:booking_id>', methods=['DELETE'])
def delete_booking(booking_id):
    try:
        booking = Booking.query.get_or_404(booking_id)
        db.session.delete(booking)
        db.session.commit()
        return jsonify({'message': 'Booking cancelled successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/boardings', methods=['POST'])
def create_boarding():
    try:
        data = request.get_json()
        if not all(k in data for k in ['id', 'petName', 'packageType', 'checkIn', 'checkOut', 'totalPrice']):
            return jsonify({'error': 'Missing required fields'}), 400
        
        boarding = Boarding(
            id=data['id'],
            pet_name=data['petName'],
            package_type=data['packageType'],
            check_in=datetime.strptime(data['checkIn'], '%Y-%m-%d').date(),
            check_out=datetime.strptime(data['checkOut'], '%Y-%m-%d').date(),
            special_needs=data.get('specialNeeds', ''),
            total_price=data['totalPrice']
        )
        db.session.add(boarding)
        db.session.commit()
        return jsonify(boarding.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error in create_boarding: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/boardings', methods=['GET'])
def get_boardings():
    try:
        boardings = Boarding.query.order_by(Boarding.check_in.asc()).all()
        return jsonify([boarding.to_dict() for boarding in boardings]), 200
    except Exception as e:
        print(f"Error in get_boardings: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/boardings/<int:boarding_id>', methods=['DELETE'])
def delete_boarding(boarding_id):
    try:
        boarding = Boarding.query.get_or_404(boarding_id)
        db.session.delete(boarding)
        db.session.commit()
        return jsonify({'message': 'Boarding cancelled'}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error in delete_boarding: {str(e)}")
        return jsonify({'error': str(e)}), 500    
    