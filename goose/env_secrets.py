from dotenv import load_dotenv
import os

load_dotenv()

def get_secret(key: str) -> str:
    var = os.getenv(key)
    if not var:
        raise MissingSecretError(key)
    return var

class MissingSecretError(BaseException):
    """Exception raised when a secret is not found.

    Attributes:
        key -- key of the secret
        message -- explanation of the error
    """

    def __init__(self, key: str, message: str | None = None):
        self.key = key
        self.message = message or self.key + ' not found'
        super().__init__(self.message)