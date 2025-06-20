#!/usr/bin/env python3
"""
验证码获取和登录工具
"""

import requests
from bs4 import BeautifulSoup
import os
import time

class CaptchaTool:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def get_captcha_and_save(self):
        """获取验证码并保存为图片"""
        try:
            login_url = "https://cus.allinpay.com/login"
            response = self.session.get(login_url)
            
            # 保存登录页面用于分析
            with open('login_page.html', 'w', encoding='utf-8') as f:
                f.write(response.text)
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 查找验证码图片
            captcha_found = False
            for img in soup.find_all('img'):
                src = img.get('src', '')
                if any(keyword in src.lower() for keyword in ['captcha', 'code', 'verify', 'kaptcha']):
                    print(f"找到验证码图片: {src}")
                    
                    if src.startswith('/'):
                        src = 'https://cus.allinpay.com' + src
                    
                    # 下载验证码图片
                    img_response = self.session.get(src)
                    if img_response.status_code == 200:
                        with open('captcha.png', 'wb') as f:
                            f.write(img_response.content)
                        print("✅ 验证码图片已保存为 captcha.png")
                        captcha_found = True
                        break
            
            if not captcha_found:
                # 如果没有找到明显的验证码，列出所有图片
                print("未找到明显的验证码图片，所有图片链接:")
                for i, img in enumerate(soup.find_all('img')):
                    src = img.get('src', '')
                    if src:
                        print(f"{i+1}. {src}")
                        
                        # 下载所有可能的图片用于检查
                        if src.startswith('/'):
                            src = 'https://cus.allinpay.com' + src
                        
                        try:
                            img_response = self.session.get(src)
                            if img_response.status_code == 200:
                                filename = f'image_{i+1}.png'
                                with open(filename, 'wb') as f:
                                    f.write(img_response.content)
                                print(f"   已下载: {filename}")
                        except:
                            pass
            
            return True
            
        except Exception as e:
            print(f"获取验证码失败: {e}")
            return False
    
    def login_with_captcha(self, username, password, captcha):
        """使用用户名密码和验证码登录"""
        try:
            login_url = "https://cus.allinpay.com/login"
            
            # 重新获取登录页面以获取最新的表单数据
            login_page = self.session.get(login_url)
            soup = BeautifulSoup(login_page.text, 'html.parser')
            
            # 准备登录数据
            login_data = {
                'loginName': username,
                'password': password,
                'captcha': captcha
            }
            
            # 查找所有隐藏字段
            hidden_inputs = soup.find_all('input', {'type': 'hidden'})
            for hidden in hidden_inputs:
                name = hidden.get('name')
                value = hidden.get('value')
                if name and value:
                    login_data[name] = value
                    print(f"添加隐藏字段: {name} = {value}")
            
            print(f"登录数据: {login_data}")
            
            # 执行登录
            response = self.session.post(login_url, data=login_data)
            
            print(f"登录响应状态: {response.status_code}")
            print(f"登录响应URL: {response.url}")
            
            # 保存登录响应
            with open('login_response.html', 'w', encoding='utf-8') as f:
                f.write(response.text)
            
            # 检查登录结果
            response_text = response.text
            if '交易查询' in response_text and '退出' in response_text:
                print("✅ 登录成功！")
                
                # 获取Cookie
                cookies = {}
                for cookie in self.session.cookies:
                    cookies[cookie.name] = cookie.value
                    print(f"Cookie: {cookie.name} = {cookie.value}")
                
                # 保存Cookie到环境变量文件
                userid = cookies.get('userid')
                session_id = cookies.get('SESSION')
                
                if userid and session_id:
                    self.update_env_file(userid, session_id)
                    print("✅ Cookie已保存到配置文件")
                    return True
                else:
                    print("❌ 未获取到有效Cookie")
                    return False
                    
            elif '验证码' in response_text or 'captcha' in response_text.lower():
                print("❌ 验证码错误，请重新输入")
                return False
            else:
                print("❌ 登录失败，可能是用户名密码错误")
                print(f"响应内容前200字符: {response_text[:200]}")
                return False
                
        except Exception as e:
            print(f"登录过程出错: {e}")
            return False
    
    def update_env_file(self, userid, session_id):
        """更新环境变量文件"""
        try:
            with open('user.env', 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            with open('user.env', 'w', encoding='utf-8') as f:
                for line in lines:
                    if line.startswith('TONGLIAN_COOKIE_USERID='):
                        f.write(f'TONGLIAN_COOKIE_USERID={userid}\n')
                    elif line.startswith('TONGLIAN_COOKIE_SESSION='):
                        f.write(f'TONGLIAN_COOKIE_SESSION={session_id}\n')
                    else:
                        f.write(line)
            return True
        except Exception as e:
            print(f"更新环境变量失败: {e}")
            return False

def main():
    tool = CaptchaTool()
    
    print("🔧 通联支付验证码登录工具")
    print("=" * 40)
    
    # 获取验证码
    print("正在获取验证码...")
    if tool.get_captcha_and_save():
        print("\n📋 请查看当前目录中的验证码图片文件")
        print("   - captcha.png (如果存在)")
        print("   - image_*.png (其他可能的图片)")
        
        # 等待用户输入验证码
        print(f"\n登录信息:")
        print(f"用户名: NJYHL013")
        print(f"密码: Yongrenzrao1")
        
        captcha = input("\n请输入验证码: ").strip()
        
        if captcha:
            print("正在登录...")
            if tool.login_with_captcha("NJYHL013", "Yongrenzrao1", captcha):
                print("\n🎉 登录成功！Cookie已保存，请重启主程序")
            else:
                print("\n❌ 登录失败，请检查验证码或重试")
        else:
            print("未输入验证码")
    else:
        print("获取验证码失败")

if __name__ == "__main__":
    main()