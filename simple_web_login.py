#!/usr/bin/env python3
"""
简化Web登录工具 - 处理验证码登录
"""

from flask import Flask, render_template_string, request, jsonify, send_from_directory
import requests
from bs4 import BeautifulSoup
import os
import threading
import time

app = Flask(__name__)

# 全局会话和状态
session_store = {}
login_status = {'logged_in': False, 'message': ''}

TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>通联支付登录助手</title>
    <meta charset="utf-8">
    <style>
        body { font-family: 'Microsoft YaHei', Arial, sans-serif; margin: 40px; background: #f0f2f5; }
        .container { max-width: 600px; margin: 0 auto; background: white; padding: 40px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h2 { color: #333; text-align: center; margin-bottom: 30px; }
        .step { margin: 20px 0; padding: 20px; border: 1px solid #e1e5e9; border-radius: 6px; background: #fafbfc; }
        .step h3 { margin: 0 0 15px 0; color: #0366d6; }
        .btn { background: #28a745; color: white; padding: 12px 24px; border: none; border-radius: 6px; cursor: pointer; font-size: 16px; margin: 5px; }
        .btn:hover { background: #218838; }
        .btn:disabled { background: #6c757d; cursor: not-allowed; }
        .success { background: #d4edda; padding: 15px; border-radius: 6px; color: #155724; margin: 15px 0; border: 1px solid #c3e6cb; }
        .error { background: #f8d7da; padding: 15px; border-radius: 6px; color: #721c24; margin: 15px 0; border: 1px solid #f5c6cb; }
        .info { background: #d1ecf1; padding: 15px; border-radius: 6px; color: #0c5460; margin: 15px 0; border: 1px solid #bee5eb; }
        .form-group { margin: 15px 0; }
        label { display: block; margin-bottom: 8px; font-weight: bold; color: #333; }
        input[type="text"] { width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 6px; font-size: 16px; box-sizing: border-box; }
        .captcha-container { text-align: center; margin: 20px 0; }
        .captcha-img { max-width: 200px; border: 2px solid #ddd; border-radius: 6px; margin: 10px 0; }
        .status { padding: 15px; border-radius: 6px; margin: 20px 0; }
        .loading { display: none; color: #666; }
    </style>
</head>
<body>
    <div class="container">
        <h2>🔐 通联支付登录助手</h2>
        
        <div class="info">
            <strong>使用说明：</strong><br>
            1. 点击"获取验证码"获取最新的验证码图片<br>
            2. 输入验证码内容<br>
            3. 点击"登录"完成登录过程<br>
            4. 登录成功后Cookie会自动保存到系统中
        </div>

        <div class="step">
            <h3>步骤 1：获取验证码</h3>
            <button class="btn" onclick="getCaptcha()" id="captcha-btn">获取验证码</button>
            <div class="loading" id="captcha-loading">正在获取验证码...</div>
            
            <div id="captcha-display" style="display:none;">
                <div class="captcha-container">
                    <p>验证码图片：</p>
                    <img id="captcha-img" class="captcha-img" src="" alt="验证码" />
                    <p><small>如果看不清，请重新获取验证码</small></p>
                </div>
            </div>
        </div>

        <div class="step">
            <h3>步骤 2：输入验证码并登录</h3>
            <div class="form-group">
                <label for="captcha-input">请输入验证码：</label>
                <input type="text" id="captcha-input" placeholder="请输入验证码" maxlength="5" />
            </div>
            <button class="btn" onclick="doLogin()" id="login-btn" disabled>登录</button>
            <div class="loading" id="login-loading">正在登录...</div>
        </div>

        <div id="result"></div>
        
        <div class="step">
            <h3>系统信息</h3>
            <p><strong>账号：</strong>NJYHL013</p>
            <p><strong>状态：</strong><span id="login-status">未登录</span></p>
        </div>
    </div>

    <script>
        function getCaptcha() {
            document.getElementById('captcha-btn').disabled = true;
            document.getElementById('captcha-loading').style.display = 'block';
            document.getElementById('result').innerHTML = '';
            
            fetch('/api/get-captcha')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('captcha-loading').style.display = 'none';
                    
                    if (data.success) {
                        document.getElementById('captcha-img').src = '/api/captcha-image?' + new Date().getTime();
                        document.getElementById('captcha-display').style.display = 'block';
                        document.getElementById('login-btn').disabled = false;
                        document.getElementById('result').innerHTML = '<div class="success">验证码获取成功，请输入验证码</div>';
                    } else {
                        document.getElementById('result').innerHTML = '<div class="error">获取验证码失败：' + data.error + '</div>';
                    }
                    
                    document.getElementById('captcha-btn').disabled = false;
                })
                .catch(error => {
                    document.getElementById('captcha-loading').style.display = 'none';
                    document.getElementById('captcha-btn').disabled = false;
                    document.getElementById('result').innerHTML = '<div class="error">网络错误：' + error + '</div>';
                });
        }
        
        function doLogin() {
            const captcha = document.getElementById('captcha-input').value.trim();
            if (!captcha) {
                alert('请输入验证码');
                return;
            }
            
            document.getElementById('login-btn').disabled = true;
            document.getElementById('login-loading').style.display = 'block';
            
            fetch('/api/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ captcha: captcha })
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById('login-loading').style.display = 'none';
                
                if (data.success) {
                    document.getElementById('result').innerHTML = '<div class="success"><strong>登录成功！</strong><br>' + data.message + '</div>';
                    document.getElementById('login-status').textContent = '已登录';
                    document.getElementById('login-status').style.color = '#28a745';
                } else {
                    document.getElementById('result').innerHTML = '<div class="error"><strong>登录失败：</strong>' + data.error + '</div>';
                    if (data.error.includes('验证码')) {
                        // 验证码错误，清空输入框
                        document.getElementById('captcha-input').value = '';
                    }
                }
                
                document.getElementById('login-btn').disabled = false;
            })
            .catch(error => {
                document.getElementById('login-loading').style.display = 'none';
                document.getElementById('login-btn').disabled = false;
                document.getElementById('result').innerHTML = '<div class="error">网络错误：' + error + '</div>';
            });
        }
        
        // 自动检查登录状态
        setInterval(function() {
            fetch('/api/status')
                .then(response => response.json())
                .then(data => {
                    if (data.logged_in) {
                        document.getElementById('login-status').textContent = '已登录';
                        document.getElementById('login-status').style.color = '#28a745';
                    }
                });
        }, 5000);
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(TEMPLATE)

@app.route('/api/get-captcha')
def api_get_captcha():
    try:
        # 创建新的会话
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Connection': 'keep-alive'
        })
        
        # 存储会话
        session_store['current'] = session
        
        # 获取登录页面
        login_url = "https://cus.allinpay.com/login"
        response = session.get(login_url)
        
        if response.status_code != 200:
            return jsonify({'success': False, 'error': f'无法访问登录页面，状态码：{response.status_code}'})
        
        # 获取验证码
        captcha_url = "https://cus.allinpay.com/getvalidCode?type=cuserrorCode"
        captcha_response = session.get(captcha_url)
        
        if captcha_response.status_code != 200:
            return jsonify({'success': False, 'error': f'无法获取验证码，状态码：{captcha_response.status_code}'})
        
        # 保存验证码图片
        captcha_path = 'current_captcha.png'
        with open(captcha_path, 'wb') as f:
            f.write(captcha_response.content)
        
        return jsonify({'success': True, 'message': '验证码获取成功'})
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'获取验证码时出错：{str(e)}'})

@app.route('/api/captcha-image')
def api_captcha_image():
    try:
        return send_from_directory('.', 'current_captcha.png')
    except Exception as e:
        return f"Error: {e}", 404

@app.route('/api/login', methods=['POST'])
def api_login():
    try:
        data = request.get_json()
        captcha = data.get('captcha', '').strip()
        
        if not captcha:
            return jsonify({'success': False, 'error': '验证码不能为空'})
        
        # 获取当前会话
        session = session_store.get('current')
        if not session:
            return jsonify({'success': False, 'error': '会话已过期，请重新获取验证码'})
        
        # 重新获取登录页面以获取最新的token
        login_url = "https://cus.allinpay.com/login"
        response = session.get(login_url)
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
        if token_input and hasattr(token_input, 'get') and token_input.get('value'):
            login_data['token'] = token_input.get('value')
        
        # 执行登录
        login_response = session.post(login_url, data=login_data, allow_redirects=False)
        
        # 分析登录结果
        if login_response.status_code in [301, 302, 303]:
            # 检查重定向位置
            location = login_response.headers.get('Location', '')
            if '/main' in location or 'main' in location or location == '/' or location == '/main.dsr':
                # 登录成功
                cookies = dict(session.cookies)
                userid = cookies.get('userid')
                session_id = cookies.get('SESSION') or cookies.get('JSESSIONID')
                
                if userid and session_id:
                    # 保存Cookie到配置文件
                    save_cookies_to_env(userid, session_id)
                    login_status['logged_in'] = True
                    login_status['message'] = f'Cookie已保存：userid={userid[:8]}...'
                    return jsonify({
                        'success': True, 
                        'message': f'登录成功！Cookie已保存到配置文件。userid: {userid[:8]}..., session: {session_id[:8]}...'
                    })
                else:
                    return jsonify({'success': False, 'error': '登录成功但未获取到有效Cookie'})
            else:
                return jsonify({'success': False, 'error': f'登录重定向异常：{location}'})
        
        # 检查响应内容
        response_text = login_response.text
        if '验证码' in response_text and ('错误' in response_text or '不正确' in response_text or '请输入正确' in response_text):
            return jsonify({'success': False, 'error': '验证码错误，请重新输入'})
        elif '用户名' in response_text and ('错误' in response_text or '不存在' in response_text):
            return jsonify({'success': False, 'error': '用户名错误'})
        elif '密码' in response_text and ('错误' in response_text or '不正确' in response_text):
            return jsonify({'success': False, 'error': '密码错误'})
        elif '交易查询' in response_text or '退出' in response_text or '主页' in response_text:
            # 通过页面内容判断登录成功
            cookies = dict(session.cookies)
            userid = cookies.get('userid')
            session_id = cookies.get('SESSION') or cookies.get('JSESSIONID')
            
            if userid and session_id:
                save_cookies_to_env(userid, session_id)
                login_status['logged_in'] = True
                return jsonify({
                    'success': True, 
                    'message': f'登录成功！Cookie已保存。userid: {userid[:8]}...'
                })
        
        # 保存响应内容用于调试
        with open('login_debug_response.html', 'w', encoding='utf-8') as f:
            f.write(response_text[:2000])  # 只保存前2000字符
        
        return jsonify({'success': False, 'error': '登录失败，可能是验证码错误或其他问题'})
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'登录过程出错：{str(e)}'})

@app.route('/api/status')
def api_status():
    return jsonify(login_status)

def save_cookies_to_env(userid, session_id):
    """保存Cookie到环境变量文件"""
    env_file = 'user.env'
    
    try:
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
            
        print(f"Cookie已保存：userid={userid}, session={session_id}")
        
    except Exception as e:
        print(f"保存Cookie失败：{e}")

if __name__ == '__main__':
    print("启动通联支付登录助手...")
    print("请在浏览器中访问：http://localhost:5000")
    print("按 Ctrl+C 停止服务")
    app.run(host='0.0.0.0', port=5000, debug=False)