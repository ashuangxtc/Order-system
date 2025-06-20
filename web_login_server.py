#!/usr/bin/env python3
"""
Web登录服务器 - 提供简单的Web界面处理验证码登录
"""

from flask import Flask, render_template_string, request, jsonify, send_file
import requests
from bs4 import BeautifulSoup
import os
import threading
import time

app = Flask(__name__)

# 全局会话对象
global_session = None
login_success = False

TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>通联支付登录</title>
    <meta charset="utf-8">
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 500px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }
        .btn { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; margin: 5px; }
        .btn:hover { background: #0056b3; }
        .success { background: #d4edda; padding: 15px; border-radius: 5px; color: #155724; margin: 10px 0; }
        .error { background: #f8d7da; padding: 15px; border-radius: 5px; color: #721c24; margin: 10px 0; }
        .form-group { margin: 15px 0; }
        input[type="text"] { width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; }
        img { max-width: 200px; border: 1px solid #ddd; margin: 10px 0; }
    </style>
</head>
<body>
    <div class="container">
        <h2>通联支付登录助手</h2>
        
        <div class="form-group">
            <button class="btn" onclick="getCaptcha()">1. 获取新验证码</button>
        </div>
        
        <div id="captcha-section" style="display:none;">
            <h3>验证码:</h3>
            <img id="captcha-img" src="" />
            
            <div class="form-group">
                <label>请输入验证码:</label>
                <input type="text" id="captcha-input" placeholder="输入验证码" />
            </div>
            
            <button class="btn" onclick="doLogin()">2. 执行登录</button>
        </div>
        
        <div id="result"></div>
    </div>

    <script>
        function getCaptcha() {
            fetch('/get-captcha')
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        document.getElementById('captcha-img').src = '/captcha-image?' + new Date().getTime();
                        document.getElementById('captcha-section').style.display = 'block';
                        document.getElementById('result').innerHTML = '<div class="success">验证码已获取，请输入</div>';
                    } else {
                        document.getElementById('result').innerHTML = '<div class="error">获取验证码失败: ' + data.error + '</div>';
                    }
                });
        }
        
        function doLogin() {
            const captcha = document.getElementById('captcha-input').value;
            if (!captcha) {
                alert('请输入验证码');
                return;
            }
            
            fetch('/do-login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ captcha: captcha })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    document.getElementById('result').innerHTML = '<div class="success">登录成功！Cookie已保存</div>';
                } else {
                    document.getElementById('result').innerHTML = '<div class="error">登录失败: ' + data.error + '</div>';
                }
            });
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(TEMPLATE)

@app.route('/get-captcha')
def get_captcha():
    global global_session
    
    try:
        # 创建新会话
        global_session = requests.Session()
        global_session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # 获取登录页面
        login_url = "https://cus.allinpay.com/login"
        response = global_session.get(login_url)
        
        # 获取验证码
        captcha_url = "https://cus.allinpay.com/getvalidCode?type=cuserrorCode"
        captcha_response = global_session.get(captcha_url)
        
        with open('web_captcha.png', 'wb') as f:
            f.write(captcha_response.content)
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/captcha-image')
def captcha_image():
    return send_file('web_captcha.png', mimetype='image/png')

@app.route('/do-login', methods=['POST'])
def do_login():
    global global_session, login_success
    
    try:
        data = request.get_json()
        captcha = data.get('captcha', '').strip()
        
        if not captcha:
            return jsonify({'success': False, 'error': '验证码不能为空'})
        
        # 重新获取登录页面以获取最新token
        login_url = "https://cus.allinpay.com/login"
        response = global_session.get(login_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 准备登录数据
        login_data = {
            'userid': 'NJYHL013',
            'password': 'Yongrenzrao1',
            'cuserrorCode': captcha,
            'logintype': 'userid'
        }
        
        # 获取token
        token_input = soup.find('input', {'name': 'token'})
        if token_input and token_input.get('value'):
            login_data['token'] = token_input.get('value')
        
        # 执行登录
        login_response = global_session.post(login_url, data=login_data, allow_redirects=False)
        
        # 检查登录结果
        if login_response.status_code in [301, 302]:
            location = login_response.headers.get('Location', '')
            if '/main' in location or 'main' in location or location == '/':
                # 登录成功，保存Cookie
                cookies = dict(global_session.cookies)
                userid = cookies.get('userid')
                session_id = cookies.get('SESSION') or cookies.get('JSESSIONID')
                
                if userid and session_id:
                    save_cookies_to_env(userid, session_id)
                    login_success = True
                    return jsonify({'success': True, 'message': '登录成功，Cookie已保存'})
                else:
                    return jsonify({'success': False, 'error': '未获取到有效Cookie'})
        
        # 检查响应内容
        response_text = login_response.text
        if '验证码' in response_text and ('错误' in response_text or '不正确' in response_text):
            return jsonify({'success': False, 'error': '验证码错误，请重新输入'})
        elif '交易查询' in response_text or '退出' in response_text:
            # 通过页面内容判断登录成功
            cookies = dict(global_session.cookies)
            userid = cookies.get('userid')
            session_id = cookies.get('SESSION') or cookies.get('JSESSIONID')
            
            if userid and session_id:
                save_cookies_to_env(userid, session_id)
                login_success = True
                return jsonify({'success': True, 'message': '登录成功，Cookie已保存'})
        
        return jsonify({'success': False, 'error': '登录失败，请重试'})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

def save_cookies_to_env(userid, session_id):
    """保存Cookie到环境变量文件"""
    env_file = 'user.env'
    
    lines = []
    if os.path.exists(env_file):
        with open(env_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    
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
    
    if not userid_updated:
        new_lines.append(f'TONGLIAN_COOKIE_USERID={userid}\n')
    if not session_updated:
        new_lines.append(f'TONGLIAN_COOKIE_SESSION={session_id}\n')
    
    with open(env_file, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)

if __name__ == '__main__':
    print("启动Web登录服务器...")
    print("访问地址: http://localhost:5000")
    print("使用浏览器打开上述地址完成登录")
    app.run(host='0.0.0.0', port=5000, debug=False)