# 通联支付登录解决方案

## 当前状况
系统已正确识别登录表单字段并建立了多种登录工具，但由于验证码时效性问题，需要手动完成登录过程。

## 解决方案

### 方案1：使用Web界面登录（推荐）
1. 运行Web登录服务器：
   ```bash
   python web_login_server.py
   ```

2. 在浏览器中访问：http://localhost:5000

3. 按照页面提示操作：
   - 点击"获取新验证码"
   - 查看验证码图片
   - 输入验证码
   - 点击"执行登录"

4. 登录成功后，Cookie会自动保存到配置文件

### 方案2：手动更新Cookie
如果你有其他方式获取到有效的Cookie，可以直接更新user.env文件：

```
TONGLIAN_COOKIE_USERID=你的userid值
TONGLIAN_COOKIE_SESSION=你的session值
```

## 系统架构
- **order_scraper_requests.py**: 订单抓取核心逻辑
- **firebase_sync.py**: Firebase数据同步
- **product_matcher.py**: 商品智能匹配
- **main.py**: 主程序入口
- **web_login_server.py**: Web登录界面

## 下一步
一旦获得有效Cookie，主程序将：
1. 自动抓取订单数据
2. 智能匹配商品信息
3. 同步到Firebase数据库
4. 持续监控新订单