from flask import request, jsonify
from app import app, db
from models import User, Booking, Boarding, Consultation, Petm, SellPet, Admin
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from datetime import datetime
import os
import bcrypt

# Define allowed_file function to check file extensions
def allowed_file(filename):
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions


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

# @app.route('/pets', methods=['POST'])
# @jwt_required()
# def add_pet():
#     data = request.get_json()

#     if not all(k in data for k in ['name', 'species', 'breed', 'contact_email']):
#         return jsonify({'error': 'Missing required fields'}), 400

#     try:
#         new_pet = Pet(
#             name=data['name'],
#             species=data['species'],
#             breed=data['breed'],
#             age=data.get('age'),
#             description=data.get('description'),
#             contact_email=data['contact_email'],
#             contact_phone=data.get('contact_phone')
#         )

#         db.session.add(new_pet)
#         db.session.commit()

#         return jsonify({'message': 'Pet added successfully!'}), 201
#     except Exception as e:
#         db.session.rollback()
#         return jsonify({'error': str(e)}), 500

# @app.route('/pets', methods=['GET'])
# def get_pets():
#     pets = Pet.query.all()
#     pets_data = [
#         {
#             "id": pet.id,
#             "name": pet.name,
#             "species": pet.species,
#             "breed": pet.breed,
#             "age": pet.age,
#             "description": pet.description,
#             "contact_email": pet.contact_email,
#             "contact_phone": pet.contact_phone
#         }
#         for pet in pets
#     ]
#     return jsonify(pets_data), 200

# @app.route('/pets/<int:pet_id>', methods=['DELETE'])
# @jwt_required()
# def delete_pet(pet_id):
#     pet = Pet.query.get(pet_id)

#     if not pet:
#         return jsonify({'error': 'Pet not found'}), 404

#     try:
#         db.session.delete(pet)
#         db.session.commit()
#         return jsonify({'message': 'Pet deleted successfully'}), 200
#     except Exception as e:
#         db.session.rollback()
#         return jsonify({'error': str(e)}), 500


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
    
@app.route('/api/consultations', methods=['POST'])
def create_consultation():
    try:
        data = request.get_json()
        if not all(k in data for k in ['id', 'vetId', 'vetName', 'petType', 'petAge', 'symptoms', 'consultDate', 'timeSlot']):
            return jsonify({'error': 'Missing required fields'}), 400
        
        consultation = Consultation(
            id=data['id'],
            vet_id=data['vetId'],
            vet_name=data['vetName'],
            pet_type=data['petType'],
            pet_age=data['petAge'],
            symptoms=data['symptoms'],
            consult_date=datetime.strptime(data['consultDate'], '%Y-%m-%d').date(),
            time_slot=data['timeSlot'],
            status=data.get('status', 'scheduled')
        )
        db.session.add(consultation)
        db.session.commit()
        return jsonify(consultation.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error in create_consultation: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/consultations', methods=['GET'])
def get_consultations():
    try:
        consultations = Consultation.query.order_by(Consultation.consult_date.asc(), Consultation.time_slot.asc()).all()
        return jsonify([consult.to_dict() for consult in consultations]), 200
    except Exception as e:
        print(f"Error in get_consultations: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/consultations/<int:consultation_id>', methods=['DELETE'])
def delete_consultation(consultation_id):
    try:
        consultation = Consultation.query.get_or_404(consultation_id)
        db.session.delete(consultation)
        db.session.commit()
        return jsonify({'message': 'Consultation cancelled'}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error in delete_consultation: {str(e)}")
        return jsonify({'error': str(e)}), 500
    
@app.route('/api/petm', methods=['POST'])
def create_petm():
    try:
        # Check for required fields in form data
        if not all(k in request.form for k in ['id', 'name', 'species', 'breed', 'age', 'vaccination', 'aggression']):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Handle file upload
        image_name = None
        if 'image' in request.files:
            file = request.files['image']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Use a unique filename to avoid overwrites (e.g., prepend ID)
                unique_filename = f"{request.form['id']}_{filename}"
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                file.save(file_path)
                image_name = unique_filename  # Store just the filename (or full path if needed)

        petm = Petm(
            id=int(request.form['id']),
            name=request.form['name'],
            species=request.form['species'],
            breed=request.form['breed'],
            age=int(request.form['age']),
            vaccination_status=request.form['vaccination'],
            aggression_level=request.form['aggression'],
            image_name=image_name
        )
        db.session.add(petm)
        db.session.commit()
        return jsonify(petm.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error in create_petm: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/petm', methods=['GET'])
def get_petm():
    try:
        petms = Petm.query.order_by(Petm.created_at.asc()).all()
        return jsonify([petm.to_dict() for petm in petms]), 200
    except Exception as e:
        print(f"Error in get_petm: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/petm/<int:petm_id>', methods=['DELETE'])
def delete_petm(petm_id):
    try:
        petm = Petm.query.get_or_404(petm_id)
        # Optionally delete the image file
        if petm.image_name:
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], petm.image_name)
            if os.path.exists(image_path):
                os.remove(image_path)
        db.session.delete(petm)
        db.session.commit()
        return jsonify({'message': 'Pet deleted'}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error in delete_petm: {str(e)}")
        return jsonify({'error': str(e)}), 500
    
@app.route('/api/sell_pets', methods=['POST'])
def create_sell_pet():
    try:
        if not all(k in request.form for k in ['id', 'name', 'species', 'breed', 'contact_email', 'price']):
            return jsonify({'error': 'Missing required fields'}), 400
        
        image_name = None
        if 'image' in request.files:
            file = request.files['image']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                unique_filename = f"{request.form['id']}_{filename}"
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                file.save(file_path)
                image_name = unique_filename

        sell_pet = SellPet(
            id=int(request.form['id']),
            name=request.form['name'],
            species=request.form['species'],
            breed=request.form['breed'],
            age=int(request.form.get('age', 0)),
            description=request.form.get('pet-desc'),
            image_name=image_name,
            contact_email=request.form['contact_email'],
            contact_phone=request.form.get('contact_phone'),
            price=int(request.form['price'])  # New price field
        )
        db.session.add(sell_pet)
        db.session.commit()
        return jsonify(sell_pet.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error in create_sell_pet: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/sell_pets', methods=['GET'])
def get_sell_pets():
    try:
        sell_pets = SellPet.query.order_by(SellPet.created_at.asc()).all()
        return jsonify([pet.to_dict() for pet in sell_pets]), 200
    except Exception as e:
        print(f"Error in get_sell_pets: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/sell_pets/<int:pet_id>', methods=['DELETE'])
def delete_sell_pet(pet_id):
    try:
        sell_pet = SellPet.query.get_or_404(pet_id)
        if sell_pet.image_name:
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], sell_pet.image_name)
            if os.path.exists(image_path):
                os.remove(image_path)
        db.session.delete(sell_pet)
        db.session.commit()
        return jsonify({'message': 'Pet deleted'}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error in delete_sell_pet: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/users', methods=['GET'])
def get_users():
    try:
        users = User.query.order_by(User.created_at.asc()).all()
        return jsonify([{
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'role': user.role,
            'created_at': user.created_at.isoformat()
        } for user in users]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
@app.route('/api/users/<int:id>', methods=['DELETE'])
def delete_user(id):
    # Logic to delete user with given id
    return jsonify({"message": "User deleted successfully"}), 200



# Handle login request
@app.route('/admin-login-page')
def login_page():
    return app.send_static_file('adminlogin.html')

# Handle login request
@app.route('/api/admin-authenticate', methods=['POST'])
def authenticate_admin():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'message': 'Email and password are required'}), 400

    admin = Admin.query.filter_by(email=email).first()
    if admin and bcrypt.checkpw(password.encode('utf-8'), admin.password.encode('utf-8')):
        return jsonify({'message': 'Login successful', 'redirect': 'http://127.0.0.1:5500/admin.html'}), 200
    else:
        return jsonify({'message': 'Invalid email or password'}), 401

# Serve the admin panel (protected route)
@app.route('/admin-dashboard')
def admin_dashboard():
    # Add authentication check here in a real app
    return app.send_static_file('admin.html')