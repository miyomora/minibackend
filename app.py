from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from dotenv import load_dotenv
from routes import routes_bp
import os


# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app, supports_credentials=True)

# Configure database
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
app.config['UPLOAD_FOLDER'] = "static/pet_images"
app.config['BASE_URL'] = "http://127.0.0.1:5000"

# Initialize extensions
db = SQLAlchemy(app)
jwt = JWTManager(app)

# Import routes after initializing app and db

app.register_blueprint(routes_bp)

@app.route('/')
def index():
    return 'Welcome to Paws Connect!'

if __name__ == '__main__':
    app.run(debug=True)
