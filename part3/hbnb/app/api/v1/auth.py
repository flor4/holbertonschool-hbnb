from flask_restx import Namespace, Resource, fields
from flask import request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt
from app.services import facade

api = Namespace('auth', description='Authentication operations')

login_model = api.model('Login', {
    'email': fields.String(required=True, description='User email'),
    'password': fields.String(required=True, description='User password')
})

register_model = api.model('Register', {
    'first_name': fields.String(required=True),
    'last_name': fields.String(required=True),
    'email': fields.String(required=True),
    'password': fields.String(required=True)
})

@api.route('/login')
class Login(Resource):
    @api.expect(login_model)
    def post(self):
        """Authenticate user and return JWT token"""
        data = request.json
        user = facade.get_user_by_email(data['email'])
        if not user or not user.verify_password(data['password']):
            return {'error': 'Invalid credentials'}, 401

        access_token = create_access_token(
            identity=str(user.id),
            additional_claims={'is_admin': user.is_admin},
            expires_delta=False
        )

        return {'access_token': access_token}, 200


@api.route('/register')
class Register(Resource):
    @api.expect(register_model)
    def post(self):
        """Register a new user"""
        data = request.json
        if facade.get_user_by_email(data['email']):
            return {'error': 'Email already registered'}, 400
        try:
            user = facade.create_user(data)
            return user.to_dict(), 201
        except ValueError as e:
            return {'error': str(e)}, 400


# Décorateur pour rôles
from functools import wraps

def role_required(role):
    def decorator(fn):
        @wraps(fn)
        @jwt_required()
        def wrapper(*args, **kwargs):
            claims = get_jwt()
            if role == 'admin' and not claims.get('is_admin', False):
                return {'error': 'Admin privileges required'}, 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator
