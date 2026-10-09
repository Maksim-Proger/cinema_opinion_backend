import firebase_admin
from firebase_admin import credentials

from project.utils.config import settings


# подключается к Firebase, если ещё не подключён
def init_firebase():
    if not firebase_admin._apps:
        cred = credentials.Certificate(settings.firebase_cred_path)
        firebase_admin.initialize_app(
            cred,
            {"databaseURL": settings.firebase_db_url}
        )
