from flask_restx import Namespace, Resource, fields
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.services import facade  # instance commune du facade

api = Namespace('places', description='Place operations')

# -----------------------
# Models
# -----------------------
amenity_model = api.model('PlaceAmenity', {
    'id': fields.String(description='Amenity ID'),
    'name': fields.String(description='Name of the amenity')
})

user_model = api.model('PlaceUser', {
    'id': fields.String(description='User ID'),
    'first_name': fields.String(description='First name of the owner'),
    'last_name': fields.String(description='Last name of the owner'),
    'email': fields.String(description='Email of the owner')
})

place_model = api.model('Place', {
    'title': fields.String(required=True),
    'description': fields.String(),
    'price': fields.Float(required=True),
    'latitude': fields.Float(required=True),
    'longitude': fields.Float(required=True),
    'amenities': fields.List(fields.String, required=True, description="List of amenities ID's")
})

# -----------------------
# LIST / CREATE PLACES
# -----------------------
@api.route('/')
class PlaceList(Resource):
    @api.response(200, 'List of places')
    def get(self):
        """List all places (public)"""
        places = facade.get_all_places()
        return [{
            "id": p.id,
            "title": p.title,
            "price": p.price,
            "latitude": p.latitude,
            "longitude": p.longitude
        } for p in places]

    @api.expect(place_model)
    @api.doc(security='Bearer')  # Swagger inclut le token
    @jwt_required()
    @api.response(201, 'Place created successfully')
    @api.response(400, 'Invalid data')
    def post(self):
        """Create a new place (authenticated users only)"""
        current_user_id = get_jwt_identity()
        data = request.json
        data['owner_id'] = current_user_id  # assign automatically

        # Vérification des amenities existants
        for amenity_id in data.get('amenities', []):
            if not facade.get_amenity(amenity_id):
                return {"message": f"Amenity {amenity_id} does not exist"}, 400

        place = facade.create_place(data)
        return {
            "id": place.id,
            "title": place.title,
            "price": place.price,
            "latitude": place.latitude,
            "longitude": place.longitude
        }, 201


# -----------------------
# GET / UPDATE / DELETE SPECIFIC PLACE
# -----------------------
@api.route('/<string:place_id>')
class PlaceResource(Resource):
    @api.response(200, 'Place details retrieved')
    @api.response(404, 'Place not found')
    def get(self, place_id):
        """Get a specific place (public)"""
        try:
            place = facade.get_place(place_id)
        except ValueError:
            return {"error": "Place not found"}, 404

        # Amenities objets directement
        amenities = [{"id": a.id, "name": a.name} for a in place.amenities]

        # Owner
        owner = facade.get_user(place.owner_id)
        if not owner:
            return {"error": "Owner not found"}, 404

        return {
            "id": place.id,
            "title": place.title,
            "description": place.description,
            "price": place.price,
            "latitude": place.latitude,
            "longitude": place.longitude,
            "owner": {
                "id": owner.id,
                "first_name": owner.first_name,
                "last_name": owner.last_name,
                "email": owner.email
            },
            "amenities": amenities
        }, 200

    @api.expect(place_model)
    @api.doc(security='Bearer')  # Swagger + JWT
    @jwt_required()
    @api.response(200, 'Place updated successfully')
    @api.response(404, 'Place not found')
    @api.response(403, 'Unauthorized')
    def put(self, place_id):
        """Update place info (owner or admin)"""
        current_user_id = get_jwt_identity()
        claims = get_jwt()
        is_admin = claims.get('is_admin', False)

        try:
            place = facade.get_place(place_id)
        except ValueError:
            return {"error": "Place not found"}, 404

        if place.owner_id != current_user_id and not is_admin:
            return {"error": "Unauthorized action"}, 403

        data = api.payload
        data.pop("owner_id", None)  # ne pas changer le propriétaire

        # Vérification des amenities existants
        for amenity_id in data.get('amenities', []):
            if not facade.get_amenity(amenity_id):
                return {"message": f"Amenity {amenity_id} does not exist"}, 400

        facade.update_place(place_id, data)
        return {"message": "Place updated successfully"}, 200

    @api.doc(security='Bearer')  # Swagger + JWT
    @jwt_required()
    @api.response(200, 'Place deleted successfully')
    @api.response(404, 'Place not found')
    @api.response(403, 'Unauthorized')
    def delete(self, place_id):
        """Delete a place (owner or admin)"""
        current_user_id = get_jwt_identity()
        claims = get_jwt()
        is_admin = claims.get('is_admin', False)

        try:
            place = facade.get_place(place_id)
        except ValueError:
            return {"error": "Place not found"}, 404

        if place.owner_id != current_user_id and not is_admin:
            return {"error": "Unauthorized action"}, 403

        facade.delete_place(place_id)
        return {"message": "Place deleted successfully"}, 200
