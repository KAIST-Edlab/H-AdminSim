import io
import os
import base64
from PIL import Image
from typing import Tuple


def encode_image(image_path:str, encode_base64:bool=True):
    with open(image_path, "rb") as image_file:
        if encode_base64:
            return base64.b64encode(image_file.read()).decode("utf-8")
        return image_file.read()



def encode_resize_image(image_path:str,
                        max_size:Tuple[int],
                        encode_base64:bool=True):
    with Image.open(image_path) as img:
        original_width, original_height = img.size
        
        # Resize the image
        width_ratio = max_size[0] / original_width
        height_ratio = max_size[1] / original_height
        min_ratio = min(width_ratio, height_ratio)
        
        if min_ratio >= 1:
            return encode_image(image_path, encode_base64)

        new_width = int(original_width * min_ratio)
        new_height = int(original_height * min_ratio)

        img = img.resize((new_width, new_height))

        # Save image to memeory
        img_buffer = io.BytesIO()
        img.save(img_buffer, format="JPEG")
        img_buffer.seek(0)

        if encode_base64:
            return base64.b64encode(img_buffer.read()).decode("utf-8")
        return img_buffer.read()
    


def get_image_extension(path:str):
    ext = os.path.splitext(path)
    if ext == "png":
        return ext
    elif ext in ["jpeg", "jpg"]:
        return "jpeg"
