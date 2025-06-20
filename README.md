# 通联支付订单抓取系统

自动从通联支付后台抓取订单数据并同步到Firebase实时数据库的Python工具。

## 功能特点

- ✅ 自动登录通联支付后台 (https://cus.allinpay.com/tranx/search)
- ✅ 支持验证码输入（手动输入）
- ✅ 抓取当日订单数据（交易时间、金额、订单号、支付方式、状态）
- ✅ 智能商品识别：48元=苏贵，20元=薯条，68元=苏贵+薯条
- ✅ 自动同步到Firebase实时数据库 `/orders_auto/{timestamp}` 路径
- ✅ 支持一次性运行或定时循环抓取
- ✅ 完整的日志记录和错误处理

## 安装与配置

### 1. 环境要求
- Python 3.11+
- 网络连接

### 2. 配置环境变量

复制 `.env.example` 为 `.env` 并填写配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```env
# 通联支付登录信息
TONGLIAN_LOGIN_URL=https://cus.allinpay.com/tranx/search
TONGLIAN_USERNAME=你的用户名
TONGLIAN_PASSWORD=你的密码

# Firebase配置
FIREBASE_CREDENTIALS_PATH=firebase-credentials.json
FIREBASE_DATABASE_URL=https://你的项目.firebaseio.com

# 同步配置
SYNC_INTERVAL=300

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=order_sync.log
```

### 3. Firebase配置

将Firebase服务账号密钥文件重命名为 `firebase-credentials.json` 并放在项目根目录。

## 使用方法

### 一次性抓取
```bash
python run.py --once
```

### 定时循环抓取（每5分钟）
```bash
python run.py --interval 300
```

### 使用原始程序（每10秒循环）
```bash
python main.py
```

## 数据结构

订单数据将保存到Firebase路径 `/orders_auto/{timestamp}`，格式如下：

```json
{
  "products": ["苏贵", "薯条"],
  "amount": 68,
  "createdAt": "2025-06-16 12:00:00",
  "source": "通联支付",
  "order_id": "202506161200001",
  "status": "处理成功",
  "payment_method": "微信支付"
}
```

## 商品匹配规则

在 `config.json` 中配置：

```json
{
  "products": {
    "mappings": [
      {
        "name": "苏贵",
        "exact_amount": 48,
        "description": "苏贵单品",
        "category": "主食"
      },
      {
        "name": "薯条",
        "exact_amount": 20,
        "description": "薯条单品",
        "category": "小食"
      },
      {
        "name": "苏贵+薯条",
        "exact_amount": 68,
        "description": "苏贵配薯条套餐",
        "category": "套餐",
        "combo_items": ["苏贵", "薯条"]
      }
    ]
  }
}
```

## 注意事项

1. **验证码输入**：登录时需要手动输入验证码，程序会显示验证码图片链接
2. **网络稳定性**：确保网络连接稳定，避免登录失败
3. **Firebase权限**：确保Firebase服务账号有读写权限
4. **日志监控**：查看 `order_sync.log` 了解运行状态

## 文件结构

```
.
├── main.py              # 主程序入口
├── run.py               # 简化运行脚本
├── order_scraper.py     # 订单抓取模块
├── firebase_sync.py     # Firebase同步模块
├── product_matcher.py   # 商品匹配模块
├── logger_config.py     # 日志配置模块
├── config.json          # 配置文件
├── .env                 # 环境变量（需要创建）
├── .env.example         # 环境变量示例
├── firebase-credentials.json  # Firebase凭证（需要上传）
└── README.md            # 说明文档
```

## 故障排除

### 1. 登录失败
- 检查用户名和密码是否正确
- 确认验证码输入正确
- 检查网络连接

### 2. Firebase同步失败
- 检查Firebase数据库URL是否正确
- 确认服务账号密钥文件是否有效
- 检查数据库读写权限

### 3. 订单解析失败
- 通联支付页面结构可能发生变化
- 查看日志文件获取详细错误信息

## 技术支持

如有问题，请查看日志文件 `order_sync.log` 或 `order_sync_error.log` 获取详细错误信息。