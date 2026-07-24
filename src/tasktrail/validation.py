from tasktrail.errors import ValidationError


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
