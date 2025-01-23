import base64
import logging
import shutil
from flask import send_file, make_response


def encode_image(image):
    file_content = image.read()
    return base64.b64encode(file_content).decode('utf-8')

def send_file_with_attachment(file_path: str, filename: str):
    response = make_response(send_file(file_path))
    response.headers["Content-Disposition"] = f"attachment; filename={filename}"
    return response
