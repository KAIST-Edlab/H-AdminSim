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



def get_individual_id(hospital: str, department: str, individual_name: str) -> str:
    """
    Make an individual ID.

    Args:
        hospital (str): A hospital name.
        department (str): A department name.
        individual_name (str): An individual name.
    
    Returns:
        str: A sanitized individual ID.
    """
    return sanitize_id(f'{hospital}-{department}-{individual_name}')



def get_practitionerrole_id(individual_id: str) -> str:
    """
    Make a practitioner role ID for an individual.

    Args:
        individual_id (str): An individual ID.

    Returns:
        str: A practitioner role ID.
    """
    return f'{individual_id}-role'



def get_schedule_id(individual_id: str) -> str:
    """
    Make a schedule ID for an individual.

    Args:
        individual_id (str): An individual ID.

    Returns:
        str: A schedule ID.
    """
    return f'{individual_id}-schedule'



def get_slot_id(individual_id: str, time_segment_index: int) -> str:
    """
    Make a slot ID for an individual.

    Args:
        individual_id (str): An individual ID.
        time_segment_index (int): An index of start time segment.

    Returns:
        str: A slot ID.
    """
    return f'{individual_id}-slot{time_segment_index}'



def get_appointment_id(individual_id: str, start_time_segment_index: int, end_time_segment_index: int) -> str:
    """
    Make an appointment ID for an individual.

    Args:
        individual_id (str): An individual ID.
        start_time_segment_index (int): An index of start time segment.
        end_time_segment_index (int): An index of end time segment.

    Returns:
        str: An appointment ID.
    """
    return f'{individual_id}-appn{start_time_segment_index}-{end_time_segment_index}'
