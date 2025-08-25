import secrets
import string
def generate_recovery_code(length: int = 6) -> str:
    characters = string.ascii_uppercase + string.digits  # A-Z and 0-9
    return ''.join(secrets.choice(characters) for _ in range(length))

def generate_temporary_password(length: int = 10) -> str:
    """Genera una contraseña provisional segura."""
    characters = string.ascii_letters + string.digits + "!@#$%^&*()-_=+"
    password = ''.join(secrets.choice(characters) for _ in range(length))
    return password