# Railway 部署指南

## 部署步骤

### 1. 准备代码

```bash
# 将项目推送到 GitHub
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/你的用户名/birthday-wisher.git
git push -u origin main
```

### 2. 部署到 Railway

1. 访问 [railway.app](https://railway.app/)
2. 使用 GitHub 账号登录
3. 点击 **New Project** → **Deploy from GitHub repo**
4. 选择你的仓库
5. Railway 会自动检测并部署

### 3. 配置数据库

1. 在项目中点击 **New Service** → **Database** → **Add PostgreSQL**
2. 数据库创建后，点击进入
3. 在 **Variables** 标签页可以看到：
   - `PGHOST`
   - `PGPORT`
   - `PGUSER`
   - `PGPASSWORD`
   - `PGDATABASE`
   - `DATABASE_URL` (连接字符串)

### 4. 配置环境变量

在 Web 服务的 **Variables** 标签页添加：

```bash
# 邮件配置
MAIL_SERVER=smtp.163.com
MAIL_PORT=465
MAIL_USER=你的邮箱@163.com
MAIL_AUTH_CODE=邮箱授权码

# 数据库配置（使用 Railway PostgreSQL）
DB_TYPE=postgresql
DB_URL=${{PostgreSQL.DATABASE_URL}}

# 发送时间
SEND_TIME=09:00

# Flask 密钥
SECRET_KEY=your-random-secret-key
```

### 5. 初始化数据库

Railway 部署后，访问应用，运行：

```bash
# 在 Railway Console 中执行
python init_db.py
```

或者通过临时域名访问后手动添加用户。

### 6. 配置定时任务

Railway 支持 Cron Jobs，但需要单独配置：

1. 创建一个新的 Service
2. 选择 **Deploy from GitHub repo**（同一个仓库）
3. 设置环境变量 `COMMAND=python main.py`
4. 添加 Cron 表达式，如 `0 9 * * *`（每天9点）

---

## Railway 环境变量说明

Railway 会自动提供以下变量：

| 变量名 | 说明 | 示例 |
|--------|------|------|
| `DATABASE_URL` | PostgreSQL 连接字符串 | `postgresql://...` |
| `PORT` | 服务端口 | 自动分配 |
| `RAILWAY_ENVIRONMENT` | 环境 | `production` |

---

## 更新代码

```bash
# 本地修改后推送
git add .
git commit -m "Update"
git push

# Railway 会自动重新部署
```

---

## 常见问题

**Q: 定时任务不工作？**
- Railway 的免费版不会一直运行 Worker
- 解决：使用 Railway Cron + 每日触发

**Q: 数据库数据丢失？**
- Railway 重新部署会重置文件系统
- 必须使用 PostgreSQL 服务存储数据

**Q: 如何查看日志？**
- 在项目中选择 Service → View Logs
