from typing import Any

class AppError(Exception):
    status_code: int = 500
    error_code: str = 'INTERNAL_ERROR'
    message: str = 'An unexpected error occurred.'

    def __init__(
            self,
            message: str | None = None,
            details: dict[str, Any] | None = None,
    ) -> None:
        self.message = message or self.__class__.message
        self.details = details or {}
        super().__init__(self.message)

class AuthError(AppError):
    status_code = 401
    error_code = 'AUTH_ERROR'
    message = 'Authentication failed.'

class InvalidCredentialsError(AuthError):
    error_code = 'AUTH_INVALID_CREDENTIALS'
    message = 'Invalid credentials.'

class TokenExpiredError(AuthError):
    error_code = 'AUTH_TOKEN_EXPIRED'
    message = 'Token has expired.'

class TokenInvalidError(AuthError):
    error_code = 'AUTH_TOKEN_INVALID'
    message = 'Token is invalid.'

class TokenRevokeError(AuthError):
    error_code = 'AUTH_YOKEN_REVOKE'
    message = 'Token has been revoked.'

class EmailnotVerifiedError(AuthError):
    error_code = 'AUTH_EMAIL_NOT_BERIFIED'
    message = 'Email address is not verified.'

class PermissionDeniedError(AppError):
    status_code = 403
    error_code = 'PERMISSION_DENIED'
    message = 'You do not have permission to perfoem this action.'

class UserNotFoundError(AppError):
    status_code = 404
    error_code = 'USER_NOT_FOUND'
    message = 'User not found.'

class UserEmailAlreadyExistsError(AppError):
    status_code = 409
    error_code = 'USER_EMAIL_ALREADY_EXISTS'
    message = 'A user with this email already exists.'

class UsernameAlreadyExistsError(AppError):
    status_code = 409
    error_code = 'USERNAME_ALREADY_EXISTS'
    message = 'A user with this username already exists.'

class UserInactiveError(AppError):
    status_code = 403
    error_code = 'USER_INACTIVE'
    message = 'User account is inactive.'

class VenueNotFoundError(AppError):
    status_code = 404
    error_code = 'VENUE_NOT_FOUND'
    message = 'Venue not found.'

class VenueInactiveError(AppError):
    status_code = 422
    error_code = 'VENUE_INACTIVE'
    message = 'Venue is not active.'

class ServiceNotFoundError(AppError):
    status_code = 404
    error_code = 'SERVICE_NOT_FOUND'
    message = 'Service not found.'

class ServiceInactiveError(AppError):
    status_code = 422
    error_code = 'SERVICE_INACTIVE'
    message = 'Service is not active'

class ResourceNotFoundError(AppError):
    status_code = 404
    error_code = 'RESOURCE_NOT_FOUND'
    message = 'Resource not found.'


class ResourceNotLinkedError(AppError):
    status_code = 422
    error_code = 'RESOURCE_NOT_LINKED'
    message = 'Resource is not linked to this service.'

class BookingNotFoundError(AppError):
    status_code = 404
    error_code = 'BOOKING_NOT_FOUND'
    message = 'Booking not found.'

class BookingSlotUnavailableError(AppError):
    status_code = 409
    error_code = 'BOOKING_SLOT_UNAVAILABLE'
    message = 'Selected slot is no longer available.'

class BookingInPastError(AppError):
    status_code = 422
    error_code = 'BOOKING_IN_PAST'
    message = 'Cannot book slot in the past.'

class BookingToofarAheadError(AppError):
    status_code = 422
    error_code = 'BOOKING_TOO_FAR_AHEAD'
    message = 'Booking is too far in the future.'

class BookingOutsideWorkingHourError(AppError):
    status_code = 422
    error_code = 'BOOKING_OUTSIDE_WORKING_HOURS'
    message = 'Selected slot is outside working hours.'

class BookingCannotCancelError(AppError):
    status_code = 422
    error_code = 'BOOKING_CANNOT_CANCEl'
    message = 'This booking cannot be cancelled.'

class WaitlistEntryNotFoundError(AppError):
    status_code = 404
    error_code = 'WAITLIST_ENTRY_NOT_FOUND'
    message = 'Waitlist entry not found.'

class WaitlistDuplicateEntryError(AppError):
    status_code = 409
    error_code = 'WAITLIST_DUPLICATE_ENTRY'
    message = 'An active waitlist entry with these params already exists.'

class ReviewNotFoundError(AppError):
    status_code = 404
    error_code = 'REVIEW_ALREDY_EXISTS'
    message = 'Review not found.'

class ReviewAlreadyExistsError(AppError):
    status_code = 409
    error_code = 'REVIEW_ALREADY_EXISTS'
    message = 'You have already this venue for this booking.'

class ReviewNotAllowedError(AppError):
    status_code = 403
    error_code = 'REVIEW_NOT_ALLOWED'
    message = 'you can only review comleted bookings.'