#!/usr/bin/env python3
"""
直接登录工具
"""

import requests
from bs4 import BeautifulSoup

def login_with_captcha():
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    })
    
    try:
        login_url = "https://cus.allinpay.com/login"
        
        # 获取登录页面
        login_page = session.get(login_url)
        soup = BeautifulSoup(login_page.text, 'html.parser')
        
        # 准备登录数据
        login_data = {
            'userid': 'NJYHL013',
            'password': 'Yongrenzrao1',
            'cuserrorCode': '5lB5'
        }
        
        # 查找隐藏字段
        for hidden in soup.find_all('input', {'type': 'hidden'}):
            name = hidden.get('name')
            value = hidden.get('value')
            if name and value:
                login_data[name] = value
                print(f"添加隐藏字段: {name} = {value}")
        
        print(f"登录数据: {login_data}")
        
        # 执行登录
        response = session.post(login_url, data=login_data)
        
        print(f"登录响应状态: {response.status_code}")
        print(f"登录响应URL: {response.url}")
        
        # 检查登录结果
        response_text = response.text
        if '交易查询' in response_text and '退出' in response_text:
            print("✅ 登录成功！")
            
            # 获取Cookie
            cookies = {}
            for cookie in session.cookies:
                cookies[cookie.name] = cookie.value
                print(f"Cookie: {cookie.name} = {cookie.value}")
            
            # 保存Cookie到环境变量文件
            userid = cookies.get('userid')
            session_id = cookies.get('SESSION')
            
            if userid and session_id:
                update_env_file(userid, session_id)
                print("✅ Cookie已保存到配置文件")
                return True
            else:
                print("❌ 未获取到有效Cookie")
                return False
                
        elif '验证码' in response_text or 'captcha' in response_text.lower():
            print("❌ 验证码错误")
            return False
        else:
            print("❌ 登录失败")
            print(f"响应内容前500字符: {response_text[:500]}")
            return False
            
    except Exception as e:
        print(f"登录过程出错: {e}")
        return False

def update_env_file(userid, session_id):
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

if __name__ == "__main__":
    print("正在使用验证码 5lB5 登录...")
    if login_with_captcha():
        print("🎉 登录成功！请重启主程序")
    else:
        print("❌ 登录失败")