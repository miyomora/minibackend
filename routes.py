from flask import request, jsonify
from app import app, db
from models import User, Pet, Notification, Adoption, Service, Booking
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import JWTManager, create_access_token ,jwt_required, get_jwt_identity

jwt = JWTManager(app)

@app.route('/register', methods=['POST'])
def register_user():
    data = request.get_json()
    hashed_password = generate_password_hash(data['password'])
    new_user = User(
        name=data['name'],
        email=data['email'],
        password_hash=hashed_password,
        role=data.get('role', 'adopter')
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User registered successfully!'})

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()
    if user and check_password_hash(user.password_hash, data['password']):
        access_token = create_access_token(identity=user.id)
        return jsonify({'token': access_token})
    return jsonify({'message': 'Invalid credentials'}), 401

@app.route('/pets', methods=['GET'])
@jwt_required()
def get_pets():
    current_user = get_jwt_identity()
    pets = Pet.query.all()
    pet_list = [
        {'id': pet.id, 'name': pet.name, 'species': pet.species, 'owner_id': pet.owner_id}
        for pet in pets
    ]
    return jsonify({'current_user': current_user, 'pets': pet_list})

@app.route('/pets', methods=['POST'])
@jwt_required()
def add_pet():
    current_user = get_jwt_identity()
    data = request.get_json()
    new_pet = Pet(
        name=data['name'],
        species=data['species'],
        owner_id=current_user,  # assuming owner_id corresponds to the user ID
        description=data.get('description'),
    )
    db.session.add(new_pet)
    db.session.commit()
    return jsonify({'message': 'Pet added successfully!'})

@app.route('/pets/<int:pet_id>', methods=['PUT'])
@jwt_required()
def update_pet(pet_id):
    data = request.get_json()
    pet = Pet.query.get_or_404(pet_id)
    pet.name = data.get('name', pet.name)
    pet.species = data.get('species', pet.species)
    pet.description = data.get('description', pet.description)
    db.session.commit()
    return jsonify({'message': 'Pet updated successfully!'})

@app.route('/pets/<int:pet_id>', methods=['DELETE'])
@jwt_required()
def delete_pet(pet_id):
    pet = Pet.query.get_or_404(pet_id)
    db.session.delete(pet)
    db.session.commit()
    return jsonify({'message': 'Pet deleted successfully!'})

@app.route('/adoptions', methods=['POST'])
@jwt_required()
def request_adoption():
    current_user = get_jwt_identity()
    data = request.get_json()
    new_adoption = Adoption(
        pet_id=data['pet_id'],
        adopter_id=current_user,
        status='pending'
    )
    db.session.add(new_adoption)
    db.session.commit()
    return jsonify({'message': 'Adoption request submitted!'})

@app.route('/adoptions', methods=['GET'])
@jwt_required()
def get_adoptions():
    # Only admins or breeders can view all adoption requests
    current_user = get_jwt_identity()
    user = User.query.get(current_user)
    if user.role not in ['admin', 'breeder']:
        return jsonify({'message': 'Unauthorized'}), 403

    adoptions = Adoption.query.all()
    adoption_list = [
        {'id': adoption.id, 'pet_id': adoption.pet_id, 'adopter_id': adoption.adopter_id, 'status': adoption.status}
        for adoption in adoptions
    ]
    return jsonify(adoption_list)

@app.route('/services', methods=['GET'])
def list_services():
    services = Service.query.all()
    service_list = [{'id': service.id, 'name': service.name, 'price': service.price} for service in services]
    return jsonify(service_list)

@app.route('/bookings', methods=['POST'])
@jwt_required()
def book_service():
    current_user = get_jwt_identity()
    data = request.get_json()
    new_booking = Booking(
        service_id=data['service_id'],
        user_id=current_user,
        booking_date=data['booking_date'],
    )
    db.session.add(new_booking)
    db.session.commit()
    return jsonify({'message': 'Service booked successfully!'})

@app.route('/pets/search', methods=['GET'])
@jwt_required()
def search_pets():
    species = request.args.get('species')
    breed = request.args.get('breed')
    pets = Pet.query
    if species:
        pets = pets.filter_by(species=species)
    if breed:
        pets = pets.filter_by(breed=breed)
    pets = pets.all()
    return jsonify([{'id': pet.id, 'name': pet.name} for pet in pets])

@app.route('/notifications', methods=['POST'])
@jwt_required()
def notify_user():
    data = request.get_json()
    new_notification = Notification(
        user_id=data['user_id'],
        message=data['message']
    )
    db.session.add(new_notification)
    db.session.commit()
    return jsonify({'message': 'Notification sent!'})
