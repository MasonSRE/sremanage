from flask import Blueprint, request, jsonify
from flask_cors import cross_origin

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/api/login', methods=['POST'])
@cross_origin()
def login():
    try:
        data = request.get_json()
        # ... 验证逻辑
        
        return jsonify({
            'success': True,
            'data': {
                'token': token,
                'username': username,
                'expires': expires
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400 