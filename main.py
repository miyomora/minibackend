from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from db import get_db_connection

app = Flask(__name__)

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data['username']
    password = data['password']
    hashed_password = generate_password_hash(password)
    print(len(hashed_password))
    
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('INSERT INTO "userDetails" (username, password) VALUES (%s, %s)', (username, hashed_password))
    connection.commit()
    cursor.close()
    connection.close()

    return jsonify({'message': 'User registered successfully'}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data['username']
    password = data['password']

    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('SELECT password FROM "userDetails" WHERE username = %s', (username,))
    user = cursor.fetchone()
    cursor.close()
    connection.close()

    if user and check_password_hash(user[0], password):
        return jsonify({'message': 'Login successful'}), 200
    else:
        return jsonify({'message': 'Invalid credentials'}), 401

@app.route('/', methods=['DELETE'])
def delete_user():
    data = request.get_json()
    username = data['username']

    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('DELETE FROM "userDetails" WHERE username = %s', (username,))
    connection.commit()
    cursor.close()
    connection.close()

    return jsonify({'message': 'User deleted successfully'}), 200

if __name__ == "__main__":
    app.run(debug=True)