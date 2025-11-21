from flask import Flask
from flask_restx import Api
from app.Extensions import jwt, bcrypt, db
from config import DevelopmentConfig
from flask_cors import CORS

# Import des namespaces
from app.api.v1.places import api as places_ns
from app.api.v1.users import api as users_ns
from app.api.v1.amenities import api as amenities_ns
from app.api.v1.reviews import api as reviews_ns
from app.api.v1.auth import api as auth_ns

# Import explicite des modèles pour que SQLAlchemy connaisse toutes les tables
from app.models.user import User
from app.models.place import Place
from app.models.amenity import Amenity
from app.models.review import Review

authorizations = {
    'Bearer': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization',
        'description': "Entrer le token JWT comme : **Bearer <votre_token>**"
    }
}

def create_app(config_class=DevelopmentConfig):
    app = Flask(__name__)
    app.config.from_object(config_class)

    CORS(app, resources={r"/api/*": {"origins": "http://localhost:8000"}}, supports_credentials=True)


    # Initialisation des extensions
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)

    # Initialisation de l'API
    api = Api(
        app,
        version='1.0',
        title='HBnB API',
        description='HBnB Application API',
        doc='/api/v1/',
        authorizations=authorizations,
    )

    # Enregistrement des namespaces
    api.add_namespace(users_ns, path='/api/v1/users')
    api.add_namespace(places_ns, path='/api/v1/places')
    api.add_namespace(amenities_ns, path='/api/v1/amenities')
    api.add_namespace(reviews_ns, path='/api/v1/reviews')
    api.add_namespace(auth_ns, path='/api/v1/auth')

    # Création des tables
    with app.app_context():
        db.create_all()  # toutes les tables importées sont créées ici

    return app
