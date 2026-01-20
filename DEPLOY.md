# 🚀 部署指南

本文档介绍如何将生日祝福系统部署到生产环境。

## 目录

- [平台部署](#平台部署)
- [自建服务器部署](#自建服务器部署)
- [Docker部署](#docker部署)
- [Nginx反向代理配置](#nginx反向代理配置)
- [HTTPS配置](#https配置)

---

## 平台部署

### Railway 部署

Railway 是一个简单的云平台，支持从GitHub直接部署。

1. **Fork本项目到你的GitHub账号**

2. **登录 [Railway](https://railway.app/)**

3. **点击 New Project → Deploy from GitHub repo**

4. **选择Fork后的仓库**

5. **添加环境变量**（在 Variables 选项卡）：
```ini
# 必需配置
MAIL_SERVER=smtp.163.com
MAIL_PORT=465
MAIL_USER=your_email@163.com
MAIL_AUTH_CODE=your_auth_code
SECRET_KEY=<随机生成的密钥>

# 可选配置
DB_TYPE=sqlite
MAX_EMAILS_PER_HOUR=50
MAX_EMAILS_PER_DAY=200
```

6. **点击 Deploy**，等待部署完成

### Render 部署

1. **登录 [Render](https://render.com/)**

2. **点击 New → Web Service**

3. **连接GitHub仓库**

4. **配置**：
- Build Command: `pip install -r requirements.txt`
- Start Command: `gunicorn app:app`

5. **添加环境变量**（同Railway）

6. **Deploy**

---

## 自建服务器部署

### 系统要求

- **操作系统**: Ubuntu 20.04+ / CentOS 7+
- **Python**: 3.8+
- **内存**: 最低512MB，推荐1GB+
- **磁盘**: 最低10GB

### 部署步骤

#### 1. 更新系统

```bash
sudo apt update && sudo apt upgrade -y
```

#### 2. 安装Python和pip

```bash
sudo apt install python3 python3-pip python3-venv -y
```

#### 3. 安装依赖

```bash
sudo apt install sqlite3 nginx supervisor -y
```

#### 4. 创建部署目录

```bash
sudo mkdir -p /var/www/birthday-system
sudo chown $USER:$USER /var/www/birthday-system
cd /var/www/birthday-system
```

#### 5. 克隆项目

```bash
git clone <your-repo-url> .
```

#### 6. 创建虚拟环境

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn
```

#### 7. 配置环境变量

```bash
cp .env.example .env
nano .env  # 编辑配置
```

#### 8. 初始化数据库

```bash
cd auto_birthday_wisher
python init_db.py
```

#### 9. 配置Supervisor（进程管理）

```bash
sudo nano /etc/supervisor/conf.d/birthday-app.conf
```

添加以下内容：

```ini
[program:birthday-app]
directory=/var/www/birthday-system/auto_birthday_wisher
command=/var/www/birthday-system/venv/bin/gunicorn app:app
user=www-data
autostart=true
autorestart=true
stderr_logfile=/var/log/birthday-app.err.log
stdout_logfile=/var/log/birthday-app.out.log
```

启动服务：

```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start birthday-app
```

---

## Docker部署

### 使用Docker Compose

1. **安装Docker和Docker Compose**

```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo apt install docker-compose -y
```

2. **创建docker-compose.yml**

```yaml
version: '3.8'

services:
  app:
    build: ./auto_birthday_wisher
    container_name: birthday-app
    restart: always
    ports:
      - "5001:5000"
    environment:
      - FLASK_ENV=production
      - DB_TYPE=sqlite
    env_file:
      - .env
    volumes:
      - ./data:/app/data

  nft:
    build: ./nft_minter
    container_name: birthday-nft
    restart: always
    ports:
      - "5002:5000"
    env_file:
      - .env
```

3. **启动服务**

```bash
docker-compose up -d
```

4. **查看日志**

```bash
docker-compose logs -f
```

---

## Nginx反向代理配置

### 基础配置

```bash
sudo nano /etc/nginx/sites-available/birthday-system
```

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # 邮件系统
    location / {
        proxy_pass http://127.0.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # NFT系统
    location /nft/ {
        proxy_pass http://127.0.0.1:5002/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        rewrite ^/nft/(.*) /$1 break;
    }
}
```

启用配置：

```bash
sudo ln -s /etc/nginx/sites-available/birthday-system /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

## HTTPS配置

### 使用Let's Encrypt免费证书

1. **安装Certbot**

```bash
sudo apt install certbot python3-certbot-nginx -y
```

2. **获取证书**

```bash
sudo certbot --nginx -d your-domain.com
```

3. **自动续期**

Certbot会自动配置续期任务，可以通过以下命令验证：

```bash
sudo certbot renew --dry-run
```

---

## 生产环境注意事项

### 安全清单

- [ ] 修改默认管理员密码
- [ ] 设置强SECRET_KEY
- [ ] 使用HTTPS
- [ ] 配置防火墙
- [ ] 定期备份数据库
- [ ] 监控日志文件

### 性能优化

- 使用Gunicorn或uWSGI代替Flask开发服务器
- 配置Nginx作为反向代理
- 使用Redis作为缓存
- 静态文件使用CDN

### 数据备份

```bash
# 备份SQLite数据库
cp auto_birthday_wisher/birthday.db backup/birthday-$(date +%Y%m%d).db

# 自动备份脚本（添加到crontab）
0 2 * * * cp /var/www/birthday-system/auto_birthday_wisher/birthday.db /backup/birthday-$(date +\%Y\%m\%d).db
```

---

## 故障排查

### 服务无法启动

```bash
# 检查日志
tail -f auto_birthday_wisher/logs/app.log
tail -f auto_birthday_wisher/logs/error.log

# 检查端口占用
sudo netstat -tlnp | grep 5001
```

### 邮件发送失败

1. 检查SMTP配置是否正确
2. 确认邮箱授权码（不是登录密码）
3. 检查速率限制状态

### 数据库连接错误

1. 确认数据库文件存在
2. 检查文件权限
3. 检查数据库配置路径

---

## 更新部署

```bash
cd /var/www/birthday-system
git pull origin main
source venv/bin/activate
pip install -r requirements.txt --upgrade
sudo supervisorctl restart birthday-app
```
