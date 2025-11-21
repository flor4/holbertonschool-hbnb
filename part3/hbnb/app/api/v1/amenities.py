from flask_restx import Namespace, Resource, fields
from flask import request
from flask_jwt_extended import jwt_required, get_jwt
from app.services import facade

api = Namespace('amenities', description='Amenity operations')

# -----------------------
# Swagger Models
# -----------------------
amenity_model = api.model('Amenity', {
    'name': fields.String(required=True, description='Name of the amenity')
})

# -----------------------
# Helper function
# -----------------------
def admin_required():
    """Abort if the current user is not an admin"""
    claims = get_jwt()
    if not claims.get('is_admin', False):
        api.abort(403, "Admin privileges required")

# -----------------------
# Routes
# -----------------------
@api.route('/')
class AmenityList(Resource):
    @api.response(200, 'List of amenities retrieved successfully')
    def get(self):
        """Public - Retrieve all amenities"""
        amenities = facade.get_all_amenities()
        return [a.to_dict() for a in amenities], 200

    @api.doc(security='Bearer')  # ✅ Swagger prend en charge le header Authorization
    @jwt_required()
    @api.expect(amenity_model)
    @api.response(201, 'Amenity created successfully')
    @api.response(400, 'Invalid input data')
    @api.response(403, 'Admin privileges required')
    def post(self):
        """Admin only - Create a new amenity"""
        admin_required()

        data = request.get_json() or {}
        name = data.get('name')
        if not name:
            api.abort(400, "Missing required field: 'name'")

        # Vérifie si un amenity avec ce nom existe déjà
        existing = next((a for a in facade.get_all_amenities() if a.name.lower() == name.lower()), None)
        if existing:
            api.abort(400, f"Amenity '{name}' already exists")

        try:
            amenity = facade.create_amenity({'name': name})
            return amenity.to_dict(), 201
        except Exception as e:
            api.abort(500, f"Error creating amenity: {str(e)}")


@api.route('/<string:amenity_id>')
class AmenityResource(Resource):
    @api.response(200, 'Amenity details retrieved successfully')
    @api.response(404, 'Amenity not found')
    def get(self, amenity_id):
        """Public - Get amenity details by ID"""
        amenity = facade.get_amenity(amenity_id)
        if not amenity:
            api.abort(404, f"Amenity with id '{amenity_id}' not found")
        return amenity.to_dict(), 200

    @api.doc(security='Bearer')
    @jwt_required()
    @api.expect(amenity_model)
    @api.response(200, 'Amenity updated successfully')
    @api.response(400, 'Invalid input data')
    @api.response(403, 'Admin privileges required')
    @api.response(404, 'Amenity not found')
    def put(self, amenity_id):
        """Admin only - Update an amenity"""
        admin_required()

        data = request.get_json() or {}
        name = data.get('name')
        if not name:
            api.abort(400, "Missing required field: 'name'")

        amenity = facade.get_amenity(amenity_id)
        if not amenity:
            api.abort(404, f"Amenity with id '{amenity_id}' not found")

        try:
            updated = facade.update_amenity(amenity_id, {'name': name})
            return updated.to_dict(), 200
        except Exception as e:
            api.abort(500, f"Error updating amenity: {str(e)}")

    @api.doc(security='Bearer')
    @jwt_required()
    @api.response(200, 'Amenity deleted successfully')
    @api.response(403, 'Admin privileges required')
    @api.response(404, 'Amenity not found')
    def delete(self, amenity_id):
        """Admin only - Delete an amenity"""
        admin_required()

        amenity = facade.get_amenity(amenity_id)
        if not amenity:
            api.abort(404, f"Amenity with id '{amenity_id}' not found")

        try:
            facade.delete_amenity(amenity_id)
            return {"message": f"Amenity '{amenity_id}' deleted successfully"}, 200
        except Exception as e:
            api.abort(500, f"Error deleting amenity: {str(e)}")
