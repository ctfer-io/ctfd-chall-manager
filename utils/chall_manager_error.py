class ChallManagerException(Exception):
    def __init__(self, code=2, message="An error occurred", details=None):
        self.code = code
        self.message = message
        self.details = details or []  # Default to an empty list if no details are provided
        super().__init__(self.message)

    def __str__(self):
        details_str = f", details: {self.details}" if self.details else ""
        return f"ChallManagerError(code={self.code}, message='{self.message}'{details_str})"
