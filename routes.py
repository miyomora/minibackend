from flask import request, jsonify
from app import app, db
from models import User, Pet
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

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
