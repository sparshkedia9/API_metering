# Import every model here so that SQLAlchemy's Base "knows" about all tables
# before Base.metadata.create_all() runs in main.py.
from app.models.user import User
