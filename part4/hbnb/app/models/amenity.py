from app.models.BaseModel import BaseModel
from app.Extensions import db, bcrypt



class Amenity(BaseModel, db.Model):
    __tablename__ = 'amenities'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

    def __init__(self, name):

        super().__init__()
        self.set_name(name)

    def set_name(self, name):

        if not name:
            raise ValueError("Amenity name is required.")
        if len(name) > 50:
            raise ValueError("Amenity name must be 50 characters or fewer.")
        self.name = name


    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
        }

    def __str__(self):

        return "Amenity(id={}, name={})".format(self.id, self.name)
