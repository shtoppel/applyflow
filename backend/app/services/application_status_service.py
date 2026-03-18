from app.models.application import Application


class ApplicationStatusService:
    STATUS_RANK = {
        "draft": 0,
        "sent": 1,
        "in_review": 2,
        "interview": 3,
        "rejected": 4,
        "accepted": 5,
    }

    FINAL_STATUSES = {"rejected", "accepted"}

    @classmethod
    def can_transition(cls, current_status: str, new_status: str) -> bool:
        current = (current_status or "").strip().lower()
        new = (new_status or "").strip().lower()

        if current not in cls.STATUS_RANK or new not in cls.STATUS_RANK:
            return False

        if current in cls.FINAL_STATUSES:
            return False

        if current == new:
            return False

        return cls.STATUS_RANK[new] > cls.STATUS_RANK[current]

    @classmethod
    def apply_status_if_allowed(cls, application: Application, new_status: str) -> bool:
        current_status = application.status

        if cls.can_transition(current_status, new_status):
            application.status = new_status
            return True

        return False