from flask import Blueprint, request, jsonify, send_from_directory, current_app
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from models import db, User, Pet, Notification, Adoption, Service, Booking
import os
import time

routes_bp = Blueprint('routes', __name__)

# Define allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@routes_bp.route('/register', methods=['POST'])
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

@routes_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()
    if user and check_password_hash(user.password_hash, password):
        access_token = create_access_token(identity=user.id)
        return jsonify({'token': access_token}), 200
    return jsonify({'message': 'Invalid credentials'}), 401

@routes_bp.route('/auth/status', methods=['GET'])
@jwt_required()
def auth_status():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if user:
        return jsonify({'logged_in': True, 'user': {'id': user.id, 'email': user.email}}), 200
    return jsonify({'logged_in': False}), 401

@routes_bp.route('/pets', methods=['GET'])
@jwt_required()
def get_pets():
    pets = Pet.query.all()
    pet_list = [{'id': pet.id, 'name': pet.name, 'species': pet.species} for pet in pets]
    return jsonify(pet_list)

@routes_bp.route('/pets', methods=['POST'])
@jwt_required()
def add_pet():
    current_user = get_jwt_identity()
    
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No selected image'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        unique_filename = f"pet_{current_user}_{int(time.time())}_{filename}"
        save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)

        os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
        file.save(save_path)

        image_url = f"{current_app.config['BASE_URL']}/static/pet_images/{unique_filename}"

        data = request.form
        new_pet = Pet(
            name=data.get('name'),
            species=data.get('species'),
            breed=data.get('breed'),
            image_url=image_url,
            owner_id=current_user
        )

        db.session.add(new_pet)
        db.session.commit()
        return jsonify({'message': 'Pet added successfully!', 'pet': {'id': new_pet.id, 'image_url': new_pet.image_url}}), 201

    return jsonify({'error': 'Invalid file type'}), 400

@routes_bp.route('/static/pet_images/<filename>')
def serve_pet_image(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)
