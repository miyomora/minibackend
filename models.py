from app import db, app
from datetime import datetime

# User Model
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.Text, nullable=False)
    role = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())



class Booking(db.Model):
    __tablename__ = 'bookings'
    id = db.Column(db.BigInteger, primary_key=True)
    pet_name = db.Column(db.String(100), nullable=False)
    service = db.Column(db.String(50), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.String(5), nullable=False)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'petName': self.pet_name,
            'service': self.service,
            'date': self.date.isoformat(),
            'time': self.time,
            'notes': self.notes
        }

class Boarding(db.Model):
    __tablename__ = 'boardings'
    id = db.Column(db.BigInteger, primary_key=True)
    pet_name = db.Column(db.String(100), nullable=False)
    package_type = db.Column(db.String(50), nullable=False)
    check_in = db.Column(db.Date, nullable=False)
    check_out = db.Column(db.Date, nullable=False)
    special_needs = db.Column(db.Text, nullable=True)
    total_price = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'petName': self.pet_name,
            'packageType': self.package_type,
            'checkIn': self.check_in.isoformat(),
            'checkOut': self.check_out.isoformat(),
            'specialNeeds': self.special_needs,
            'totalPrice': self.total_price
        }
    
class Consultation(db.Model):
    __tablename__ = 'consultations'
    id = db.Column(db.BigInteger, primary_key=True)
    vet_id = db.Column(db.Integer, nullable=False)
    vet_name = db.Column(db.String(100), nullable=False)
    pet_type = db.Column(db.String(50), nullable=False)
    pet_age = db.Column(db.Integer, nullable=False)
    symptoms = db.Column(db.Text, nullable=False)
    consult_date = db.Column(db.Date, nullable=False)
    time_slot = db.Column(db.String(10), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='scheduled')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'vetId': self.vet_id,
            'vetName': self.vet_name,
            'petType': self.pet_type,
            'petAge': self.pet_age,
            'symptoms': self.symptoms,
            'consultDate': self.consult_date.isoformat(),
            'timeSlot': self.time_slot,
            'status': self.status
            }    
class Petm(db.Model):
    __tablename__ = 'petm'
    id = db.Column(db.BigInteger, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    species = db.Column(db.String(50), nullable=False)
    breed = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    vaccination_status = db.Column(db.String(20), nullable=False)
    aggression_level = db.Column(db.String(20), nullable=False)
    image_name = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'species': self.species,
            'breed': self.breed,
            'age': self.age,
            'vaccination': self.vaccination_status,
            'aggression': self.aggression_level,
            'imageName': self.image_name
        }
    
class SellPet(db.Model):
    __tablename__ = 'sell_pets'
    id = db.Column(db.BigInteger, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    species = db.Column(db.String(50), nullable=False)
    breed = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False, default=0)
    description = db.Column(db.Text, nullable=True)
    image_name = db.Column(db.String(255), nullable=True)
    contact_email = db.Column(db.String(120), nullable=False)
    contact_phone = db.Column(db.String(20), nullable=True)
    price = db.Column(db.Integer, nullable=False)  # New price field
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'species': self.species,  # Changed from 'type' to match sell.js
            'breed': self.breed,
            'age': self.age,
            'description': self.description,
            'image_name': self.image_name,
            'contact_email': self.contact_email,
            'contact_phone': self.contact_phone,
            'price': self.price,
            'images': [f"http://127.0.0.1:5000/static/uploads/{self.image_name}"] if self.image_name else []
        }
class Admin(db.Model):
    __tablename__ = 'admins'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(50), default='admin')

    def __repr__(self):
        return f'<Admin {self.email}>'