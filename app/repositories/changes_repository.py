from firebase_admin import db
from firebase_admin.db import TransactionAbortedError

class ChangesRepository:
    @staticmethod
    def get_change(change_id: str) -> dict | None:
        ref = db.reference(f"list_of_changes/{change_id}")
        return ref.get()

    @staticmethod
    def is_processed(change: dict) -> bool:
        return bool(change.get("pushProcessed"))

    @staticmethod
    def mark_as_processed(change_id: str) -> bool:
        """
        Атомарно устанавливает pushProcessed: true только если его ещё нет.
        Возвращает True — если применили, False — если уже было true.
        """
        ref = db.reference(f"list_of_changes/{change_id}")

        def transaction_handler(current):
            if current is None:
                return None  # событие удалено
            if current.get("pushProcessed"):
                return current  # уже обработано — не меняем
            current["pushProcessed"] = True
            return current

        try:
            committed = ref.transaction(transaction_handler)
            return committed is not None and committed.get("pushProcessed") is True
        except TransactionAbortedError:
            return False

