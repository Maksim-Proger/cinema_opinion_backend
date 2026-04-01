from firebase_admin import db

class UserRepository:
    class UserRepository:
        @staticmethod
        def find_users_by_shared_list(shared_list_id: str) -> list[str]:
            ref = db.reference("shared_lists")
            snapshot = ref.get()

            if not snapshot:
                return []

            for node_key, node_data in snapshot.items():
                if node_data.get("listId") == shared_list_id:
                    users = node_data.get("users")
                    if not users:
                        return []
                    return list(users.keys())

            return []
