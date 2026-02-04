import firebase_admin
from firebase_admin import credentials, db
from app.core.config import settings

def init_firebase():
    if not firebase_admin._apps:
        cred = credentials.Certificate(settings.firebase_cred_path)
        firebase_admin.initialize_app(
            cred,
            {"databaseURL": settings.firebase_db_url}
        )
