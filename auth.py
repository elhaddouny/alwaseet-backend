from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from src.models.user import db, User
from src.models.craftsman import Craftsman
import jwt
import datetime
import os

auth_bp = Blueprint('auth', __name__)

# Secret key for JWT (in production, use environment variable)
SECRET_KEY = os.environ.get('SECRET_KEY', 'asdf#FGSgvasgf$5$WGT')

def generate_token(user_id, user_type='customer'):
    """Generate JWT token for user"""
    payload = {
        'user_id': user_id,
        'user_type': user_type,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7)  # Token expires in 7 days
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def verify_token(token):
    """Verify JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user (customer or craftsman)"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'email', 'password', 'user_type']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Validate user type
        if data['user_type'] not in ['customer', 'craftsman']:
            return jsonify({
                'success': False,
                'error': 'Invalid user type. Must be customer or craftsman'
            }), 400
        
        # Check if email already exists
        existing_user = User.query.filter_by(email=data['email']).first()
        existing_craftsman = Craftsman.query.filter_by(email=data['email']).first()
        
        if existing_user or existing_craftsman:
            return jsonify({
                'success': False,
                'error': 'Email already exists'
            }), 400
        
        if data['user_type'] == 'customer':
            # Create customer user
            user = User(
                username=data['name'],
                email=data['email']
            )
            db.session.add(user)
            db.session.commit()
            
            # Generate token
            token = generate_token(user.id, 'customer')
            
            return jsonify({
                'success': True,
                'data': {
                    'user': user.to_dict(),
                    'token': token,
                    'user_type': 'customer'
                },
                'message': 'Customer registered successfully'
            }), 201
            
        else:  # craftsman
            # Validate additional fields for craftsman
            craftsman_fields = ['phone', 'service_type', 'location']
            for field in craftsman_fields:
                if field not in data:
                    return jsonify({
                        'success': False,
                        'error': f'Missing required field for craftsman: {field}'
                    }), 400
            
            # Create craftsman
            craftsman = Craftsman(
                name=data['name'],
                email=data['email'],
                phone=data['phone'],
                service_type=data['service_type'],
                location=data['location'],
                description=data.get('description', ''),
                experience_years=data.get('experience_years', 0),
                price_range=data.get('price_range', ''),
                availability=data.get('availability', ''),
                is_verified=False  # Craftsmen need to be verified
            )
            
            db.session.add(craftsman)
            db.session.commit()
            
            # Generate token
            token = generate_token(craftsman.id, 'craftsman')
            
            return jsonify({
                'success': True,
                'data': {
                    'craftsman': craftsman.to_dict(),
                    'token': token,
                    'user_type': 'craftsman'
                },
                'message': 'Craftsman registered successfully. Account pending verification.'
            }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login user"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['email', 'password']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        # For demo purposes, we'll skip password verification
        # In production, you should hash passwords and verify them
        
        # Check if user exists as customer
        user = User.query.filter_by(email=data['email']).first()
        if user:
            token = generate_token(user.id, 'customer')
            return jsonify({
                'success': True,
                'data': {
                    'user': user.to_dict(),
                    'token': token,
                    'user_type': 'customer'
                },
                'message': 'Login successful'
            })
        
        # Check if user exists as craftsman
        craftsman = Craftsman.query.filter_by(email=data['email']).first()
        if craftsman:
            token = generate_token(craftsman.id, 'craftsman')
            return jsonify({
                'success': True,
                'data': {
                    'craftsman': craftsman.to_dict(),
                    'token': token,
                    'user_type': 'craftsman'
                },
                'message': 'Login successful'
            })
        
        # User not found
        return jsonify({
            'success': False,
            'error': 'Invalid email or password'
        }), 401
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@auth_bp.route('/verify-token', methods=['POST'])
def verify_user_token():
    """Verify JWT token"""
    try:
        data = request.get_json()
        token = data.get('token')
        
        if not token:
            return jsonify({
                'success': False,
                'error': 'Token is required'
            }), 400
        
        payload = verify_token(token)
        if not payload:
            return jsonify({
                'success': False,
                'error': 'Invalid or expired token'
            }), 401
        
        return jsonify({
            'success': True,
            'data': payload,
            'message': 'Token is valid'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@auth_bp.route('/profile', methods=['GET'])
def get_profile():
    """Get user profile (requires authentication)"""
    try:
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({
                'success': False,
                'error': 'Authorization token is required'
            }), 401
        
        token = auth_header.split(' ')[1]
        payload = verify_token(token)
        
        if not payload:
            return jsonify({
                'success': False,
                'error': 'Invalid or expired token'
            }), 401
        
        user_id = payload['user_id']
        user_type = payload['user_type']
        
        if user_type == 'customer':
            user = User.query.get_or_404(user_id)
            return jsonify({
                'success': True,
                'data': {
                    'user': user.to_dict(),
                    'user_type': 'customer'
                }
            })
        else:  # craftsman
            craftsman = Craftsman.query.get_or_404(user_id)
            craftsman_data = craftsman.to_dict()
            craftsman_data['services'] = [service.to_dict() for service in craftsman.services]
            craftsman_data['portfolio'] = [item.to_dict() for item in craftsman.portfolio]
            
            return jsonify({
                'success': True,
                'data': {
                    'craftsman': craftsman_data,
                    'user_type': 'craftsman'
                }
            })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

