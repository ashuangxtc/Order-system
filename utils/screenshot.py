import os
import base64
import requests
import logging

logger = logging.getLogger("order_sync")

def upload_screenshot(page, title="截图"):
    try:
        buffer = page.screenshot()
        b64_image = base64.b64encode(buffer).decode("utf-8")

        client_id = os.getenv("IMGUR_CLIENT_ID")
        if not client_id:
            logger.warning("⚠️ 未设置 IMGUR_CLIENT_ID，无法上传截图")
            return None

        headers = {"Authorization": f"Client-ID {client_id}"}
        data = {"image": b64_image, "title": title}
        response = requests.post("https://api.imgur.com/3/image", headers=headers, data=data)

        if response.status_code == 200:
            img_url = response.json()["data"]["link"]
            logger.warning(f"📸 截图上传成功：{img_url}")
            return img_url
        else:
            logger.error(f"❌ 截图上传失败：{response.text}")
            return None

    except Exception as e:
        logger.error(f"❌ 上传截图时发生异常: {str(e)}")
        return None