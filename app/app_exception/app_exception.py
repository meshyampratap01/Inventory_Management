class AppException(Exception):
    def __init__(
        self,
        message: str,
        *,
        status_code: int = 400,
        error_code: str = "APP_ERROR",
        details: dict | None = None,
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details
        super().__init__(message)
