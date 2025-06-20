import requests
from bs4 import BeautifulSoup
import datetime
import logging

class OrderScraper:
    def __init__(self, login_url, username=None, password=None, cookie_userid=None, cookie_session=None):
        self.logger = logging.getLogger("order_scraper")
        self.session = requests.Session()
        self.login_url = login_url
        self.logged_in = False

        # 如果有 Cookie，优先使用 Cookie 登录
        if cookie_userid and cookie_session:
            self.session.cookies.set("userid", cookie_userid, domain="cus.allinpay.com")
            self.session.cookies.set("SESSION", cookie_session, domain="cus.allinpay.com")
            self.logged_in = self.check_login()
        elif username and password:
            self.logged_in = self.login(username, password)
        else:
            raise ValueError("必须提供 Cookie 或 用户名和密码 之一")

    def check_login(self):
        """检测当前 Cookie 是否有效"""
        try:
            test_url = "https://cus.allinpay.com/tranx/search"
            response = self.session.get(test_url, timeout=10)
            if "交易查询" in response.text or "订单查询" in response.text:
                return True
            return False
        except Exception as e:
            self.logger.error(f"登录状态检测失败: {e}")
            return False

    def fetch_orders(self):
        """抓取订单数据"""
        try:
            now = datetime.datetime.now()
            start_time = now.strftime("%Y-%m-%d") + " 00:00:00"
            end_time = now.strftime("%Y-%m-%d") + " 23:59:59"

            url = "https://cus.allinpay.com/tranx/search"
            data = {
                "transTimeBegin": start_time,
                "transTimeEnd": end_time,
                "tranxType": "",
                "queryType": "0",
                "pageSize": "10",
                "pageNum": "1"
            }

            response = self.session.post(url, data=data)
            if response.status_code != 200:
                self.logger.warning(f"订单查询失败，状态码: {response.status_code}")
                return []

            soup = BeautifulSoup(response.text, "html.parser")
            rows = soup.select("table tbody tr")

            orders = []
            for row in rows:
                cols = row.find_all("td")
                if len(cols) >= 5:
                    amount_text = cols[4].text.strip().replace("￥", "").replace(",", "")
                    try:
                        amount = float(amount_text)
                    except:
                        amount = 0

                    order = {
                        "order_id": cols[0].text.strip(),
                        "amount": amount,
                        "createdAt": cols[2].text.strip(),
                        "source": "通联支付"
                    }