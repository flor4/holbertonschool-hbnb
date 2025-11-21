from flask_restx import Namespace, Resource, fields
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.services import facade
from app.api.v1.auth import role_required

api = Namespace('users', description='User operations')

# Modèles Swagger
user_model = api.model('User', {
    'first_name': fields.String(required=True),
    'last_name': fields.String(required=True),
    'email': fields.String(required=True),
    'password': fields.String(required=True)
})

user_update_model = api.model('UserUpdate', {
    'first_name': fields.String(),
    'last_name': fields.String()
})

admin_update_model = api.model('AdminUserUpdate', {
    'first_name': fields.String(),
    'last_name': fields.String(),
    'email': fields.String(),
    'password': fields.String()
})

# -----------------------
# Routes utilisateurs
# -----------------------
@api.route('/')
class UserList(Resource):
    def get(self):
        """List all users"""
        users = facade.get_all_users()
        return [u.to_dict() for u in users], 200

    @api.expect(user_model)
    def post(self):
        """Normal user registration"""
        data = request.json
        if facade.get_user_by_email(data['email']):
            return {'error': 'Email already registered'}, 400
        try:
            user = facade.create_user(data)
            return user.to_dict(), 201
        except ValueError as e:
            return {'error': str(e)}, 400


@api.route('/<string:user_id>')
class UserResource(Resource):
    @jwt_required()
    @api.doc(security='Bearer')
    @api.expect(user_update_model)
    def put(self, user_id):
        """Update own profile (first_name / last_name)"""
        current_user = get_jwt_identity()
        if str(current_user) != str(user_id):
            return {'error': 'Unauthorized action'}, 403

        data = request.json or {}
        if not any(k in data for k in ['first_name', 'last_name']):
            return {'error': 'No valid fields to update'}, 400

        try:
            updated_user = facade.update_user(user_id, data)
        except ValueError as e:
            return {'error': str(e)}, 400

        if not updated_user:
            return {'error': 'User not found'}, 404

        return {'message': 'User updated successfully'}, 200


# -----------------------
# Routes admin
# -----------------------
@api.route('/admin/')
class AdminUserCreate(Resource):
    @role_required('admin')
    @api.doc(security='Bearer')
    @api.expect(user_model)
    def post(self):
        """Admin creates a new user"""
        data = request.json
        if facade.get_user_by_email(data['email']):
            return {'error': 'Email already registered'}, 400
        try:
            user = facade.create_user(data)
            return user.to_dict(), 201
        except ValueError as e:
            return {'error': str(e)}, 400


@api.route('/admin/<string:user_id>')
class AdminUserModify(Resource):
    @role_required('admin')
    @api.doc(security='Bearer')
    @api.expect(admin_update_model)
    def put(self, user_id):
        """Admin updates any user"""
        data = request.json or {}
        email = data.get('email')
        if email:
            existing_user = facade.get_user_by_email(email)
            if existing_user and str(existing_user.id) != str(user_id):
                return {'error': 'Email already in use'}, 400
        try:
            updated_user = facade.update_user(user_id, data)
        except ValueError as e:
            return {'error': str(e)}, 400

        if not updated_user:
            return {'error': 'User not found'}, 404

        return {'message': 'User updated successfully'}, 200
