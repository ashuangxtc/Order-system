#!/usr/bin/env python3
"""
通联支付Cookie获取助手
帮助用户手动登录并获取有效的Cookie用于自动化脚本
"""

import requests
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv

class CookieHelper:
    def __init__(self):
        load_dotenv()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def save_login_page(self):
        """保存登录页面，供用户查看验证码"""
        login_url = "https://cus.allinpay.com/login"
        response = self.session.get(login_url)
        
        # 保存完整登录页面
        with open('manual_login.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        print("✅ 登录页面已保存到 manual_login.html")
        print("📋 请在浏览器中打开此文件查看登录表单")
        
        # 查找验证码图片
        soup = BeautifulSoup(response.text, 'html.parser')
        captcha_imgs = soup.find_all('img', src=lambda x: x and 'captcha' in x.lower())
        
        if captcha_imgs:
            for img in captcha_imgs:
                img_url = img.get('src')
                if img_url.startswith('/'):
                    img_url = 'https://cus.allinpay.com' + img_url
                
                print(f"🔍 验证码图片URL: {img_url}")
                
                # 下载验证码图片
                img_response = self.session.get(img_url)
                if img_response.status_code == 200:
                    with open('captcha.png', 'wb') as f:
                        f.write(img_response.content)
                    print("✅ 验证码图片已保存到 captcha.png")
        
        return self.session.cookies
    
    def test_manual_login(self, username, password, captcha=None):
        """测试手动登录（用于验证登录逻辑）"""
        login_url = "https://cus.allinpay.com/login"
        
        # 获取登录页面
        login_page = self.session.get(login_url)
        soup = BeautifulSoup(login_page.text, 'html.parser')
        
        # 准备登录数据
        login_data = {
            'loginName': username,
            'password': password
        }
        
        if captcha:
            login_data['captcha'] = captcha
        
        # 查找隐藏字段
        hidden_inputs = soup.find_all('input', {'type': 'hidden'})
        for hidden in hidden_inputs:
            name = hidden.get('name')
            value = hidden.get('value')
            if name and value:
                login_data[name] = value
        
        print(f"登录数据: {login_data}")
        
        # 执行登录
        response = self.session.post(login_url, data=login_data)
        
        print(f"登录响应状态: {response.status_code}")
        print(f"登录响应URL: {response.url}")
        
        # 保存响应用于调试
        with open('login_test_response.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        # 检查Cookie
        print("获得的Cookie:")
        for cookie in self.session.cookies:
            print(f"  {cookie.name}: {cookie.value}")
        
        return self.session.cookies
    
    def update_env_cookies(self, cookies):
        """更新环境变量文件中的Cookie"""
        userid = None
        session_id = None
        
        for cookie in cookies:
            if cookie.name.lower() == 'userid':
                userid = cookie.value
            elif cookie.name.upper() == 'SESSION':
                session_id = cookie.value
        
        if userid and session_id:
            # 读取现有环境文件
            with open('user.env', 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # 更新Cookie值
            with open('user.env', 'w', encoding='utf-8') as f:
                for line in lines:
                    if line.startswith('TONGLIAN_COOKIE_USERID='):
                        f.write(f'TONGLIAN_COOKIE_USERID={userid}\n')
                    elif line.startswith('TONGLIAN_COOKIE_SESSION='):
                        f.write(f'TONGLIAN_COOKIE_SESSION={session_id}\n')
                    else:
                        f.write(line)
            
            print(f"✅ Cookie已更新到 user.env 文件")
            print(f"   USERID: {userid}")
            print(f"   SESSION: {session_id}")
            return True
        else:
            print("❌ 未找到有效的Cookie")
            return False

def main():
    """主函数 - 提供交互式Cookie获取工具"""
    helper = CookieHelper()
    
    print("🔧 通联支付Cookie获取助手")
    print("=" * 50)
    
    while True:
        print("\n请选择操作:")
        print("1. 保存登录页面和验证码图片")
        print("2. 测试手动登录")
        print("3. 退出")
        
        choice = input("请输入选择 (1-3): ").strip()
        
        if choice == '1':
            helper.save_login_page()
            print("\n📋 下一步:")
            print("1. 打开保存的 manual_login.html 文件")
            print("2. 查看 captcha.png 验证码图片")
            print("3. 记录登录表单中的所有字段名称")
            print("4. 手动在浏览器中登录并记录Cookie")
            
        elif choice == '2':
            username = input("请输入用户名: ").strip()
            password = input("请输入密码: ").strip()
            captcha = input("请输入验证码 (如果有): ").strip()
            
            cookies = helper.test_manual_login(username, password, captcha if captcha else None)
            
            if input("是否更新环境变量? (y/n): ").lower() == 'y':
                helper.update_env_cookies(cookies)
                
        elif choice == '3':
            break
        else:
            print("无效选择，请重试")

if __name__ == "__main__":
    main()