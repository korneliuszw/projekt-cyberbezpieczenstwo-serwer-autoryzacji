import bcrypt

from database import DbSession
from models import UserModel, Roles

password = "admin123"
email = "admin@admin.com"
login = "admin"

with DbSession() as session:
    admin = UserModel(
        username=login,
        email=email,
        hashed_password=bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()),
        role=Roles.ADMIN
    )
    session.add(admin)
    session.commit()