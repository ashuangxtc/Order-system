import requests
import os

IMGUR_CLIENT_ID = "54be774f2217634"

def upload_to_imgur(image_path):
    headers = {"Authorization": f"Client-ID {IMGUR_CLIENT_ID}"}
    with open(image_path, "rb") as f:
        image_data = f.read()
    response = requests.post(
        "https://api.imgur.com/3/image",
        headers=headers,
        files={"image": image_data}
    )
    if response.status_code == 200:
        return response.json()["data"]["link"]
    else:
        raise Exception(f"Imgur 上传失败：{response.text}")