import bcrypt

from database import DbSession
from models import UserModel, Roles

admin_password = "admin1234"
admin_email = "admin@admin.com"
admin_login = "admin"

manager_password = "manager123"
manager_email = "manager@company.com"
manager_login = "manager"

employee_password = "employee123"
employee_email = "employee@company.com"
employee_login = "employee"

manager2_password = "manager2123"
manager2_email = "manager2@company.com"
manager2_login = "manager2"

with DbSession() as session:
    admin = UserModel(
        username=admin_login,
        email=admin_email,
        hashed_password=bcrypt.hashpw(admin_password.encode("utf-8"), bcrypt.gensalt()),
        role=Roles.ADMIN,
        restaurant="ADMIN",
    )
    session.add(admin)

    manager = UserModel(
        username=manager_login,
        email=manager_email,
        hashed_password=bcrypt.hashpw(
            manager_password.encode("utf-8"), bcrypt.gensalt()
        ),
        role=Roles.MANAGER,
        restaurant="GDA01",
    )
    session.add(manager)

    employee = UserModel(
        username=employee_login,
        email=employee_email,
        hashed_password=bcrypt.hashpw(
            employee_password.encode("utf-8"), bcrypt.gensalt()
        ),
        role=Roles.EMPLOYEE,
        restaurant="GDA01",
    )
    session.add(employee)

    manager2 = UserModel(
        username=manager2_login,
        email=manager2_email,
        hashed_password=bcrypt.hashpw(
            manager2_password.encode("utf-8"), bcrypt.gensalt()
        ),
        role=Roles.MANAGER,
        restaurant="GDA02",
    )
    session.add(manager2)

    session.commit()
