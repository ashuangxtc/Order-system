#!/usr/bin/env python3
"""
通联支付Cookie获取Web助手
提供简单的Web界面帮助获取有效Cookie
"""

from flask import Flask, render_template_string, request, jsonify, redirect, url_for
import requests
from bs4 import BeautifulSoup
import os
import base64

app = Flask(__name__)

# HTML模板
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>通联支付Cookie获取助手</title>
    <meta charset="utf-8">
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .container { max-width: 800px; margin: 0 auto; }
        .card { border: 1px solid #ddd; padding: 20px; margin: 10px 0; border-radius: 5px; }
        .success { background-color: #d4edda; border-color: #c3e6cb; }
        .error { background-color: #f8d7da; border-color: #f5c6cb; }
        .warning { background-color: #fff3cd; border-color: #ffeaa7; }
        input, button { padding: 8px; margin: 5px; }
        button { background-color: #007bff; color: white; border: none; cursor: pointer; }
        button:hover { background-color: #0056b3; }
        .captcha-img { max-width: 200px; margin: 10px 0; }
        pre { background-color: #f8f9fa; padding: 10px; border-radius: 3px; }
        .step { margin: 10px 0; padding: 10px; background-color: #f8f9fa; border-left: 4px solid #007bff; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔧 通联支付Cookie获取助手</h1>
        
        <div class="card warning">
            <h3>📋 使用说明</h3>
            <div class="step">
                <strong>步骤1:</strong> 点击"获取登录页面"查看当前登录状态
            </div>
            <div class="step">
                <strong>步骤2:</strong> 如果需要验证码，请输入验证码后登录
            </div>
            <div class="step">
                <strong>步骤3:</strong> 登录成功后，Cookie会自动更新到系统配置
            </div>
        </div>

        <div class="card">
            <h3>🔍 当前状态检查</h3>
            <button onclick="checkStatus()">检查登录状态</button>
            <button onclick="getCaptcha()">获取验证码</button>
            <div id="status-result"></div>
        </div>

        <div class="card">
            <h3>🔑 手动登录</h3>
            <form onsubmit="submitLogin(event)">
                <div>
                    <label>用户名:</label>
                    <input type="text" id="username" value="{{username}}" required>
                </div>
                <div>
                    <label>密码:</label>
                    <input type="password" id="password" value="{{password}}" required>
                </div>
                <div id="captcha-section" style="display:none;">
                    <label>验证码:</label>
                    <input type="text" id="captcha" placeholder="请输入验证码">
                    <div id="captcha-display"></div>
                </div>
                <button type="submit">登录</button>
            </form>
            <div id="login-result"></div>
        </div>

        <div class="card">
            <h3>🍪 Cookie管理</h3>
            <button onclick="showCurrentCookies()">显示当前Cookie</button>
            <button onclick="testCookies()">测试Cookie有效性</button>
            <div id="cookie-result"></div>
        </div>

        <div class="card">
            <h3>⚙️ 系统配置</h3>
            <button onclick="updateConfig()">更新配置文件</button>
            <button onclick="restartSystem()">重启抓单系统</button>
            <div id="config-result"></div>
        </div>
    </div>

    <script>
        async function checkStatus() {
            const result = document.getElementById('status-result');
            result.innerHTML = '检查中...';
            
            try {
                const response = await fetch('/api/status');
                const data = await response.json();
                
                if (data.success) {
                    result.innerHTML = `<div class="success">✅ ${data.message}</div>`;
                } else {
                    result.innerHTML = `<div class="error">❌ ${data.message}</div>`;
                    if (data.needCaptcha) {
                        document.getElementById('captcha-section').style.display = 'block';
                    }
                }
            } catch (error) {
                result.innerHTML = `<div class="error">❌ 检查失败: ${error.message}</div>`;
            }
        }

        async function getCaptcha() {
            try {
                const response = await fetch('/api/captcha');
                const data = await response.json();
                
                if (data.success) {
                    document.getElementById('captcha-section').style.display = 'block';
                    document.getElementById('captcha-display').innerHTML = 
                        `<img src="data:image/png;base64,${data.captcha}" class="captcha-img" alt="验证码">`;
                } else {
                    alert('获取验证码失败: ' + data.message);
                }
            } catch (error) {
                alert('获取验证码失败: ' + error.message);
            }
        }

        async function submitLogin(event) {
            event.preventDefault();
            const result = document.getElementById('login-result');
            result.innerHTML = '登录中...';
            
            const formData = {
                username: document.getElementById('username').value,
                password: document.getElementById('password').value,
                captcha: document.getElementById('captcha').value
            };
            
            try {
                const response = await fetch('/api/login', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(formData)
                });
                const data = await response.json();
                
                if (data.success) {
                    result.innerHTML = `<div class="success">✅ ${data.message}</div>`;
                    if (data.cookies) {
                        result.innerHTML += `<pre>获得Cookie: ${JSON.stringify(data.cookies, null, 2)}</pre>`;
                    }
                } else {
                    result.innerHTML = `<div class="error">❌ ${data.message}</div>`;
                }
            } catch (error) {
                result.innerHTML = `<div class="error">❌ 登录失败: ${error.message}</div>`;
            }
        }

        async function showCurrentCookies() {
            try {
                const response = await fetch('/api/cookies');
                const data = await response.json();
                document.getElementById('cookie-result').innerHTML = 
                    `<pre>${JSON.stringify(data, null, 2)}</pre>`;
            } catch (error) {
                document.getElementById('cookie-result').innerHTML = 
                    `<div class="error">❌ 获取Cookie失败: ${error.message}</div>`;
            }
        }

        async function testCookies() {
            const result = document.getElementById('cookie-result');
            result.innerHTML = '测试中...';
            
            try {
                const response = await fetch('/api/test-cookies');
                const data = await response.json();
                
                if (data.success) {
                    result.innerHTML = `<div class="success">✅ ${data.message}</div>`;
                } else {
                    result.innerHTML = `<div class="error">❌ ${data.message}</div>`;
                }
            } catch (error) {
                result.innerHTML = `<div class="error">❌ 测试失败: ${error.message}</div>`;
            }
        }

        async function updateConfig() {
            try {
                const response = await fetch('/api/update-config', {method: 'POST'});
                const data = await response.json();
                
                const result = document.getElementById('config-result');
                if (data.success) {
                    result.innerHTML = `<div class="success">✅ ${data.message}</div>`;
                } else {
                    result.innerHTML = `<div class="error">❌ ${data.message}</div>`;
                }
            } catch (error) {
                document.getElementById('config-result').innerHTML = 
                    `<div class="error">❌ 更新失败: ${error.message}</div>`;
            }
        }

        async function restartSystem() {
            try {
                const response = await fetch('/api/restart', {method: 'POST'});
                const data = await response.json();
                
                const result = document.getElementById('config-result');
                result.innerHTML = `<div class="success">✅ ${data.message}</div>`;
            } catch (error) {
                document.getElementById('config-result').innerHTML = 
                    `<div class="error">❌ 重启失败: ${error.message}</div>`;
            }
        }
    </script>
</body>
</html>
"""

class TonglianSession:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def get_login_page(self):
        """获取登录页面"""
        login_url = "https://cus.allinpay.com/login"
        response = self.session.get(login_url)
        return response

    def get_captcha(self):
        """获取验证码图片"""
        try:
            login_response = self.get_login_page()
            soup = BeautifulSoup(login_response.text, 'html.parser')
            
            # 查找验证码图片
            captcha_imgs = soup.find_all('img')
            for img in captcha_imgs:
                src = img.get('src', '')
                if 'captcha' in src.lower() or 'code' in src.lower():
                    if src.startswith('/'):
                        src = 'https://cus.allinpay.com' + src
                    
                    img_response = self.session.get(src)
                    if img_response.status_code == 200:
                        return base64.b64encode(img_response.content).decode()
            
            return None
        except Exception as e:
            return None

    def login(self, username, password, captcha=None):
        """执行登录"""
        login_url = "https://cus.allinpay.com/login"
        
        # 获取登录页面和表单数据
        login_page = self.get_login_page()
        soup = BeautifulSoup(login_page.text, 'html.parser')
        
        login_data = {
            'loginName': username,
            'password': password
        }
        
        if captcha:
            login_data['captcha'] = captcha
        
        # 添加隐藏字段
        hidden_inputs = soup.find_all('input', {'type': 'hidden'})
        for hidden in hidden_inputs:
            name = hidden.get('name')
            value = hidden.get('value')
            if name and value:
                login_data[name] = value
        
        # 执行登录
        response = self.session.post(login_url, data=login_data)
        
        # 检查登录结果
        if '交易查询' in response.text and '退出' in response.text:
            return True, "登录成功", self.session.cookies
        elif '验证码' in response.text:
            return False, "需要验证码", None
        else:
            return False, "登录失败，请检查用户名密码", None

tonglian = TonglianSession()

@app.route('/')
def index():
    username = os.getenv('TONGLIAN_USERNAME', '')
    password = os.getenv('TONGLIAN_PASSWORD', '')
    return render_template_string(HTML_TEMPLATE, username=username, password=password)

@app.route('/api/status')
def api_status():
    try:
        response = tonglian.get_login_page()
        if '商户登录' in response.text:
            return jsonify({
                'success': False, 
                'message': '未登录状态，需要手动登录',
                'needCaptcha': '验证码' in response.text
            })
        elif '交易查询' in response.text:
            return jsonify({'success': True, 'message': '已登录状态'})
        else:
            return jsonify({'success': False, 'message': '页面状态未知'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'检查失败: {str(e)}'})

@app.route('/api/captcha')
def api_captcha():
    captcha_data = tonglian.get_captcha()
    if captcha_data:
        return jsonify({'success': True, 'captcha': captcha_data})
    else:
        return jsonify({'success': False, 'message': '无法获取验证码'})

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    captcha = data.get('captcha')
    
    success, message, cookies = tonglian.login(username, password, captcha)
    
    if success:
        # 保存Cookie到环境变量文件
        userid = None
        session_id = None
        
        for cookie in cookies:
            if cookie.name.lower() == 'userid':
                userid = cookie.value
            elif cookie.name.upper() == 'SESSION':
                session_id = cookie.value
        
        if userid and session_id:
            update_env_cookies(userid, session_id)
            return jsonify({
                'success': True, 
                'message': message + '，Cookie已更新到配置文件',
                'cookies': {'userid': userid, 'session': session_id}
            })
    
    return jsonify({'success': success, 'message': message})

@app.route('/api/cookies')
def api_cookies():
    cookies = {}
    for cookie in tonglian.session.cookies:
        cookies[cookie.name] = cookie.value
    return jsonify(cookies)

@app.route('/api/test-cookies')
def api_test_cookies():
    try:
        test_url = "https://cus.allinpay.com/tranx/search"
        response = tonglian.session.get(test_url)
        
        if '交易查询' in response.text and '商户登录' not in response.text:
            return jsonify({'success': True, 'message': 'Cookie有效，可以访问订单页面'})
        else:
            return jsonify({'success': False, 'message': 'Cookie已失效，需要重新登录'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'测试失败: {str(e)}'})

@app.route('/api/update-config', methods=['POST'])
def api_update_config():
    try:
        userid = None
        session_id = None
        
        for cookie in tonglian.session.cookies:
            if cookie.name.lower() == 'userid':
                userid = cookie.value
            elif cookie.name.upper() == 'SESSION':
                session_id = cookie.value
        
        if userid and session_id:
            update_env_cookies(userid, session_id)
            return jsonify({'success': True, 'message': 'Cookie已更新到配置文件'})
        else:
            return jsonify({'success': False, 'message': '没有有效的Cookie可更新'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'更新失败: {str(e)}'})

@app.route('/api/restart', methods=['POST'])
def api_restart():
    return jsonify({'success': True, 'message': '请手动重启主程序以应用新的Cookie配置'})

def update_env_cookies(userid, session_id):
    """更新环境变量文件中的Cookie"""
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)