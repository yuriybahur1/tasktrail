from tasktrail.errors import ValidationError


def required_text(value: str, field: str, maximum: int = 120) -> str:
    cleaned = value.strip()

    if not cleaned:
        raise ValidationError(f"{field} must not be empty")

    if len(cleaned) > maximum:
        raise ValidationError(f"{field} must be at most {maximum} characters")

    return cleaned
