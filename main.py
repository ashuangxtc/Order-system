
import os
import time
import logging
from dotenv import load_dotenv
from order_scraper_requests import OrderScraperRequests
from firebase_sync import FirebaseSync
from product_matcher import ProductMatcher

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("main")

def run():
    """启动Web登录助手"""
    print("=== 通联支付Web登录助手 ===")
    print()
    print("正在启动登录界面...")
    
    try:
        from simple_web_login import app
        print("Web登录界面已启动")
        print("请在浏览器中访问以下地址完成登录：")
        print("http://localhost:5000")
        print()
        print("使用说明：")
        print("1. 点击'获取验证码'按钮")
        print("2. 查看验证码图片并输入")
        print("3. 点击'登录'完成验证")
        print("4. 登录成功后Cookie会自动保存")
        print()
        print("账号信息：")
        print("用户名：NJYHL013")
        print("密码：Yongrenzrao1")
        print()
        
        # 启动Flask应用
        app.run(host='0.0.0.0', port=5000, debug=False)
        
    except Exception as e:
        print(f"Web界面启动失败：{e}")
        print("回退到订单抓取模式...")
        
        # 回退到原有的订单抓取功能
        logger.info("🍔 通联支付订单同步系统")
        logger.info(f"🕰️ 启动时间：{time.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("🛠️ 初始化服务组件...")

        load_dotenv()
        firebase = FirebaseSync()
        matcher = ProductMatcher()
        scraper = OrderScraperRequests()

        while True:
            try:
                logger.info(f"📅 当前日期：{time.strftime('%Y-%m-%d')}")
                logger.info("🔍 正在抓取订单数据...")

                html = scraper.query_orders()
                if html and "金额" in html:
                    logger.info("✅ 抓取成功，截图已上传")
                else:
                    logger.warning("⚠️ 未发现订单或页面异常，已截图上传")

            except Exception as e:
                logger.error(f"❌ 主循环异常：{e}")

            time.sleep(int(os.getenv("SYNC_INTERVAL", 60)))

if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        print("🛑 已手动停止同步任务")
