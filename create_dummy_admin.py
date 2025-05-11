from app import create_app, db, bcrypt
from app.models import Admin

# Create a Flask application instance
app = create_app()

# Push an application context
with app.app_context():
    # Create a dummy admin user
    # WARNING: This is dummy data for testing purposes only.
    # Replace with a secure method for creating administrators in a production environment.
    dummy_username = 'admin'
    dummy_password = 'password'
    hashed_password = bcrypt.generate_password_hash(dummy_password).decode('utf-8')

    # Check if admin already exists
    existing_admin = Admin.query.filter_by(username=dummy_username).first()

    if not existing_admin:
        new_admin = Admin(username=dummy_username, password=hashed_password)
        db.session.add(new_admin)
        db.session.commit()
        print(f"Dummy admin '{dummy_username}' created successfully.")
    else:
        print(f"Dummy admin '{dummy_username}' already exists.")

    # Remember to remove or replace this script in a production environment.