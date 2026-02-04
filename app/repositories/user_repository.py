from firebase_admin import db
class UserRepository:
    """
    Работа с пользователями в RTDB.
    """
    @staticmethod
    def find_users_by_shared_list(shared_list_id: str) -> list[str]:
        """
        Возвращает список userKey (ключей в users),
        у которых есть my_shared_list с указанным sharedListId.
        """
        users_ref = db.reference("users")
        users_snapshot = users_ref.get()
        if not users_snapshot:
            return []
        matched_user_keys: list[str] = []
        for user_key, user_data in users_snapshot.items():
            shared_lists = user_data.get("my_shared_list")
            if not shared_lists:
                continue
            for item in shared_lists.values():
                if item.get("listId") == shared_list_id:
                    matched_user_keys.append(user_key)
                    break
        return matched_user_keys
