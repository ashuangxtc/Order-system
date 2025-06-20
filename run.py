#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通联支付订单抓取运行脚本
简化版运行入口，支持一次性抓取和定时抓取
"""

import os
import sys
import argparse
from main import OrderSyncApp


def main():
    parser = argparse.ArgumentParser(description='通联支付订单抓取工具')
    parser.add_argument('--once', action='store_true', help='只运行一次，不循环')
    parser.add_argument('--interval',
                        type=int,
                        default=10,
                        help='循环间隔(秒)，默认10秒')

    args = parser.parse_args()

    print("=" * 60)
    print("通联支付订单抓取工具")
    print("=" * 60)
    print("功能：")
    print("• 自动登录通联支付后台（需要手动输入验证码）")
    print("• 抓取今日订单数据")
    print("• 根据金额智能识别商品（48元=苏贵，20元=薯条，68元=套餐）")
    print("• 自动同步到Firebase数据库 orders_auto/ 路径")
    print("=" * 60)

    # 检查环境变量
    required_vars = [
        'TONGLIAN_USERNAME', 'TONGLIAN_PASSWORD', 'FIREBASE_DATABASE_URL'
    ]
    missing_vars = []

    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)

    if missing_vars:
        print("❌ 缺少必要的环境变量:")
        for var in missing_vars:
            print(f"   {var}")
        print("\n请在 .env 文件中设置这些变量，参考 .env.example")
        return 1

    # 检查Firebase凭证
    firebase_cred_path = os.getenv('FIREBASE_CREDENTIALS_PATH',
                                   'firebase-credentials.json')
    firebase_cred_env = os.getenv('FIREBASE_CREDENTIALS')

    if not os.path.exists(firebase_cred_path) and not firebase_cred_env:
        print(f"❌ 找不到Firebase凭证文件: {firebase_cred_path}")
        print("请上传Firebase服务账号密钥文件，或在环境变量中设置FIREBASE_CREDENTIALS")
        return 1

    print("✅ 环境检查通过")
    print()

    # 创建并运行应用
    try:
        app = OrderSyncApp()

        if args.once:
            print("🔄 执行一次性抓取...")
            if app.initialize_services():
                app.sync_orders()
                print("✅ 抓取完成")
            else:
                print("❌ 服务初始化失败")
                return 1
        else:
            print(f"🔄 开始循环抓取，间隔 {args.interval} 秒...")
            print("按 Ctrl+C 停止")

            # 设置循环间隔
            os.environ['SYNC_INTERVAL'] = str(args.interval)
            app.run()

    except KeyboardInterrupt:
        print("\n⏹️  用户停止了程序")
    except Exception as e:
        print(f"❌ 程序运行出错: {str(e)}")
        return 1

    return 0


if __name__ == "__main__":
    from order_scraper import run_scraper
    run_scraper()