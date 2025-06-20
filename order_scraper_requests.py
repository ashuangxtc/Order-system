import os
import logging
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json

class OrderScraperRequests:
    def __init__(self):
        self.username = os.getenv("TONGLIAN_USERNAME")
        self.password = os.getenv("TONGLIAN_PASSWORD")
        self.base_url = "https://cus.allinpay.com"
        self.login_url = "https://cus.allinpay.com/login"
        self.orders_url = "https://cus.allinpay.com/tranx/search"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def login(self):
        """使用用户名密码登录"""
        try:
            # 先尝试直接访问登录页面
            actual_login_url = "https://cus.allinpay.com/login"
            login_page = self.session.get(actual_login_url)
            
            # 保存登录页面用于调试
            with open('login_page_debug.html', 'w', encoding='utf-8') as f:
                f.write(login_page.text)
            
            soup = BeautifulSoup(login_page.text, 'html.parser')
            
            # 查找表单和必要字段
            form = soup.find('form')
            if not form:
                logging.error("❌ 未找到登录表单")
                return False
            
            # 准备登录数据
            login_data = {
                'loginName': self.username,  # 通联可能使用loginName
                'password': self.password,
                'loginType': '1'  # 可能需要指定登录类型
            }
            
            # 查找所有隐藏字段
            hidden_inputs = soup.find_all('input', {'type': 'hidden'})
            for hidden in hidden_inputs:
                name = hidden.get('name')
                value = hidden.get('value')
                if name and value:
                    login_data[name] = value
            
            # 执行登录POST请求
            login_response = self.session.post(actual_login_url, data=login_data)
            
            logging.info(f"登录响应状态: {login_response.status_code}")
            logging.info(f"登录响应URL: {login_response.url}")
            
            # 保存登录响应用于调试
            with open('login_response_debug.html', 'w', encoding='utf-8') as f:
                f.write(login_response.text)
            
            # 检查登录是否成功 - 通过检查响应内容
            response_text = login_response.text
            if ('交易查询' in response_text or 
                'tranx/search' in response_text or 
                '退出登录' in response_text):
                logging.info("✅ 用户名密码登录成功")
                return True
            elif '验证码' in response_text or 'captcha' in response_text.lower():
                logging.error("❌ 登录需要验证码，请手动处理")
                return False
            else:
                logging.error("❌ 登录失败：用户名密码可能错误")
                logging.info(f"响应前200字符: {response_text[:200]}")
                return False
                
        except Exception as e:
            logging.error(f"❌ 登录异常：{e}")
            return False
    
    def login_with_cookie(self):
        """使用环境变量中的Cookie登录"""
        try:
            userid = os.getenv("TONGLIAN_COOKIE_USERID")
            session_id = os.getenv("TONGLIAN_COOKIE_SESSION")
            
            # Cookie为空时直接使用用户名密码登录
            if not userid or not session_id:
                logging.warning("⚠️ Cookie环境变量为空，直接使用用户名密码登录")
                return self.login()
            
            # 如果Cookie存在但为空字符串，也使用用户名密码登录
            if userid.strip() == '' or session_id.strip() == '':
                logging.warning("⚠️ Cookie值为空，直接使用用户名密码登录")
                return self.login()
            
            # 设置Cookie
            self.session.cookies.set('userid', userid, domain='cus.allinpay.com')
            self.session.cookies.set('SESSION', session_id, domain='cus.allinpay.com')
            
            # 测试Cookie是否有效
            test_response = self.session.get(self.orders_url)
            response_text = test_response.text
            
            # 详细检查页面内容
            has_login_elements = ('商户登录' in response_text or 
                                '账号登录' in response_text or 
                                'loginName' in response_text)
            has_order_elements = '交易查询' in response_text
            
            logging.info(f"Cookie测试结果: 登录元素={has_login_elements}, 订单元素={has_order_elements}")
            
            if has_login_elements:
                logging.warning("⚠️ Cookie已失效，检测到登录页面，使用用户名密码登录")
                return self.login()
            elif has_order_elements:
                logging.info("✅ Cookie登录成功，已进入订单查询页面")
                return True
            else:
                logging.warning("⚠️ 页面状态未知，使用用户名密码登录")
                return self.login()
                
        except Exception as e:
            logging.error(f"❌ Cookie登录异常：{e}")
            return self.login()
    
    def fetch_orders(self, start_date=None, end_date=None):
        """抓取订单数据"""
        try:
            if not start_date:
                start_date = time.strftime("%Y-%m-%d")
            if not end_date:
                end_date = start_date
            
            # 构建查询参数
            params = {
                'startDate': start_date,
                'endDate': end_date,
                'pageNum': 1,
                'pageSize': 100
            }
            
            # 发送查询请求
            response = self.session.get(self.orders_url, params=params)
            
            if response.status_code == 200:
                logging.info(f"✅ 成功获取订单页面 ({len(response.text)} 字符)")
                return self.parse_orders(response.text)
            else:
                logging.error(f"❌ 获取订单失败：HTTP {response.status_code}")
                return []
                
        except Exception as e:
            logging.error(f"❌ 抓取订单异常：{e}")
            return []
    
    def parse_orders(self, html_content):
        """解析订单HTML内容"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            orders = []
            
            # 智能解析页面内容 - 查找包含订单信息的文本
            page_text = soup.get_text()
            
            # 保存页面文本内容用于调试
            with open('debug_page_text.txt', 'w', encoding='utf-8') as f:
                f.write(page_text[:5000])  # 保存前5000字符
            
            # 详细检查页面内容
            logging.info(f"📄 页面标题: {soup.title.string if soup.title else '无标题'}")
            logging.info(f"📄 页面前200字符: {page_text[:200]}")
            
            # 检查页面是否包含订单相关关键词
            order_keywords = ['交易时间', '金额', '订单号', '支付方式', '交易状态', '商户订单号', '查询', '交易查询']
            found_keywords = [kw for kw in order_keywords if kw in page_text]
            
            if found_keywords:
                logging.info(f"📦 页面包含订单关键词: {', '.join(found_keywords)}")
                
                # 尝试解析JSON数据（很多现代网站使用AJAX加载数据）
                script_tags = soup.find_all('script')
                for script in script_tags:
                    if script.string and ('data' in script.string or 'list' in script.string):
                        try:
                            # 尝试提取JSON数据
                            import re
                            json_matches = re.findall(r'\{[^{}]*"[^"]*"[^{}]*\}', script.string)
                            for match in json_matches[:3]:  # 只检查前3个匹配
                                try:
                                    data = json.loads(match)
                                    if isinstance(data, dict) and any(key in str(data).lower() for key in ['amount', 'order', 'trade']):
                                        logging.info(f"📋 找到可能的订单JSON数据")
                                        orders.append(data)
                                except:
                                    continue
                        except:
                            continue
                
                # 使用正则表达式查找金额模式
                import re
                amount_pattern = r'[\d,]+\.\d{2}'
                amounts = re.findall(amount_pattern, page_text)
                if amounts:
                    logging.info(f"💰 找到 {len(amounts)} 个金额: {amounts[:5]}")  # 只显示前5个
                    
                    # 创建基于文本解析的订单记录
                    for i, amount in enumerate(amounts[:10]):  # 最多处理10个
                        order_data = {
                            'amount': amount,
                            'order_id': f'parsed_{i+1}',
                            'status': '已解析',
                            'parse_time': time.strftime('%Y-%m-%d %H:%M:%S')
                        }
                        orders.append(order_data)
                
            else:
                logging.warning("⚠️ 页面不包含订单关键词，可能需要登录或页面结构已变化")
                
                # 检查是否是登录页面
                if any(word in page_text.lower() for word in ['login', '登录', 'username', 'password']):
                    logging.error("❌ 页面似乎是登录页面，Cookie可能已失效")
                elif '验证码' in page_text or 'captcha' in page_text.lower():
                    logging.error("❌ 页面要求验证码，需要手动处理")
                
            logging.info(f"✅ 解析到 {len(orders)} 条订单")
            return orders
            
        except Exception as e:
            logging.error(f"❌ 解析订单异常：{e}")
            return []
    
    def query_orders(self):
        """主查询方法"""
        try:
            # 尝试登录
            if not self.login_with_cookie():
                logging.error("❌ 登录失败，无法继续查询")
                return None
            
            # 抓取今日订单
            today = time.strftime("%Y-%m-%d")
            orders = self.fetch_orders(today, today)
            
            if orders:
                logging.info(f"📦 成功抓取 {len(orders)} 条订单")
                # 返回HTML内容用于兼容现有代码
                return f"抓取成功：{len(orders)} 条订单，包含金额等信息"
            else:
                logging.warning("⚠️ 未抓取到订单数据")
                return "未发现订单数据"
                
        except Exception as e:
            logging.error(f"❌ 查询订单异常：{e}")
            return None