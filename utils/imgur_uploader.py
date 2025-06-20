
import requests
import base64
import os
import time
import logging

def upload_image_to_imgur(image_path, client_id=None):
    client_id = client_id or os.getenv("IMGUR_CLIENT_ID")
    if not client_id:
        raise ValueError("IMGUR_CLIENT_ID is not set in environment variables")

    with open(image_path, "rb") as f:
        encoded_image = base64.b64encode(f.read()).decode("utf-8")

    headers = {
        "Authorization": f"Client-ID {client_id}"
    }

    data = {
        "image": encoded_image,
        "type": "base64",
        "name": f"screenshot_{int(time.time())}.png",
        "title": "Screenshot Upload"
    }

    try:
        response = requests.post("https://api.imgur.com/3/image", headers=headers, data=data)
        response.raise_for_status()
        return response.json()["data"]["link"]
    except Exception as e:
        logging.error(f"Imgur upload failed: {e}")
        return None
