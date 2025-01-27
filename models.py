from app import db

# User Model
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.Text, nullable=False)
    role = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    pets = db.relationship('Pet', backref='owner', lazy=True)
    bookings = db.relationship('Booking', backref='user', lazy=True)
    adoptions = db.relationship('Adoption', backref='adopter', lazy=True)
    notifications = db.relationship('Notification', backref='user', lazy=True)


# Pet Model
class Pet(db.Model):
    __tablename__ = 'pets'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    species = db.Column(db.String(50), nullable=False)
    breed = db.Column(db.String(50), nullable=True)
    age = db.Column(db.Integer, nullable=True)
    size = db.Column(db.String(20), nullable=True)  # Example: Small, Medium, Large
    description = db.Column(db.Text, nullable=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    available_for_adoption = db.Column(db.Boolean, default=True)

    adoption_requests = db.relationship('Adoption', backref='pet', lazy=True)


# Adoption Model
class Adoption(db.Model):
    __tablename__ = 'adoptions'
    id = db.Column(db.Integer, primary_key=True)
    pet_id = db.Column(db.Integer, db.ForeignKey('pets.id'), nullable=False)
    adopter_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(50), default='pending')  # Example: pending, approved, rejected
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())


# Service Model
class Service(db.Model):
    __tablename__ = 'services'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False)
    duration = db.Column(db.Integer, nullable=True)  # Duration in minutes

    bookings = db.relationship('Booking', backref='service', lazy=True)


# Booking Model
class Booking(db.Model):
    __tablename__ = 'bookings'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('services.id'), nullable=False)
    booking_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(50), default='pending')  # Example: pending, confirmed, canceled
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())


# Notification Model
class Notification(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
