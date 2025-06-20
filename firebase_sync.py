#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Firebase同步模块
负责将订单数据同步到Firebase实时数据库
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
import firebase_admin
from firebase_admin import credentials, db

class FirebaseSync:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.db_ref = None
        self.synced_orders = set()  # 用于去重
        
        self._initialize_firebase()
        self._load_config()
    
    def _initialize_firebase(self):
        """初始化Firebase"""
        try:
            # 检查Firebase是否已经初始化
            if not firebase_admin._apps:
                cred_path = os.getenv('FIREBASE_CREDENTIALS_PATH', 'firebase-credentials.json')
                database_url = os.getenv('FIREBASE_DATABASE_URL')
                
                if not database_url:
                    raise ValueError("请设置FIREBASE_DATABASE_URL环境变量")
                
                if os.path.exists(cred_path):
                    # 使用凭证文件
                    cred = credentials.Certificate(cred_path)
                else:
                    # 尝试使用环境变量中的凭证
                    firebase_cred = os.getenv('FIREBASE_CREDENTIALS')
                    if firebase_cred:
                        cred_dict = json.loads(firebase_cred)
                        cred = credentials.Certificate(cred_dict)
                    else:
                        raise ValueError(f"找不到Firebase凭证文件: {cred_path}")
                
                firebase_admin.initialize_app(cred, {
                    'databaseURL': database_url
                })
            
            self.db_ref = db.reference()
            self.logger.info("Firebase初始化成功")
            
        except Exception as e:
            self.logger.error(f"Firebase初始化失败: {str(e)}")
            raise
    
    def _load_config(self):
        """加载配置"""
        try:
            with open('config.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            firebase_config = config.get('firebase', {})
            self.orders_collection = firebase_config.get('orders_collection', 'orders')
            self.products_collection = firebase_config.get('products_collection', 'products')
            self.sync_log_collection = firebase_config.get('sync_log_collection', 'sync_logs')
            
        except Exception as e:
            self.logger.error(f"加载配置失败: {str(e)}")
            # 使用默认配置
            self.orders_collection = 'orders'
            self.products_collection = 'products'
            self.sync_log_collection = 'sync_logs'
    
    def sync_order(self, order_data: Dict) -> bool:
        """同步单个订单到Firebase"""
        try:
            order_id = order_data.get('order_id')
            if not order_id:
                self.logger.warning("订单ID为空，跳过同步")
                return False
            
            # 检查是否已经同步过
            if order_id in self.synced_orders:
                self.logger.debug(f"订单 {order_id} 已同步过，跳过")
                return True
            
            # 检查Firebase中是否已存在
            if self._order_exists(order_id):
                self.logger.debug(f"订单 {order_id} 在Firebase中已存在，跳过")
                self.synced_orders.add(order_id)
                return True
            
            # 准备同步数据
            sync_data = self._prepare_sync_data(order_data)
            
            # 写入Firebase到orders_auto路径，使用时间戳作为key
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]  # 精确到毫秒
            orders_ref = self.db_ref.child('orders_auto')
            orders_ref.child(timestamp).set(sync_data)
            
            # 记录同步日志
            self._log_sync_operation(order_id, 'success', sync_data)
            
            # 添加到已同步集合
            self.synced_orders.add(order_id)
            
            self.logger.info(f"订单 {order_id} 同步成功")
            return True
            
        except Exception as e:
            self.logger.error(f"同步订单 {order_id} 失败: {str(e)}")
            self._log_sync_operation(order_id, 'error', {'error': str(e)})
            return False
    
    def _order_exists(self, order_id: str) -> bool:
        """检查订单是否已存在于Firebase中"""
        try:
            order_ref = self.db_ref.child(self.orders_collection).child(order_id)
            return order_ref.get() is not None
        except Exception as e:
            self.logger.error(f"检查订单存在性时出错: {str(e)}")
            return False
    
    def _prepare_sync_data(self, order_data: Dict) -> Dict:
        """准备同步数据"""
        # 获取匹配的商品
        matched_products = order_data.get('matched_products', [])
        products_list = []
        
        for product in matched_products:
            if isinstance(product, dict):
                if 'combo_items' in product:
                    # 如果是组合商品，添加各个组合项
                    products_list.extend(product['combo_items'])
                else:
                    # 普通商品
                    products_list.append(product.get('name', '未知商品'))
            else:
                products_list.append(str(product))
        
        # 如果没有匹配的商品,使用默认值
        if not products_list:
            products_list = ['其他商品']
        
        sync_data = {
            'products': products_list,
            'amount': order_data.get('amount', 0),
            'createdAt': self._format_datetime(order_data.get('create_time')),
            'source': '通联支付',
            'order_id': order_data.get('order_id'),
            'status': order_data.get('status', ''),
            'pay_time': self._format_datetime(order_data.get('pay_time')),
            'payment_method': order_data.get('payment_method', ''),
            'sync_time': datetime.now().isoformat()
        }
        
        return sync_data
    
    def _format_datetime(self, dt) -> Optional[str]:
        """格式化日期时间"""
        if dt is None:
            return None
        
        if isinstance(dt, datetime):
            return dt.isoformat()
        elif isinstance(dt, str):
            return dt
        else:
            return str(dt)
    
    def _log_sync_operation(self, order_id: str, status: str, data: Dict):
        """记录同步操作日志"""
        try:
            log_data = {
                'order_id': order_id,
                'status': status,
                'timestamp': datetime.now().isoformat(),
                'data': data
            }
            
            log_ref = self.db_ref.child(self.sync_log_collection)
            log_ref.push(log_data)
            
        except Exception as e:
            self.logger.error(f"记录同步日志失败: {str(e)}")
    
    def sync_multiple_orders(self, orders: List[Dict]) -> Dict:
        """批量同步订单"""
        results = {
            'success': 0,
            'failed': 0,
            'skipped': 0,
            'errors': []
        }
        
        for order in orders:
            try:
                if self.sync_order(order):
                    results['success'] += 1
                else:
                    results['failed'] += 1
            except Exception as e:
                results['failed'] += 1
                results['errors'].append(f"订单 {order.get('order_id', 'unknown')}: {str(e)}")
        
        self.logger.info(f"批量同步完成: 成功 {results['success']}, 失败 {results['failed']}")
        return results
    
    def get_recent_orders(self, limit: int = 50) -> List[Dict]:
        """获取最近的订单"""
        try:
            orders_ref = self.db_ref.child(self.orders_collection)
            orders = orders_ref.order_by_child('sync_time').limit_to_last(limit).get()
            
            if orders:
                return list(orders.values())
            return []
            
        except Exception as e:
            self.logger.error(f"获取最近订单失败: {str(e)}")
            return []
    
    def cleanup_old_logs(self, days_to_keep: int = 30):
        """清理旧的同步日志"""
        try:
            cutoff_date = datetime.now().timestamp() - (days_to_keep * 24 * 3600)
            
            logs_ref = self.db_ref.child(self.sync_log_collection)
            old_logs = logs_ref.order_by_child('timestamp').end_at(cutoff_date).get()
            
            if old_logs:
                for log_id in old_logs.keys():
                    logs_ref.child(log_id).delete()
                
                self.logger.info(f"清理了 {len(old_logs)} 条旧日志")
            
        except Exception as e:
            self.logger.error(f"清理旧日志失败: {str(e)}")
    
    def get_sync_statistics(self) -> Dict:
        """获取同步统计信息"""
        try:
            stats = {
                'total_orders': 0,
                'today_synced': 0,
                'last_sync_time': None,
                'error_count': 0
            }
            
            # 获取订单总数
            orders_ref = self.db_ref.child(self.orders_collection)
            orders = orders_ref.get()
            if orders:
                stats['total_orders'] = len(orders)
            
            # 获取今日同步数量
            today = datetime.now().strftime('%Y-%m-%d')
            today_orders = [
                order for order in (orders.values() if orders else [])
                if order.get('sync_time', '').startswith(today)
            ]
            stats['today_synced'] = len(today_orders)
            
            # 获取最后同步时间
            if orders:
                latest_order = max(
                    orders.values(),
                    key=lambda x: x.get('sync_time', ''),
                    default={}
                )
                stats['last_sync_time'] = latest_order.get('sync_time')
            
            return stats
            
        except Exception as e:
            self.logger.error(f"获取同步统计失败: {str(e)}")
            return {}
    
    def close(self):
        """关闭Firebase连接"""
        try:
            # Firebase Admin SDK会自动管理连接
            self.logger.info("Firebase同步服务已关闭")
        except Exception as e:
            self.logger.error(f"关闭Firebase连接时出错: {str(e)}")
