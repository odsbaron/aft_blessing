# 🎂 自动化生日祝福系统 + NFT纪念币

一个完整的生日自动化管理系统，支持邮件祝福发送和链上NFT纪念币铸造。

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/MIT-MIT.svg)](LICENSE)

## ✨ 功能特性

### 📧 邮件祝福系统
- **每日自动扫描**生日用户并发送祝福邮件
- **精美HTML邮件模板**，支持自定义设计
- **防重复发送**机制，同一年度只发送一次
- **邮件速率限制**，防止触发服务商限制
- **Web管理后台**，可视化管理用户和祝福语

### 🎨 NFT纪念币系统
- **一键铸造**生日纪念NFT（Polygon链）
- **每地址每年限领**一次，链上强制执行
- **免费铸造**（Gas费用由系统承担）
- **IPFS存储**NFT元数据
- **MetaMask钱包**连接支持

### 🔐 安全特性
- **用户登录认证**系统
- **密码强度验证**
- **会话管理**（12小时有效期）
- **管理员权限**控制

## 📁 项目结构

```
邮件系统开发/
├── auto_birthday_wisher/     # 邮件祝福系统
│   ├── app.py                 # Flask Web应用
│   ├── main.py                # 定时任务主程序
│   ├── db_manager.py          # 数据库管理
│   ├── email_service.py       # 邮件发送服务
│   ├── email_template.py      # 邮件模板管理
│   ├── auth.py                # 用户认证模块
│   ├── rate_limiter.py        # 速率限制器
│   ├── validators.py          # 输入验证
│   ├── config.py              # 配置文件
│   ├── templates/             # HTML模板
│   ├── static/                # 静态资源
│   └── logs/                  # 日志文件
│
├── nft_minter/                # NFT铸造系统
│   ├── app.py                 # Flask Web应用
│   ├── web3_handler.py        # Web3交互
│   ├── ipfs_handler.py        # IPFS文件上传
│   ├── contracts/             # 智能合约
│   └── templates/             # HTML模板
│
├── tests/                     # 单元测试
├── docker-compose.yml         # Docker编排
├── README.md                  # 本文档
└── DEPLOY.md                  # 部署指南
```

## 🚀 快速开始

### 环境要求

- Python 3.8+
- SQLite / MySQL / PostgreSQL
- SMTP邮箱账户

### 安装步骤

1. **克隆项目**
```bash
git clone <repository-url>
cd 邮件系统开发
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **配置环境变量**
```bash
cp .env.example .env
# 编辑 .env 文件，填入邮箱配置
```

4. **初始化数据库**
```bash
cd auto_birthday_wisher
python init_db.py
```

5. **启动Web服务**
```bash
python app.py
```

访问 http://localhost:5001 开始使用！

**默认账户：** `admin` / `admin123`（首次登录后请修改）

## 📖 使用指南

### 配置邮箱

编辑 `auto_birthday_wisher/.env` 文件：

```ini
MAIL_SERVER=smtp.163.com
MAIL_PORT=465
MAIL_USER=your_email@163.com
MAIL_AUTH_CODE=your_authorization_code
MAIL_FROM_NAME=生日祝福助手
```

### 添加用户

方式一：Web界面添加
- 登录后台 → 用户管理 → 添加用户

方式二：CSV批量导入
```bash
cd auto_birthday_wisher
python import_users.py users.csv
```

CSV格式：
```csv
姓名,邮箱,生日
张三,zhangsan@example.com,1990-01-01
李四,lisi@example.com,1995-05-15
```

### 自定义邮件模板

登录后台 → 邮件模板 → 创建模板

可用变量：
- `{name}` - 收件人姓名
- `{wish}` - 祝福语内容
- `{from_name}` - 发件人名称
- `{year}` - 当前年份
- `{age}` - 收件人年龄

### 部署NFT合约

1. 配置私钥（`.env`文件）
2. 登录NFT管理后台
3. 点击"部署合约"
4. 确认交易

## 🔧 配置说明

### 速率限制配置

```ini
MAX_EMAILS_PER_HOUR=50      # 每小时最大发送数
MAX_EMAILS_PER_DAY=200       # 每日最大发送数
EMAIL_COOLDOWN_SECONDS=300   # 同一收件人冷却时间
MIN_EMAIL_INTERVAL=2         # 发送间隔（秒）
```

### 数据库配置

支持三种数据库，通过 `DB_TYPE` 环境变量切换：

```ini
# SQLite（默认，适合小型部署）
DB_TYPE=sqlite
DB_SQLITE_PATH=birthday.db

# MySQL
DB_TYPE=mysql
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASS=your_password
DB_NAME=birthday_db

# PostgreSQL
DB_TYPE=postgresql
DATABASE_URL=postgresql://user:pass@host:5432/dbname
```

## 🐳 Docker部署

```bash
docker-compose up -d
```

服务将运行在：
- Web服务: http://localhost:5001
- NFT服务: http://localhost:5002

## 📝 API文档

### 邮件系统API

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/stats` | GET | 获取统计数据 |
| `/api/upcoming-birthdays` | GET | 获取即将过生日的用户 |
| `/api/rate-limit` | GET | 获取速率限制状态 |

### NFT系统API

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/nft/check` | POST | 检查地址是否可铸造 |
| `/api/nft/mint` | POST | 铸造NFT |
| `/api/ipfs/upload` | POST | 上传文件到IPFS |

## 🧪 测试

```bash
# 运行所有测试
python run_tests.py

# 运行特定测试
python -m pytest tests/test_rate_limiter.py
```

## 📄 开源协议

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📧 联系方式

如有问题请提交 Issue。
