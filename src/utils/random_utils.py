import uuid
import random



def random_uuid(is_develop:bool=False) -> str:
    """_summary_

    Args:
        is_develop (bool, optional): _description_. Defaults to False.

    Returns:
        str: _description_
    """
    if is_develop:
        # For development purposes, generate controlled random UUID
        rand_bytes = random.getrandbits(128).to_bytes(16, 'big')
        return str(uuid.UUID(bytes=rand_bytes))
    return str(uuid.uuid1())
