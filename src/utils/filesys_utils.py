import os
import json



def txt_load(path: str):
    with open(path, 'r') as f:
        content = f.read()
    return content    


def json_load(path: str):
    with open(path, 'r') as f:
        return json.load(f)
    

def get_files(path:str, ext:str=None) -> list[str]:
    """
    Get all files in a directory with a specific extension.

    Args:
        path (str): Folder path to search for files.
        ext (str, optional): Extension that you want to filter. Defaults to None.

    Raises:
        ValueError: _description_

    Returns:
        list[str]: List of file paths that match the given extension.
    """
    if not os.path.isdir(path):
        raise ValueError(f"Path {path} is not a directory.")
    
    files = []
    for root, _, filenames in os.walk(path):
        for filename in filenames:
            if ext is None or filename.endswith(ext):
                files.append(os.path.join(root, filename))
    
    return files