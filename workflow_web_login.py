#!/usr/bin/env python3
"""
工作流集成Web登录 - 在5000端口启动登录界面
"""

import subprocess
import sys
import time
import os
from threading import Thread

def start_web_server():
    """启动Web登录服务器"""
    try:
        # 启动Flask应用
        process = subprocess.Popen([
            sys.executable, 'simple_web_login.py'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        return process
    except Exception as e:
        print(f"启动Web服务器失败: {e}")
        return None

def check_login_status():
    """检查登录状态"""
    try:
        import requests
        response = requests.get('http://localhost:5000/api/status', timeout=5)
        data = response.json()
        return data.get('logged_in', False)
    except:
        return False

def main():
    print("启动通联支付Web登录界面...")
    
    # 启动Web服务器
    web_process = start_web_server()
    if not web_process:
        print("无法启动Web服务器")
        return
    
    # 等待服务器启动
    time.sleep(3)
    
    print("Web登录界面已启动")
    print("请在浏览器中访问: http://localhost:5000")
    print("完成登录后，主程序将自动获取有效Cookie")
    print("按 Ctrl+C 停止服务")
    
    try:
        # 监控登录状态
        while True:
            if check_login_status():
                print("检测到登录成功！Cookie已保存")
                print("主程序现在可以正常运行订单抓取")
                break
            time.sleep(10)  # 每10秒检查一次
            
    except KeyboardInterrupt:
        print("停止Web登录服务")
    finally:
        if web_process:
            web_process.terminate()

if __name__ == '__main__':
    main()