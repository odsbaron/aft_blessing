# 自动化生日祝福邮件系统
## Auto-Birthday-Wisher

一个轻量级的自动化生日祝福系统，每日定时扫描用户数据库，自动发送生日祝福邮件。

### 功能特点

- **Web管理界面** - 可视化管理用户、祝福语和发送日志
- **定时调度** - 每日固定时间自动触发
- **精准匹配** - 自动识别当天过生日的用户
- **随机祝福** - 从语料库随机抽取祝福语，避免千篇一律
- **防重机制** - 记录发送年份，同一天不会重复发送
- **精美邮件** - HTML 格式邮件模板
- **发送日志** - 完整的发送记录，便于追踪
- **批量导入** - 支持CSV批量导入用户数据

### 快速开始

#### 1. 安装依赖

```bash
pip install -r requirements.txt
```

#### 2. 配置环境变量

复制 `.env.example` 为 `.env`，并填写配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件：
- 配置邮箱服务器信息（网易/QQ邮箱等）
- 配置数据库连接信息

#### 3. 初始化数据库

```bash
python init_db.py
```

#### 4. 导入用户数据

创建用户数据 CSV 文件（或使用示例）：

```bash
python import_users.py --sample  # 创建示例文件
```

然后编辑 `users_sample.csv`，导入用户：

```bash
python import_users.py users_sample.csv
```

#### 5. 启动服务

**Web管理界面（推荐）**

```bash
# 方式一：使用启动脚本
./start_web.sh      # Linux/Mac
start_web.bat       # Windows

# 方式二：直接运行
python app.py
```

访问地址：http://127.0.0.1:5000

**命令行模式**

```bash
# 守护进程模式（每天定时执行）
python main.py

# 立即执行一次（测试用）
python main.py --once
```

### Web管理界面功能

| 功能模块 | 说明 |
|---------|------|
| 仪表盘 | 查看系统统计、即将过生日的用户、最近发送记录 |
| 用户管理 | 添加、编辑、删除用户，批量导入CSV |
| 祝福语管理 | 添加、启用/禁用、删除祝福语 |
| 发送日志 | 查看历史发送记录和状态 |
| 手动发送 | 向指定用户发送测试邮件 |

### 文件说明

| 文件 | 说明 |
|------|------|
| `app.py` | Web管理界面主程序 |
| `config.py` | 配置文件加载 |
| `db_manager.py` | 数据库操作 |
| `email_service.py` | 邮件发送 |
| `main.py` | 命令行主程序入口 |
| `init_db.py` | 数据库初始化 |
| `import_users.py` | 批量导入用户 |
| `templates/` | HTML模板文件 |
| `static/` | CSS样式和静态资源 |

### CSV 导入格式

```csv
name,email,dob
张三,zhangsan@example.com,1995-01-17
李四,lisi@example.com,1998-06-23
```

### 常见问题

**Q: 如何获取邮箱授权码？**

A: 以网易邮箱为例：
1. 登录网易邮箱网页版
2. 设置 -> POP3/SMTP/IMAP
3. 开启 SMTP 服务并获取授权码

**Q: 数据库支持哪些？**

A: 目前支持 MySQL，需要安装 pymysql 驱动。

**Q: 如何修改发送时间？**

A: 编辑 `.env` 文件中的 `SEND_TIME=09:00`。

### 许可证

MIT License
