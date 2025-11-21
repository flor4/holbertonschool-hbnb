from app.persistence.user_repository import UserRepository
from app.persistence.repository import SQLAlchemyRepository
from app.models.user import User
from app.models.place import Place
from app.models.amenity import Amenity
from app.models.review import Review

class HBnBFacade:
    def __init__(self):
        self.user_repo = UserRepository()
        self.place_repo = SQLAlchemyRepository(Place)
        self.review_repo = SQLAlchemyRepository(Review)
        self.amenity_repo = SQLAlchemyRepository(Amenity)

    # =====================
    # User facade
    # =====================
    def create_user(self, user_data):
        user = User(**user_data)
        user.hash_password(user_data['password'])
        self.user_repo.add(user)
        return user

    def get_user(self, user_id):
        return self.user_repo.get(user_id)

    def get_user_by_email(self, email):
        return self.user_repo.get_user_by_email(email)

    def get_all_users(self):
        return self.user_repo.get_all()

    def update_user(self, user_id, data):
        user = self.user_repo.get(user_id)
        if not user:
            raise ValueError("User not found")
        
        data.pop("id", None)  # ne pas changer l'id
        data.pop("password", None)  # password géré à part si besoin

        for key, value in data.items():
            setattr(user, key, value)

        self.user_repo.update(user_id, data)
        return user

    def delete_user(self, user_id):
        user = self.user_repo.get(user_id)
        if not user:
            raise ValueError("User not found")
        self.user_repo.delete(user_id)

    # =====================
    # Place facade
    # =====================
    def create_place(self, place_data):
        owner_id = place_data.get("owner_id")
        if not owner_id:
            raise ValueError("owner_id is required")
        owner = self.user_repo.get(owner_id)
        if not owner:
            raise ValueError("Owner not found")

        amenities = place_data.get("amenities") or []
        amenities_objs = [self.amenity_repo.get(a_id) for a_id in amenities]

        new_place = Place(
            place_data.get("title"),
            place_data.get("description"),
            place_data.get("price"),
            place_data.get("latitude"),
            place_data.get("longitude"),
            owner_id,
            amenities_objs
        )
        self.place_repo.add(new_place)
        return new_place

    def get_place(self, place_id):
        return self.place_repo.get(place_id)

    def get_all_places(self):
        return self.place_repo.get_all()

    def update_place(self, place_id, data):
        place = self.place_repo.get(place_id)
        if not place:
            raise ValueError("Place not found")

        data.pop("owner_id", None)
        for key, value in data.items():
            setattr(place, key, value)

        self.place_repo.update(place_id, data)
        return place

    def delete_place(self, place_id):
        place = self.place_repo.get(place_id)
        if not place:
            raise ValueError("Place not found")
        self.place_repo.delete(place_id)

    # =====================
    # Review facade
    # =====================
    def create_review(self, review_data):
        user_id = review_data.get('user_id')
        place_id = review_data.get('place_id')
        rating = review_data.get('rating')
        text = review_data.get('text')

        if not user_id or not place_id or rating is None:
            raise ValueError("user_id, place_id, and rating are required")

        if not self.user_repo.get(user_id):
            raise ValueError("User not found.")
        if not self.place_repo.get(place_id):
            raise ValueError("Place not found.")

        if not (1 <= rating <= 5):
            raise ValueError("Rating must be between 1 and 5")

        review = Review(text=text, rating=rating, user_id=user_id, place_id=place_id)
        self.review_repo.add(review)
        return review

    def get_review(self, review_id):
        return self.review_repo.get(review_id)

    def get_all_reviews(self):
        return self.review_repo.get_all()

    # =====================
    # Amenity facade
    # =====================
    def create_amenity(self, amenity_data):
        amenity = Amenity(**amenity_data)
        self.amenity_repo.add(amenity)
        return amenity

    def get_amenity(self, amenity_id):
        return self.amenity_repo.get(amenity_id)

    def get_all_amenities(self):
        return self.amenity_repo.get_all()

    def update_amenity(self, amenity_id, data):
        amenity = self.amenity_repo.get(amenity_id)
        if not amenity:
            raise ValueError("Amenity not found")

        data.pop("id", None)
        for key, value in data.items():
            setattr(amenity, key, value)

        self.amenity_repo.update(amenity_id, data)
        return amenity

    def delete_amenity(self, amenity_id):
        amenity = self.amenity_repo.get(amenity_id)
        if not amenity:
            raise ValueError("Amenity not found")
        self.amenity_repo.delete(amenity_id)

