from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/auth/status', methods=['GET'])
@jwt_required(optional=True)
def auth_status():
    current_user = get_jwt_identity()
    return jsonify({"logged_in": bool(current_user)}), 200
