from flask import Flask, render_template_string, request, jsonify
import requests
from bs4 import BeautifulSoup
import os
import base64

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>通联支付登录助手</title>
    <meta charset="utf-8">
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }
        .container { max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .success { background-color: #d4edda; padding: 15px; border-radius: 5px; border-left: 4px solid #28a745; margin: 10px 0; }
        .error { background-color: #f8d7da; padding: 15px; border-radius: 5px; border-left: 4px solid #dc3545; margin: 10px 0; }
        .warning { background-color: #fff3cd; padding: 15px; border-radius: 5px; border-left: 4px solid #ffc107; margin: 10px 0; }
        .form-group { margin: 15px 0; }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
        input { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; box-sizing: border-box; }
        button { background-color: #007bff; color: white; padding: 12px 20px; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; }
        button:hover { background-color: #0056b3; }
        .captcha-section { display: none; }
        .captcha-img { max-width: 200px; margin: 10px 0; border: 1px solid #ddd; }
        .status { margin: 20px 0; padding: 15px; border-radius: 5px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔐 通联支付登录助手</h1>
        
        <div class="warning">
            <strong>使用说明:</strong><br>
            1. 输入通联支付账号密码<br>
            2. 如需验证码，点击获取验证码<br>
            3. 登录成功后，Cookie将自动保存到系统
        </div>

        <div class="form-group">
            <button onclick="checkStatus()">检查当前登录状态</button>
        </div>
        <div id="status-result"></div>

        <form onsubmit="submitLogin(event)">
            <div class="form-group">
                <label>用户名:</label>
                <input type="text" id="username" value="NJYHL013" required>
            </div>
            
            <div class="form-group">
                <label>密码:</label>
                <input type="password" id="password" value="Yongrenzrao1" required>
            </div>
            
            <div class="form-group">
                <button type="button" onclick="getCaptcha()">获取验证码</button>
            </div>
            
            <div id="captcha-section" class="captcha-section">
                <div class="form-group">
                    <label>验证码:</label>
                    <input type="text" id="captcha" placeholder="请输入验证码">
                    <div id="captcha-display"></div>
                </div>
            </div>
            
            <div class="form-group">
                <button type="submit">登录获取Cookie</button>
            </div>
        </form>
        
        <div id="login-result"></div>
    </div>

    <script>
        async function checkStatus() {
            const result = document.getElementById('status-result');
            result.innerHTML = '<div class="status">检查中...</div>';
            
            try {
                const response = await fetch('/api/status');
                const data = await response.json();
                
                if (data.success) {
                    result.innerHTML = '<div class="success">✅ ' + data.message + '</div>';
                } else {
                    result.innerHTML = '<div class="error">❌ ' + data.message + '</div>';
                }
            } catch (error) {
                result.innerHTML = '<div class="error">❌ 检查失败: ' + error.message + '</div>';
            }
        }

        async function getCaptcha() {
            try {
                const response = await fetch('/api/captcha');
                const data = await response.json();
                
                if (data.success) {
                    document.getElementById('captcha-section').style.display = 'block';
                    document.getElementById('captcha-display').innerHTML = 
                        '<img src="data:image/png;base64,' + data.captcha + '" class="captcha-img" alt="验证码">';
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
            result.innerHTML = '<div class="status">登录中...</div>';
            
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
                    result.innerHTML = '<div class="success">✅ ' + data.message + '</div>';
                    if (data.cookies) {
                        result.innerHTML += '<div class="success">Cookie已保存，系统将自动重启</div>';
                        setTimeout(() => {
                            window.location.reload();
                        }, 3000);
                    }
                } else {
                    result.innerHTML = '<div class="error">❌ ' + data.message + '</div>';
                    if (data.message.includes('验证码')) {
                        getCaptcha();
                    }
                }
            } catch (error) {
                result.innerHTML = '<div class="error">❌ 登录失败: ' + error.message + '</div>';
            }
        }
    </script>
</body>
</html>
"""

class TonglianAuth:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def check_login_status(self):
        """检查当前登录状态"""
        try:
            response = self.session.get("https://cus.allinpay.com/tranx/search")
            if '商户登录' in response.text or '账号登录' in response.text:
                return False, "未登录状态"
            elif '交易查询' in response.text:
                return True, "已登录状态"
            else:
                return False, "状态未知"
        except Exception as e:
            return False, f"检查失败: {str(e)}"

    def get_captcha_image(self):
        """获取验证码图片"""
        try:
            login_url = "https://cus.allinpay.com/login"
            response = self.session.get(login_url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 查找验证码图片
            for img in soup.find_all('img'):
                src = img.get('src', '')
                if any(keyword in src.lower() for keyword in ['captcha', 'code', 'verify']):
                    if src.startswith('/'):
                        src = 'https://cus.allinpay.com' + src
                    
                    img_response = self.session.get(src)
                    if img_response.status_code == 200:
                        return base64.b64encode(img_response.content).decode()
            
            return None
        except Exception:
            return None

    def login(self, username, password, captcha=None):
        """执行登录"""
        try:
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
            
            # 添加隐藏字段
            for hidden in soup.find_all('input', {'type': 'hidden'}):
                name = hidden.get('name')
                value = hidden.get('value')
                if name and value:
                    login_data[name] = value
            
            # 执行登录
            response = self.session.post(login_url, data=login_data)
            
            # 检查登录结果
            if '交易查询' in response.text and '退出' in response.text:
                return True, "登录成功", self.get_cookies()
            elif '验证码' in response.text or 'captcha' in response.text.lower():
                return False, "需要验证码", None
            else:
                return False, "登录失败，请检查用户名密码", None
                
        except Exception as e:
            return False, f"登录异常: {str(e)}", None

    def get_cookies(self):
        """获取当前会话的Cookie"""
        cookies = {}
        for cookie in self.session.cookies:
            cookies[cookie.name] = cookie.value
        return cookies

auth = TonglianAuth()

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/status')
def api_status():
    success, message = auth.check_login_status()
    return jsonify({'success': success, 'message': message})

@app.route('/api/captcha')
def api_captcha():
    captcha_data = auth.get_captcha_image()
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
    
    success, message, cookies = auth.login(username, password, captcha)
    
    if success and cookies:
        # 保存Cookie到环境变量文件
        userid = cookies.get('userid')
        session_id = cookies.get('SESSION')
        
        if userid and session_id:
            update_env_file(userid, session_id)
            return jsonify({
                'success': True, 
                'message': 'Cookie已保存到配置文件',
                'cookies': {'userid': userid, 'session': session_id}
            })
    
    return jsonify({'success': success, 'message': message})

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
    except Exception:
        return False

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)