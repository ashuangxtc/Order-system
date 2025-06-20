#!/usr/bin/env python3
"""
手动验证码登录工具
"""

import requests
from bs4 import BeautifulSoup
import os

def get_fresh_captcha_and_login():
    """获取新验证码并完成登录"""
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Connection': 'keep-alive'
    })
    
    try:
        # 1. 获取登录页面
        login_url = "https://cus.allinpay.com/login"
        print("获取登录页面...")
        response = session.get(login_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 2. 获取最新验证码
        print("下载验证码...")
        captcha_url = "https://cus.allinpay.com/getvalidCode?type=cuserrorCode"
        captcha_response = session.get(captcha_url)
        
        with open('current_captcha.png', 'wb') as f:
            f.write(captcha_response.content)
        print("验证码已保存为 current_captcha.png")
        
        # 3. 显示验证码内容（需要手动输入）
        print("\n" + "="*50)
        print("请打开 current_captcha.png 查看验证码")
        print("="*50)
        
        captcha_input = input("请输入验证码: ").strip()
        
        # 4. 准备登录数据
        login_data = {
            'userid': 'NJYHL013',
            'password': 'Yongrenzrao1',
            'cuserrorCode': captcha_input,
            'logintype': 'userid'
        }
        
        # 获取token
        token_input = soup.find('input', {'name': 'token'})
        if token_input and token_input.get('value'):
            login_data['token'] = token_input.get('value')
            print(f"Token: {token_input.get('value')}")
        
        print(f"登录数据: {login_data}")
        
        # 5. 执行登录
        print("正在登录...")
        login_response = session.post(login_url, data=login_data, allow_redirects=False)
        
        print(f"状态码: {login_response.status_code}")
        print(f"响应URL: {login_response.url}")
        
        # 检查重定向
        if login_response.status_code in [301, 302]:
            location = login_response.headers.get('Location', '')
            print(f"重定向: {location}")
            
            if '/main' in location or 'main' in location:
                print("登录成功！")
                
                # 获取并保存Cookie
                cookies = dict(session.cookies)
                print("获取到的Cookie:")
                for name, value in cookies.items():
                    print(f"  {name}: {value}")
                
                userid = cookies.get('userid')
                session_id = cookies.get('SESSION') or cookies.get('JSESSIONID')
                
                if userid and session_id:
                    save_cookies(userid, session_id)
                    print("Cookie已保存到配置文件！")
                    return True
                else:
                    print("未找到有效Cookie")
                    return False
        
        # 检查响应内容
        response_text = login_response.text
        if '验证码' in response_text and '错误' in response_text:
            print("验证码错误，请重试")
            return False
        elif '登录' in response_text and 'userid' in response_text:
            print("登录失败，可能是用户名密码错误")
            return False
        else:
            print("登录状态未知")
            # 保存响应用于调试
            with open('login_debug.html', 'w', encoding='utf-8') as f:
                f.write(response_text)
            print("响应已保存到 login_debug.html")
            return False
            
    except Exception as e:
        print(f"登录出错: {e}")
        return False

def save_cookies(userid, session_id):
    """保存Cookie到配置文件"""
    env_file = 'user.env'
    
    # 读取现有配置
    lines = []
    if os.path.exists(env_file):
        with open(env_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    
    # 更新配置
    new_lines = []
    userid_updated = False
    session_updated = False
    
    for line in lines:
        if line.startswith('TONGLIAN_COOKIE_USERID='):
            new_lines.append(f'TONGLIAN_COOKIE_USERID={userid}\n')
            userid_updated = True
        elif line.startswith('TONGLIAN_COOKIE_SESSION='):
            new_lines.append(f'TONGLIAN_COOKIE_SESSION={session_id}\n')
            session_updated = True
        else:
            new_lines.append(line)
    
    # 添加新配置
    if not userid_updated:
        new_lines.append(f'TONGLIAN_COOKIE_USERID={userid}\n')
    if not session_updated:
        new_lines.append(f'TONGLIAN_COOKIE_SESSION={session_id}\n')
    
    # 写入文件
    with open(env_file, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)

if __name__ == "__main__":
    print("通联支付手动登录工具")
    print("账号: NJYHL013")
    print("密码: Yongrenzrao1")
    print("-" * 40)
    
    success = get_fresh_captcha_and_login()
    
    if success:
        print("\n✅ 登录成功！现在可以运行主程序抓取订单了")
        print("运行命令: python main.py")
    else:
        print("\n❌ 登录失败，请检查验证码输入是否正确")