from app.models.BaseModel import BaseModel
from app.Extensions import db, bcrypt
import uuid

class User(BaseModel):
    __tablename__ = "users"

    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    #_emails = set()

    def __init__(self, first_name, last_name, email, password, is_admin=False):
        super().__init__()

        if not first_name or len(first_name) > 50:
            raise ValueError("first_name is required and must be <= 50 characters")

        if not last_name or len(last_name) > 50:
            raise ValueError("last_name is required and must be <= 50 characters")
        if not email or len(email) > 100:
            raise ValueError("email is required and must be <= 100 characters")

        if '@' not in email or '.' not in email.split('@')[-1]:
            raise ValueError("email must be a valid email address")

        """if email in User._email:
            raise ValueError("email must be unique")

        User._email.add(email)"""
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            raise ValueError("Email already exists")


        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.is_admin = is_admin
        self.hash_password(password)

    def hash_password(self, password):
            """Hashes the password before storing it."""
            self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def verify_password(self, password):
            """Verifies if the provided password matches the hashed password."""
            return bcrypt.check_password_hash(self.password, password)

    def to_dict(self):
        return {
        "id": str(self.id),
        "first_name": self.first_name,
        "last_name": self.last_name,
        "email": self.email,
        "is_admin": self.is_admin,
        "created_at": self.created_at.isoformat() if hasattr(self, 'created_at') else None,
        "updated_at": self.updated_at.isoformat() if hasattr(self, 'updated_at') else None
    }
