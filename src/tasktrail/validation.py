from datetime import date

from tasktrail.errors import ValidationError
from tasktrail.models import Priority


def required_text(value: str, field: str, maximum: int = 120) -> str:
    cleaned = value.strip()

    if not cleaned:
        raise ValidationError(f"{field} must not be empty")

    if len(cleaned) > maximum:
        raise ValidationError(f"{field} must be at most {maximum} characters")

    return cleaned


def optional_text(value: str | None, field: str, maximum: int = 1000) -> str | None:
    if value is None:
        return None

    cleaned = value.strip()

    if not cleaned:
        return None

    if len(cleaned) > maximum:
        raise ValidationError(f"{field} must be at most {maximum} characters")

    return cleaned


def priority(value: str) -> str:
    try:
        return Priority(value).value
    except ValueError as exc:
        raise ValidationError("priority must be low, medium, or high") from exc


def due_date(value: str | None) -> str | None:
    if value is None:
        return None

    try:
        return date.fromisoformat(value).isoformat()
    except ValueError as exc:
        raise ValidationError("due date must use YYYY-MM-DD") from exc
