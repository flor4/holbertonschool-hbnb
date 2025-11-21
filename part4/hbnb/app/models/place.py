from app.models.BaseModel import BaseModel
from app import db

# Association table between place and amenities
place_amenity = db.Table(
    'place_amenity',
    db.Column('place_id', db.Integer, db.ForeignKey('places.id'), primary_key=True),
    db.Column('amenity_id', db.Integer, db.ForeignKey('amenities.id'), primary_key=True)
)


class Place(BaseModel, db.Model):
    __tablename__ = 'places'

    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500))
    price = db.Column(db.Float, nullable=False)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)

    # Relation One-to-Many : a User can have Places
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Relation Many-to-Many : a Place can have many Amenities
    amenities = db.relationship(
        'Amenity',
        secondary=place_amenity,
        backref=db.backref('places', lazy=True),
        lazy='subquery'
    )

    # Relation One-to-Many : a Place can have many Reviews
    reviews = db.relationship('Review', backref='place', lazy=True)


    def __init__(self, title, description, price, latitude, longitude, owner_id, amenities=None):
        super().__init__()

        if not title or len(title) > 100:
            raise ValueError("Title is required and must be 100 characters max.")
        if price <= 0:
            raise ValueError("Price must be positive.")
        if not (-90 <= latitude <= 90):
            raise ValueError("Latitude must be between -90 and 90.")
        if not (-180 <= longitude <= 180):
            raise ValueError("Longitude must be between -180 and 180.")
        if not owner_id:
            raise ValueError("Place must have an owner (User).")

        self.title = title
        self.description = description
        self.price = price
        self.latitude = latitude
        self.longitude = longitude
        self.owner_id = owner_id
        self.amenities = amenities or []

    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'price': self.price,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'owner_id': self.owner_id,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    def __repr__(self):
        return f"<Place {self.title}>"
