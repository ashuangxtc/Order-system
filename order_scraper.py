import os
import logging
import time
from playwright.async_api import async_playwright
from utils.imgur_uploader import upload_image_to_imgur

class OrderScraper:
    def __init__(self):
        self.userid = os.getenv("TONGLIAN_COOKIE_USERID")
        self.session = os.getenv("TONGLIAN_COOKIE_SESSION")
        self.orders_url = "https://cus.allinpay.com/tranx/search"
        self.screenshot_dir = "screenshots"
        os.makedirs(self.screenshot_dir, exist_ok=True)

    async def login_with_cookie(self, context):
        page = await context.new_page()
        await page.goto("https://cus.allinpay.com")

        await context.add_cookies([
            {"name": "userid", "value": self.userid, "domain": "cus.allinpay.com", "path": "/"},
            {"name": "SESSION", "value": self.session, "domain": "cus.allinpay.com", "path": "/"}
        ])

        await page.goto(self.orders_url)
        await page.wait_for_load_state("networkidle")

        # 登录成功截图
        login_path = os.path.join(self.screenshot_dir, f"screenshot_login_{int(time.time())}.png")
        await page.screenshot(path=login_path)
        login_imgur = upload_image_to_imgur(login_path)
        print("✅ 登录成功截图：", login_imgur)
        return page

    async def query_orders(self):
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                executable_path="/usr/bin/chromium"
            )
            context = await browser.new_context()

            try:
                page = await self.login_with_cookie(context)

                await page.fill('input[name="startDate"]', time.strftime("%Y-%m-%d"))
                await page.fill('input[name="endDate"]', time.strftime("%Y-%m-%d"))
                await page.click('button:has-text("查询")')
                await page.wait_for_timeout(2000)

                content = await page.content()

                if "交易时间" in content or "金额" in content:
                    order_path = os.path.join(self.screenshot_dir, f"screenshot_orders_{int(time.time())}.png")
                    await page.screenshot(path=order_path)
                    order_imgur = upload_image_to_imgur(order_path)
                    print("📦 抓单成功截图：", order_imgur)

                await browser.close()
                return content

            except Exception as e:
                print("❌ 查询出错：", str(e))
                try:
                    error_path = os.path.join(self.screenshot_dir, f"screenshot_error_{int(time.time())}.png")
                    await page.screenshot(path=error_path)
                    error_imgur = upload_image_to_imgur(error_path)
                    print("⚠️ 报错截图：", error_imgur)
                except:
                    print("⚠️ 报错但截图失败")
                await browser.close()
                return None