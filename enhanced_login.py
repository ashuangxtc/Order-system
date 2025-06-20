#!/usr/bin/env python3
"""
增强登录工具 - 使用同一会话获取验证码和登录
"""

import requests
from bs4 import BeautifulSoup
import time

def login_with_session():
    # 创建持久会话
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    })
    
    try:
        login_url = "https://cus.allinpay.com/login"
        
        # Step 1: 获取登录页面
        print("Step 1: 获取登录页面...")
        login_page = session.get(login_url)
        soup = BeautifulSoup(login_page.text, 'html.parser')
        
        # Step 2: 获取验证码
        print("Step 2: 获取验证码...")
        captcha_url = "https://cus.allinpay.com/getvalidCode?type=cuserrorCode"
        captcha_response = session.get(captcha_url)
        
        if captcha_response.status_code == 200:
            with open('session_captcha.png', 'wb') as f:
                f.write(captcha_response.content)
            print("验证码已保存为 session_captcha.png")
        
        # Step 3: 手动输入验证码（暂时硬编码，实际应该用OCR或手动输入）
        # 需要用户查看验证码图片并输入
        captcha_code = input("请查看 session_captcha.png 并输入验证码: ").strip()
        
        # Step 4: 准备登录数据
        print("Step 3: 准备登录数据...")
        login_data = {
            'userid': 'NJYHL013',
            'password': 'Yongrenzrao1',
            'cuserrorCode': captcha_code,
            'logintype': 'userid'
        }
        
        # 查找隐藏的token字段
        token_input = soup.find('input', {'name': 'token'})
        if token_input:
            token_value = token_input.get('value')
            login_data['token'] = token_value
            print(f"找到token: {token_value}")
        
        print(f"登录数据: {login_data}")
        
        # Step 5: 执行登录
        print("Step 4: 执行登录...")
        response = session.post(login_url, data=login_data, allow_redirects=False)
        
        print(f"登录响应状态: {response.status_code}")
        print(f"登录响应URL: {response.url}")
        print(f"响应头: {dict(response.headers)}")
        
        # 检查是否有重定向
        if response.status_code in [302, 301]:
            redirect_url = response.headers.get('Location', '')
            print(f"重定向到: {redirect_url}")
            
            if '/main' in redirect_url or 'main' in redirect_url:
                print("✅ 登录成功！检测到重定向到主页")
                
                # 跟随重定向获取主页
                main_response = session.get("https://cus.allinpay.com" + redirect_url if redirect_url.startswith('/') else redirect_url)
                
                # 保存Cookie
                cookies = {}
                for cookie in session.cookies:
                    cookies[cookie.name] = cookie.value
                    print(f"Cookie: {cookie.name} = {cookie.value}")
                
                userid = cookies.get('userid')
                session_id = cookies.get('SESSION')
                
                if userid and session_id:
                    update_env_file(userid, session_id)
                    print("✅ Cookie已保存到配置文件")
                    return True
                else:
                    print("❌ 未获取到有效Cookie")
                    return False
            else:
                print(f"❌ 重定向目标异常: {redirect_url}")
                return False
        
        # 检查登录结果
        response_text = response.text
        if '交易查询' in response_text or '退出' in response_text or 'main' in response.url:
            print("✅ 登录成功！")
            
            # 获取Cookie
            cookies = {}
            for cookie in session.cookies:
                cookies[cookie.name] = cookie.value
                print(f"Cookie: {cookie.name} = {cookie.value}")
            
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
        elif '用户名' in response_text or '密码' in response_text:
            print("❌ 用户名或密码错误")
            return False
        else:
            print("❌ 登录失败")
            print(f"响应内容前500字符: {response_text[:500]}")
            
            # 保存响应内容用于调试
            with open('login_response_debug.html', 'w', encoding='utf-8') as f:
                f.write(response_text)
            print("响应内容已保存到 login_response_debug.html")
            return False
            
    except Exception as e:
        print(f"登录过程出错: {e}")
        import traceback
        traceback.print_exc()
        return False

def update_env_file(userid, session_id):
    """更新环境变量文件"""
    try:
        # 读取现有文件
        try:
            with open('user.env', 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except FileNotFoundError:
            lines = []
        
        # 更新或添加Cookie配置
        updated_lines = []
        userid_found = False
        session_found = False
        
        for line in lines:
            if line.startswith('TONGLIAN_COOKIE_USERID='):
                updated_lines.append(f'TONGLIAN_COOKIE_USERID={userid}\n')
                userid_found = True
            elif line.startswith('TONGLIAN_COOKIE_SESSION='):
                updated_lines.append(f'TONGLIAN_COOKIE_SESSION={session_id}\n')
                session_found = True
            else:
                updated_lines.append(line)
        
        # 如果没找到相关配置，添加新的
        if not userid_found:
            updated_lines.append(f'TONGLIAN_COOKIE_USERID={userid}\n')
        if not session_found:
            updated_lines.append(f'TONGLIAN_COOKIE_SESSION={session_id}\n')
        
        # 写回文件
        with open('user.env', 'w', encoding='utf-8') as f:
            f.writelines(updated_lines)
        
        return True
    except Exception as e:
        print(f"更新环境变量失败: {e}")
        return False

if __name__ == "__main__":
    print("🔐 增强登录工具")
    print("=" * 40)
    if login_with_session():
        print("🎉 登录成功！请重启主程序")
    else:
        print("❌ 登录失败")