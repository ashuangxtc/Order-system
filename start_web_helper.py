#!/usr/bin/env python3
"""
启动Web登录助手
"""

import os
import sys

def main():
    print("=== 通联支付Web登录助手 ===")
    print()
    print("正在启动登录界面...")
    
    # 导入并运行Web应用
    try:
        from simple_web_login import app
        print("Web登录界面已启动")
        print("请在浏览器中访问以下地址完成登录：")
        print("  http://localhost:5000")
        print()
        print("使用说明：")
        print("1. 点击'获取验证码'按钮")
        print("2. 查看验证码图片并输入")
        print("3. 点击'登录'完成验证")
        print("4. 登录成功后Cookie会自动保存")
        print()
        print("账号信息：")
        print("  用户名：NJYHL013")
        print("  密码：Yongrenzrao1")
        print()
        
        # 启动Flask应用
        app.run(host='0.0.0.0', port=5000, debug=False)
        
    except Exception as e:
        print(f"启动失败：{e}")
        sys.exit(1)

if __name__ == '__main__':
    main()