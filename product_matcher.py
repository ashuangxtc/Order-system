#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
商品匹配模块
根据订单金额智能识别商品组合
"""

import json
import logging
from typing import Dict, List, Optional

class ProductMatcher:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.products_config = {}
        self.load_config()
    
    def load_config(self):
        """加载商品配置"""
        try:
            with open('config.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            self.products_config = config.get('products', {})
            self.logger.info("商品配置加载成功")
            
        except Exception as e:
            self.logger.error(f"加载商品配置失败: {str(e)}")
            # 使用默认配置
            self.products_config = {
                'mappings': [],
                'default_product': {
                    'name': '其他商品',
                    'description': '未分类商品',
                    'category': '其他'
                }
            }
    
    def match_products(self, order_data: Dict) -> List[Dict]:
        """根据订单数据匹配商品"""
        try:
            amount = float(order_data.get('amount', 0))
            if amount <= 0:
                self.logger.warning(f"订单金额无效: {amount}")
                return []
            
            matched_products = []
            
            # 尝试精确匹配
            exact_match = self._find_exact_match(amount)
            if exact_match:
                matched_products.append(exact_match)
                self.logger.info(f"找到精确匹配商品: {exact_match['name']}")
                return matched_products
            
            # 尝试范围匹配
            range_matches = self._find_range_matches(amount)
            if range_matches:
                matched_products.extend(range_matches)
                self.logger.info(f"找到 {len(range_matches)} 个范围匹配商品")
                return matched_products
            
            # 尝试组合匹配
            combo_matches = self._find_combo_matches(amount)
            if combo_matches:
                matched_products.extend(combo_matches)
                self.logger.info(f"找到组合匹配: {len(combo_matches)} 个商品")
                return matched_products
            
            # 使用默认商品
            default_product = self._get_default_product(amount)
            matched_products.append(default_product)
            self.logger.info(f"使用默认商品匹配: {default_product['name']}")
            
            return matched_products
            
        except Exception as e:
            self.logger.error(f"商品匹配时出错: {str(e)}")
            return [self._get_default_product(order_data.get('amount', 0))]
    
    def _find_exact_match(self, amount: float) -> Optional[Dict]:
        """查找精确金额匹配的商品"""
        mappings = self.products_config.get('mappings', [])
        
        for mapping in mappings:
            # 检查是否有exact_amount字段
            if 'exact_amount' in mapping and mapping['exact_amount'] == amount:
                return self._create_product_info(mapping, amount, 'exact')
        
        return None
    
    def _find_range_matches(self, amount: float) -> List[Dict]:
        """查找范围匹配的商品"""
        matches = []
        mappings = self.products_config.get('mappings', [])
        
        for mapping in mappings:
            amount_range = mapping.get('amount_range', [])
            if len(amount_range) >= 2:
                min_amount, max_amount = amount_range[0], amount_range[1]
                if min_amount <= amount <= max_amount:
                    product_info = self._create_product_info(mapping, amount, 'range')
                    matches.append(product_info)
        
        return matches
    
    def _find_combo_matches(self, amount: float) -> List[Dict]:
        """查找组合匹配的商品"""
        mappings = self.products_config.get('mappings', [])
        best_combo = []
        best_diff = float('inf')
        
        # 尝试不同的商品组合
        for i in range(len(mappings)):
            for j in range(i, len(mappings)):
                combo = [mappings[i]]
                combo_amount = self._get_mapping_price(mappings[i])
                
                if i != j:
                    combo.append(mappings[j])
                    combo_amount += self._get_mapping_price(mappings[j])
                
                # 计算差值
                diff = abs(amount - combo_amount)
                tolerance = amount * 0.05  # 5%的容错率
                
                if diff <= tolerance and diff < best_diff:
                    best_diff = diff
                    best_combo = combo
        
        if best_combo:
            return [
                self._create_product_info(mapping, amount / len(best_combo), 'combo')
                for mapping in best_combo
            ]
        
        return []
    
    def _get_mapping_price(self, mapping: Dict) -> float:
        """获取商品映射的价格"""
        if 'exact_amount' in mapping:
            return float(mapping['exact_amount'])
        elif 'amount_range' in mapping:
            amount_range = mapping['amount_range']
            if len(amount_range) >= 2:
                return (amount_range[0] + amount_range[1]) / 2  # 使用中位数
        elif 'default_price' in mapping:
            return float(mapping['default_price'])
        
        return 0.0
    
    def _create_product_info(self, mapping: Dict, amount: float, match_type: str) -> Dict:
        """创建商品信息"""
        return {
            'name': mapping.get('name', '未知商品'),
            'description': mapping.get('description', ''),
            'category': mapping.get('category', '其他'),
            'amount': amount,
            'match_type': match_type,
            'confidence': self._calculate_confidence(mapping, amount, match_type),
            'mapping_id': mapping.get('id', ''),
            'attributes': mapping.get('attributes', {})
        }
    
    def _calculate_confidence(self, mapping: Dict, amount: float, match_type: str) -> float:
        """计算匹配置信度"""
        if match_type == 'exact':
            return 1.0  # 精确匹配
        elif match_type == 'range':
            amount_range = mapping.get('amount_range', [])
            if len(amount_range) >= 2:
                min_amount, max_amount = amount_range[0], amount_range[1]
                range_size = max_amount - min_amount
                distance_from_center = abs(amount - (min_amount + max_amount) / 2)
                confidence = 1.0 - (distance_from_center / (range_size / 2))
                return max(0.5, min(1.0, confidence))  # 范围0.5-1.0
        elif match_type == 'combo':
            return 0.7  # 组合匹配
        
        return 0.3  # 默认匹配
    
    def _get_default_product(self, amount: float) -> Dict:
        """获取默认商品"""
        default_config = self.products_config.get('default_product', {})
        
        return {
            'name': default_config.get('name', '其他商品'),
            'description': default_config.get('description', '未分类商品'),
            'category': default_config.get('category', '其他'),
            'amount': amount,
            'match_type': 'default',
            'confidence': 0.1,
            'mapping_id': 'default',
            'attributes': {}
        }
    
    def add_product_mapping(self, mapping: Dict) -> bool:
        """添加商品映射"""
        try:
            mappings = self.products_config.get('mappings', [])
            mappings.append(mapping)
            self.products_config['mappings'] = mappings
            
            # 保存到配置文件
            self._save_config()
            
            self.logger.info(f"添加商品映射: {mapping.get('name', 'unknown')}")
            return True
            
        except Exception as e:
            self.logger.error(f"添加商品映射失败: {str(e)}")
            return False
    
    def remove_product_mapping(self, mapping_id: str) -> bool:
        """删除商品映射"""
        try:
            mappings = self.products_config.get('mappings', [])
            original_count = len(mappings)
            
            mappings = [m for m in mappings if m.get('id') != mapping_id]
            self.products_config['mappings'] = mappings
            
            if len(mappings) < original_count:
                self._save_config()
                self.logger.info(f"删除商品映射: {mapping_id}")
                return True
            else:
                self.logger.warning(f"未找到要删除的商品映射: {mapping_id}")
                return False
                
        except Exception as e:
            self.logger.error(f"删除商品映射失败: {str(e)}")
            return False
    
    def _save_config(self):
        """保存配置到文件"""
        try:
            with open('config.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            config['products'] = self.products_config
            
            with open('config.json', 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            self.logger.error(f"保存配置失败: {str(e)}")
    
    def get_matching_statistics(self) -> Dict:
        """获取匹配统计信息"""
        try:
            mappings = self.products_config.get('mappings', [])
            
            stats = {
                'total_mappings': len(mappings),
                'exact_mappings': 0,
                'range_mappings': 0,
                'categories': {}
            }
            
            for mapping in mappings:
                # 统计匹配类型
                if 'exact_amount' in mapping:
                    stats['exact_mappings'] += 1
                elif 'amount_range' in mapping:
                    stats['range_mappings'] += 1
                
                # 统计类别
                category = mapping.get('category', '其他')
                stats['categories'][category] = stats['categories'].get(category, 0) + 1
            
            return stats
            
        except Exception as e:
            self.logger.error(f"获取匹配统计失败: {str(e)}")
            return {}
