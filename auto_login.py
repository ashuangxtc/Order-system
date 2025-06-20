#!/usr/bin/env python3
"""
自动登录脚本 - 使用当前验证码
"""

import requests
from bs4 import BeautifulSoup
import os

def login_with_current_captcha():
    """使用当前验证码登录"""
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Connection': 'keep-alive',
        'Referer': 'https://cus.allinpay.com/login'
    })
    
    try:
        # 获取登录页面
        login_url = "https://cus.allinpay.com/login"
        print("获取登录页面...")
        response = session.get(login_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 使用识别的验证码
        captcha_code = "h2Ea"
        print(f"使用验证码: {captcha_code}")
        
        # 准备登录数据
        login_data = {
            'userid': 'NJYHL013',
            'password': 'Yongrenzrao1',
            'cuserrorCode': captcha_code,
            'logintype': 'userid'
        }
        
        # 获取token
        token_input = soup.find('input', {'name': 'token'})
        if token_input and token_input.get('value'):
            login_data['token'] = token_input.get('value')
            print(f"Token: {token_input.get('value')}")
        
        print("执行登录...")
        login_response = session.post(login_url, data=login_data, allow_redirects=False)
        
        print(f"状态码: {login_response.status_code}")
        print(f"响应URL: {login_response.url}")
        
        # 检查重定向
        if login_response.status_code in [301, 302]:
            location = login_response.headers.get('Location', '')
            print(f"重定向: {location}")
            
            if '/main' in location or 'main' in location or location == '/':
                print("登录成功！")
                
                # 跟随重定向
                if location.startswith('/'):
                    full_url = 'https://cus.allinpay.com' + location
                else:
                    full_url = location
                
                main_response = session.get(full_url)
                
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
        if '验证码' in response_text and ('错误' in response_text or '不正确' in response_text):
            print("验证码错误")
            return False
        elif '密码' in response_text and ('错误' in response_text or '不正确' in response_text):
            print("密码错误")
            return False
        elif '交易查询' in response_text or '退出' in response_text:
            print("登录成功（通过页面内容判断）")
            
            # 获取并保存Cookie
            cookies = dict(session.cookies)
            userid = cookies.get('userid')
            session_id = cookies.get('SESSION') or cookies.get('JSESSIONID')
            
            if userid and session_id:
                save_cookies(userid, session_id)
                print("Cookie已保存到配置文件！")
                return True
            else:
                print("未找到有效Cookie")
                return False
        else:
            print("登录状态未知")
            # 保存响应用于调试
            with open('login_debug_auto.html', 'w', encoding='utf-8') as f:
                f.write(response_text)
            print("响应已保存到 login_debug_auto.html")
            return False
            
    except Exception as e:
        print(f"登录出错: {e}")
        import traceback
        traceback.print_exc()
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
    print("通联支付自动登录")
    print("使用验证码: h2Ea")
    print("-" * 40)
    
    success = login_with_current_captcha()
    
    if success:
        print("\n登录成功！现在可以运行主程序抓取订单了")
    else:
        print("\n登录失败")