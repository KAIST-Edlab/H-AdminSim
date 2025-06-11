import json



def txt_load(path: str):
    with open(path, 'r') as f:
        content = f.read()
    return content    


def json_load(path: str):
    with open(path, 'r') as f:
        return json.load(f)