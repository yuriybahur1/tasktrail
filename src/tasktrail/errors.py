class AppError(Exception):
    pass


class DatabaseError(AppError):
    pass


class DatabaseNotInitializedError(DatabaseError):
    pass


class MigrationError(AppError):
    pass


class SchemaCompatibilityError(AppError):
    pass


class ValidationError(AppError):
    pass


class ConflictError(AppError):
    pass
