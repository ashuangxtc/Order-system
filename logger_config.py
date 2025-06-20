#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日志配置模块
提供统一的日志配置和管理
"""

import os
import json
import logging
import logging.handlers
from datetime import datetime

def setup_logger(name='order_sync', config_file='config.json'):
    """设置日志配置"""
    
    # 加载配置
    log_config = _load_log_config(config_file)
    
    # 创建logger
    logger = logging.getLogger(name)
    
    # 清除现有处理器
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # 设置日志级别
    log_level = getattr(logging, log_config.get('level', 'INFO').upper())
    logger.setLevel(log_level)
    
    # 创建格式器
    formatter = logging.Formatter(
        log_config.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s'),
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 文件处理器
    log_file = os.getenv('LOG_FILE', 'order_sync.log')
    try:
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=_parse_size(log_config.get('max_file_size', '10MB')),
            backupCount=log_config.get('max_log_files', 10),
            encoding='utf-8'
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        logger.warning(f"无法创建文件日志处理器: {str(e)}")
    
    # 错误日志文件处理器
    try:
        error_file = log_file.replace('.log', '_error.log')
        error_handler = logging.handlers.RotatingFileHandler(
            error_file,
            maxBytes=_parse_size('10MB'),
            backupCount=5,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        logger.addHandler(error_handler)
    except Exception as e:
        logger.warning(f"无法创建错误日志处理器: {str(e)}")
    
    # 记录启动信息
    logger.info("=" * 50)
    logger.info("日志系统初始化完成")
    logger.info(f"日志级别: {log_config.get('level', 'INFO')}")
    logger.info(f"日志文件: {log_file}")
    logger.info(f"启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 50)
    
    return logger

def _load_log_config(config_file):
    """加载日志配置"""
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config.get('logging', {})
    except Exception:
        # 返回默认配置
        return {
            'level': 'INFO',
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            'max_log_files': 10,
            'max_file_size': '10MB'
        }

def _parse_size(size_str):
    """解析文件大小字符串"""
    try:
        size_str = size_str.upper()
        if size_str.endswith('KB'):
            return int(float(size_str[:-2]) * 1024)
        elif size_str.endswith('MB'):
            return int(float(size_str[:-2]) * 1024 * 1024)
        elif size_str.endswith('GB'):
            return int(float(size_str[:-2]) * 1024 * 1024 * 1024)
        else:
            return int(size_str)
    except:
        return 10 * 1024 * 1024  # 默认10MB

def get_logger(name=None):
    """获取logger实例"""
    if name is None:
        name = 'order_sync'
    return logging.getLogger(name)

def log_exception(logger, message="异常信息"):
    """记录异常信息"""
    logger.exception(message)

def log_performance(logger, operation, start_time, end_time):
    """记录性能信息"""
    duration = end_time - start_time
    logger.info(f"操作 [{operation}] 耗时: {duration:.2f}秒")

def create_operation_logger(operation_name):
    """为特定操作创建专用logger"""
    logger_name = f"order_sync.{operation_name}"
    return logging.getLogger(logger_name)

# 预定义的专用loggers
scraper_logger = create_operation_logger('scraper')
firebase_logger = create_operation_logger('firebase')
matcher_logger = create_operation_logger('matcher')
