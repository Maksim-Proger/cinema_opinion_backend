from firebase_admin import db
from firebase_admin.db import TransactionAbortedError


# события об изменениях в Firebase
class ChangesRepository:
    # событие по id, либо None
    @staticmethod
    def get_change(change_id: str) -> dict | None:
        ref = db.reference(f"list_of_changes/{change_id}")
        return ref.get()

    # не используется
    @staticmethod
    def is_processed(change: dict) -> bool:
        return bool(change.get("pushProcessed"))

    # помечает событие обработанным, чтобы пуши не разослались дважды (сейчас всегда возвращает True)
    @staticmethod
    def mark_as_processed(change_id: str) -> bool:
        """
        Атомарно устанавливает pushProcessed: true только если его ещё нет.
        Возвращает True — если применили, False — если уже было true.
        """
        ref = db.reference(f"list_of_changes/{change_id}")

        # ставит pushProcessed=true, если оно ещё не стоит
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
