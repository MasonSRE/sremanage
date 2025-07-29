from flask import Blueprint, jsonify, request
from app.models.user import User
from app.extensions import db
from app.utils.auth import token_required
from app.utils.logger import get_logger

logger = get_logger(__name__)
user_bp = Blueprint('user', __name__)

@user_bp.route('/users', methods=['GET'])
@token_required
def get_users():
    try:
        users = User.query.all()
        return jsonify({
            'success': True,
            'data': [user.to_dict() for user in users]
        })
    except Exception as e:
        logger.error(f"Get users error: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@user_bp.route('/users/<int:user_id>', methods=['GET'])
@token_required
def get_user(user_id):
    try:
        user = User.query.get_or_404(user_id)
        return jsonify({
            'success': True,
            'data': user.to_dict()
        })
    except Exception as e:
        logger.error(f"Get user error: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@user_bp.route('/users', methods=['POST'])
@token_required
def create_user():
    try:
        data = request.get_json()
        
        # 验证必填字段
        required_fields = ['username', 'password', 'email']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'message': f'Missing required field: {field}'}), 400
        
        # 检查用户名是否已存在
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'success': False, 'message': 'Username already exists'}), 400
            
        # 创建新用户
        user = User(
            username=data['username'],
            password=data['password'],
            email=data['email']
        )
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'User created successfully',
            'data': user.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        logger.error(f"Create user error: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@user_bp.route('/users/<int:user_id>', methods=['PUT'])
@token_required
def update_user(user_id):
    try:
        user = User.query.get_or_404(user_id)
        data = request.get_json()
        
        # 更新用户信息
        if 'username' in data:
            # 检查新用户名是否与其他用户冲突
            existing_user = User.query.filter_by(username=data['username']).first()
            if existing_user and existing_user.id != user_id:
                return jsonify({'success': False, 'message': 'Username already exists'}), 400
            user.username = data['username']
            
        if 'email' in data:
            user.email = data['email']
            
        if 'password' in data:
            user.set_password(data['password'])
            
        if 'is_active' in data:
            user.is_active = data['is_active']
            
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'User updated successfully',
            'data': user.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        logger.error(f"Update user error: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@user_bp.route('/users/<int:user_id>', methods=['DELETE'])
@token_required
def delete_user(user_id):
    try:
        user = User.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'User deleted successfully'
        })
    except Exception as e:
        db.session.rollback()
        logger.error(f"Delete user error: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500 