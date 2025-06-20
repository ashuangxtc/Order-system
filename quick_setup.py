#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速配置脚本
帮助用户快速设置环境变量和Firebase凭证
"""

import os
import json

def setup_env():
    """设置环境变量"""
    print("=== 通联支付订单抓取系统 - 快速配置 ===\n")
    
    # 检查.env文件
    if os.path.exists('.env'):
        print("✅ .env文件已存在")
        with open('.env', 'r', encoding='utf-8') as f:
            content = f.read()
            if '请填写' in content:
                print("⚠️  请编辑.env文件，填写正确的配置信息")
            else:
                print("✅ .env文件配置看起来已完成")
    else:
        print("❌ .env文件不存在，正在创建...")
        # 从.env.example复制
        if os.path.exists('.env.example'):
            with open('.env.example', 'r', encoding='utf-8') as src:
                with open('.env', 'w', encoding='utf-8') as dst:
                    dst.write(src.read())
            print("✅ 已创建.env文件，请编辑填写配置")
    
    # 检查Firebase凭证
    firebase_cred_path = 'firebase-credentials.json'
    if os.path.exists(firebase_cred_path):
        print("✅ Firebase凭证文件已存在")
        try:
            with open(firebase_cred_path, 'r') as f:
                cred = json.load(f)
                if 'project_id' in cred:
                    print(f"✅ Firebase项目: {cred['project_id']}")
        except:
            print("⚠️  Firebase凭证文件格式可能有误")
    else:
        print("❌ 未找到Firebase凭证文件")
        print("请从Firebase控制台下载服务账号密钥，重命名为'firebase-credentials.json'")
    
    print("\n=== 配置检查完成 ===")
    print("\n下一步:")
    print("1. 编辑.env文件，填写通联支付账号信息")
    print("2. 上传Firebase服务账号密钥文件")
    print("3. 运行: python run.py --once")

if __name__ == "__main__":
    setup_env()