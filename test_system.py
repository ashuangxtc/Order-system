#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统测试脚本
测试各个模块的基本功能
"""

import os
import sys
from dotenv import load_dotenv

def test_environment():
    """测试环境配置"""
    print("=== 环境配置测试 ===")
    
    # 加载环境变量
    load_dotenv()
    
    # 检查关键环境变量
    required_vars = {
        'TONGLIAN_USERNAME': os.getenv('TONGLIAN_USERNAME'),
        'TONGLIAN_PASSWORD': os.getenv('TONGLIAN_PASSWORD'),
        'FIREBASE_DATABASE_URL': os.getenv('FIREBASE_DATABASE_URL')
    }
    
    all_good = True
    for var_name, var_value in required_vars.items():
        if var_value and '请填写' not in var_value:
            print(f"✅ {var_name}: 已配置")
        else:
            print(f"❌ {var_name}: 未配置或使用默认值")
            all_good = False
    
    return all_good

def test_firebase_credentials():
    """测试Firebase凭证"""
    print("\n=== Firebase凭证测试 ===")
    
    firebase_cred_path = os.getenv('FIREBASE_CREDENTIALS_PATH', 'firebase-credentials.json')
    
    if os.path.exists(firebase_cred_path):
        print(f"✅ 找到Firebase凭证文件: {firebase_cred_path}")
        
        try:
            import json
            with open(firebase_cred_path, 'r') as f:
                cred = json.load(f)
            
            required_fields = ['type', 'project_id', 'private_key_id', 'private_key', 'client_email']
            missing_fields = [field for field in required_fields if field not in cred]
            
            if missing_fields:
                print(f"❌ Firebase凭证文件缺少字段: {missing_fields}")
                return False
            else:
                print(f"✅ Firebase项目ID: {cred['project_id']}")
                print(f"✅ Firebase凭证格式正确")
                return True
                
        except Exception as e:
            print(f"❌ Firebase凭证文件格式错误: {str(e)}")
            return False
    else:
        print(f"❌ 未找到Firebase凭证文件: {firebase_cred_path}")
        print("\n请按以下步骤添加Firebase凭证:")
        print("1. 访问 Firebase控制台 https://console.firebase.google.com/")
        print("2. 选择您的项目")
        print("3. 进入 项目设置 > 服务账号")
        print("4. 点击 '生成新的私钥' 下载JSON文件")
        print("5. 将下载的文件重命名为 'firebase-credentials.json'")
        print("6. 上传到当前目录")
        return False

def test_product_matching():
    """测试商品匹配功能"""
    print("\n=== 商品匹配测试 ===")
    
    try:
        from product_matcher import ProductMatcher
        
        matcher = ProductMatcher()
        
        # 测试各种金额
        test_amounts = [48, 20, 58, 68, 96, 106, 100]
        
        for amount in test_amounts:
            test_order = {'amount': amount}
            matched_products = matcher.match_products(test_order)
            
            if matched_products:
                product_names = [p.get('name', '未知') for p in matched_products]
                print(f"✅ {amount}元 → {', '.join(product_names)}")
            else:
                print(f"⚠️  {amount}元 → 无匹配商品")
        
        return True
        
    except Exception as e:
        print(f"❌ 商品匹配测试失败: {str(e)}")
        return False

def test_login_capability():
    """测试登录功能（不实际登录）"""
    print("\n=== 登录功能测试 ===")
    
    try:
        from order_scraper import OrderScraper
        
        login_url = os.getenv('TONGLIAN_LOGIN_URL', 'https://cus.allinpay.com/tranx/search')
        username = os.getenv('TONGLIAN_USERNAME', 'test')
        password = os.getenv('TONGLIAN_PASSWORD', 'test')
        
        scraper = OrderScraper(login_url, username, password)
        
        # 测试访问登录页面
        import requests
        try:
            response = requests.get(login_url, timeout=10)
            if response.status_code == 200:
                print(f"✅ 可以访问通联支付登录页面")
                print(f"✅ 响应长度: {len(response.text)} 字符")
                
                if '验证码' in response.text or 'captcha' in response.text.lower():
                    print("✅ 检测到验证码字段")
                
                return True
            else:
                print(f"⚠️  登录页面响应状态码: {response.status_code}")
                return False
                
        except requests.RequestException as e:
            print(f"❌ 无法访问登录页面: {str(e)}")
            return False
            
    except Exception as e:
        print(f"❌ 登录功能测试失败: {str(e)}")
        return False

def main():
    """主测试函数"""
    print("通联支付订单抓取系统 - 系统测试")
    print("=" * 50)
    
    tests = [
        ("环境配置", test_environment),
        ("Firebase凭证", test_firebase_credentials), 
        ("商品匹配", test_product_matching),
        ("登录功能", test_login_capability)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name}测试出错: {str(e)}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("测试结果汇总:")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n总体结果: {passed}/{total} 项测试通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！系统准备就绪，可以运行:")
        print("python run.py --once")
    else:
        print(f"\n⚠️  请先解决失败的测试项，然后重新运行测试")
    
    return passed == total

if __name__ == "__main__":
    sys.exit(0 if main() else 1)