from registry import Hospital, Department, Doctor
from utils import Information



def padded_int(n: int, total_digit_l: int = 3) -> str:
    """
    Convert an integer to a zero-padded string of length 2.

    Args:
        n (int): The integer to convert.
        total_digit_l (int): The total number of digits in the output string. Default is 3.

    Returns:
        str: The zero-padded string representation of the integer.
    """
    if n < 0:
        raise ValueError("Negative integers are not supported")
    if total_digit_l <= 0:
        raise ValueError("Total digit length must be a positive integer")
    
    return str(n).zfill(total_digit_l)



def to_dict(obj) -> dict:
    """
    Convert an object to a dictionary representation.

    Args:
        obj: The object to convert.

    Returns:
        dict: A dictionary representation of the object.
    """
    if isinstance(obj, Information):
        return {k: to_dict(v) for k, v in obj.__dict__.items()}
    elif isinstance(obj, dict):
        return {k: to_dict(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [to_dict(v) for v in obj]
    else:
        return obj



def convert_info_to_obj(data: Information) -> Hospital:
    """
    Convert an Information object to a Hospital object.

    Args:
        data (Information): The Information object to convert.

    Returns:
        Hospital: A Hospital object constructed from the Information data.
    """
    data = to_dict(data)  # Convert Information to dict for easier access
    
    hospital_obj = Hospital(**data.get('metadata'))
    for department, department_values in data.get('department').items():
        filtered_values1 = {k: v for k, v in department_values.items() if k != 'doctor'}
        department_obj = hospital_obj.add_department(department, **filtered_values1)
        
        for doctor in department_values['doctor']:
            doctor_values = data.get('doctor').get(doctor)
            filtered_values2 = {k: v for k, v in doctor_values.items() if k != 'department'}
            department_obj.add_doctor(doctor, **filtered_values2)
    
    return hospital_obj



def convert_obj_to_info(hospital_obj: Hospital) -> Information:
    """
    Convert a Hospital object to an Information object.

    Args:
        hospital (Hospital): The Hospital object to convert.

    Returns:
        Information: An Information object constructed from the Hospital data.
    """
    filtered_values = {k: v for k, v in hospital_obj.__dict__.items() if k not in ['department', 'time']}
    filtered_values['time'] = Information(**hospital_obj.time)
    metadata = Information(**filtered_values)
    
    department_info, doctor_info = {}, {}
    for department_obj in hospital_obj.department:
        filtered_values = {k: v for k, v in department_obj.__dict__.items() if k not in ['name', 'doctor']}
        filtered_values['doctor'] = [doctor_obj.name for doctor_obj in department_obj.doctor]
        department_info[department_obj.name] = {**filtered_values}
        
        for doctor_obj in department_obj.doctor:
            filtered_values2 = {k: v for k, v in doctor_obj.__dict__.items() if k not in ['name', 'department']}
            filtered_values2['department'] = doctor_obj.department.name
            doctor_info[doctor_obj.name] = {**filtered_values2}

    return Information(metadata=metadata, department=department_info, doctor=doctor_info)
