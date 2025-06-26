import re



def sanitize_id(s: str) -> str:
    """
    Sanitize a string to conform to the pattern: ^[A-Za-z0-9\-\.]{1,64}$

    Args:
        s (str): The input string to sanitize.

    Returns:
        str: A sanitized string containing only allowed characters,
             and no longer than 64 characters.
    """
    cleaned = re.sub(r'[^A-Za-z0-9\-\.]', '', s)
    return cleaned[:64]