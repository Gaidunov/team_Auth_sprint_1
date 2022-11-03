from functools import wraps
from http import HTTPStatus
from typing import Optional


class AppError(Exception):
    def __init__(
        self,
        status: int,
        error: Optional[str] = None,
        reason: Optional[str] = None,
    ) -> None:
        super().__init__()
        self.status = status
        self.error = error
        self.reason = reason

    def json(self):
        return {
            'status': self.status,
            'error': self.error,
            'reason': self.reason,
        }


class CustomNotFoundError(AppError):
    status = HTTPStatus.NOT_FOUND

    def __init__(
        self,
        reason: Optional[str] = None,
        error: Optional[str] = None,
    ) -> None:
        super().__init__(
            error=error or 'Not found',
            reason=reason,
            status=self.status,
        )


class AlreadyExistsError(AppError):
    status = HTTPStatus.CONFLICT

    def __init__(
        self,
        reason: Optional[str] = None,
        error: Optional[str] = None,
    ) -> None:
        super().__init__(
            error=error or 'Conflict',
            reason=reason,
            status=self.status,
        )


class Forbidden(AppError):
    status = HTTPStatus.FORBIDDEN

    def __init__(
        self,
        reason: Optional[str] = None,
        error: Optional[str] = None,
    ) -> None:
        super().__init__(
            error=error or 'FORBIDDEN',
            reason=reason,
            status=self.status,
        )


def catch_http_errors(func):
    @wraps(func)
    def wrapper(*a, **kw):
        try:
            return func(*a, **kw)
        except (
            CustomNotFoundError,
            AlreadyExistsError,
            Forbidden,
        ) as ex:
            return ex.json(), ex.status
    return wrapper
