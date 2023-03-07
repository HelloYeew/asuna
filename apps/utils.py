import string
import random


def random_key(length: int) -> str:
    """Generate a random key."""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
