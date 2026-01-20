# 🐳 Docker一键部署指南

本指南提供使用Docker在服务器上快速部署生日祝福系统的完整步骤。

## 📋 前置要求

- 一台运行Linux的服务器（Ubuntu 20.04+ 推荐）
- 服务器内存至少512MB，推荐1GB+
- root权限或sudo权限
- 一个SMTP邮箱账户（用于发送邮件）

---

## 🚀 快速部署（3步完成）

### 步骤1：上传代码到服务器

**方式一：SCP上传（本地执行）**
```bash
scp -r /本地路径/邮件系统开发 root@your-server-ip:/root/
```

**方式二：Git克隆（服务器上执行）**
```bash
git clone <your-repo-url>
cd 邮件系统开发
```

**方式三：SFTP上传**
使用 FileZilla、WinSCP 等工具上传整个项目文件夹。

---

### 步骤2：一键部署脚本

创建并运行部署脚本：

```bash
# 创建部署脚本
cat > deploy.sh << 'EOF'
#!/bin/bash

set -e

echo "╔═══════════════════════════════════════════════════════╗"
echo "║         🎂 生日祝福系统 Docker 部署脚本              ║"
echo "╚═══════════════════════════════════════════════════════╝"
echo ""

# 检查是否为root用户
if [ "$EUID" -ne 0 ]; then
    echo "❌ 请使用 root 用户执行此脚本"
    exit 1
fi

# 检查Docker是否已安装
if ! command -v docker &> /dev/null; then
    echo "📦 安装 Docker..."
    curl -fsSL https://get.docker.com | sh
    systemctl start docker
    systemctl enable docker
    echo "✅ Docker 安装完成"
else
    echo "✅ Docker 已安装"
fi

# 检查Docker Compose是否已安装
if ! command -v docker-compose &> /dev/null; then
    echo "📦 安装 Docker Compose..."
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    echo "✅ Docker Compose 安装完成"
else
    echo "✅ Docker Compose 已安装"
fi

# 检查.env文件
if [ ! -f .env ]; then
    echo ""
    echo "⚙️  配置环境变量"
    echo "=================================="

    read -p "📧 请输入邮箱地址: " MAIL_USER
    read -sp "🔑 请输入邮箱授权码(不是登录密码): " MAIL_AUTH_CODE
    echo ""

    # 生成随机密钥
    SECRET_KEY=$(openssl rand -hex 32)

    # 创建.env文件
    cat > .env << ENVEOF
# ========== 邮件配置 ==========
MAIL_SERVER=smtp.163.com
MAIL_PORT=465
MAIL_USER=$MAIL_USER
MAIL_AUTH_CODE=$MAIL_AUTH_CODE
MAIL_FROM_NAME=生日祝福助手

# ========== 数据库配置 ==========
DB_TYPE=sqlite

# ========== 安全配置 ==========
SECRET_KEY=$SECRET_KEY

# ========== 速率限制配置 ==========
MAX_EMAILS_PER_HOUR=50
MAX_EMAILS_PER_DAY=200
EMAIL_COOLDOWN_SECONDS=300
MIN_EMAIL_INTERVAL=2
ENVEOF

    echo "✅ 配置文件已创建: .env"
else
    echo "✅ 配置文件已存在"
fi

# 初始化数据库
echo ""
echo "🗄️  初始化数据库..."
if [ ! -f auto_birthday_wisher/birthday.db ]; then
    cd auto_birthday_wisher
    python init_db.py
    cd ..

    # 创建管理员用户
    python3 << PYEOF
import hashlib
pwd_hash = hashlib.sha256('admin123'.encode()).hexdigest()
import sqlite3
conn = sqlite3.connect('auto_birthday_wisher/birthday.db')
cursor = conn.cursor()
cursor.execute("INSERT INTO admin_users (username, password_hash, role, is_active, password_changed) VALUES (?, ?, ?, ?, ?)",
               ('admin', pwd_hash, 'admin', 1, 0))
conn.commit()
conn.close()
print("✅ 默认管理员账户已创建")
PYEOF
else
    echo "✅ 数据库已存在"
fi

# 启动服务
echo ""
echo "🚀 启动 Docker 服务..."
docker-compose down 2>/dev/null || true
docker-compose up -d --build

# 等待服务启动
echo ""
echo "⏳ 等待服务启动..."
sleep 5

# 检查服务状态
echo ""
if docker-compose ps | grep -q "Up"; then
    echo "🎉 部署成功！"
    echo ""
    echo "📍 访问地址:"
    echo "   Web管理: http://$(hostname -I | awk '{print $1}'):5001"
    echo ""
    echo "🔑 默认账户: admin / admin123"
    echo "   ⚠️  请在首次登录后修改密码！"
    echo ""
    echo "📋 常用命令:"
    echo "   查看日志: docker-compose logs -f"
    echo "   停止服务: docker-compose down"
    echo "   重启服务: docker-compose restart"
else
    echo "❌ 服务启动失败，请检查日志: docker-compose logs"
fi
EOF

# 添加执行权限并运行
chmod +x deploy.sh
./deploy.sh
```

---

### 步骤3：访问系统

部署成功后，在浏览器中访问：

```
http://your-server-ip:5001
```

**默认登录账户：**
- 用户名：`admin`
- 密码：`admin123`

---

## 📋 手动部署步骤（备选方案）

如果自动脚本无法运行，可以手动执行以下步骤：

### 1. 安装Docker

```bash
# 更新软件包索引
sudo apt update

# 安装依赖
sudo apt install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# 添加Docker官方GPG密钥
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# 设置Docker稳定版仓库
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# 安装Docker Engine
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io

# 安装Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 验证安装
docker --version
docker-compose --version

# 启动Docker服务
sudo systemctl start docker
sudo systemctl enable docker
```

### 2. 配置环境变量

```bash
cd 邮件系统开发

# 创建配置文件
cp .env.example .env
nano .env  # 编辑配置，至少填入邮箱信息
```

必须配置项：
```ini
MAIL_USER=your_email@163.com
MAIL_AUTH_CODE=your_smtp_auth_code
SECRET_KEY=random_string_here
```

### 3. 初始化数据库

```bash
cd auto_birthday_wisher
python init_db.py
```

### 4. 启动服务

```bash
cd ..
docker-compose up -d --build
```

### 5. 验证部署

```bash
# 检查容器状态
docker-compose ps

# 查看日志
docker-compose logs -f app

# 测试访问
curl http://localhost:5001
```

---

## 🔧 配置Nginx反向代理（可选）

如果需要使用域名和HTTPS，配置Nginx：

### 安装Nginx

```bash
sudo apt install nginx -y
```

### 创建站点配置

```bash
sudo nano /etc/nginx/sites-available/birthday
```

配置内容：
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 启用配置

```bash
sudo ln -s /etc/nginx/sites-available/birthday /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 配置HTTPS（Let's Encrypt免费证书）

```bash
# 安装Certbot
sudo apt install certbot python3-certbot-nginx -y

# 获取证书
sudo certbot --nginx -d your-domain.com

# 证书会自动续期
```

---

## 📝 常用Docker运维命令

### 查看日志

```bash
# 查看所有服务日志
docker-compose logs

# 查看特定服务日志
docker-compose logs app

# 实时跟踪日志
docker-compose logs -f app

# 查看最近100行日志
docker-compose logs --tail=100 app
```

### 服务管理

```bash
# 启动服务
docker-compose up -d

# 停止服务
docker-compose down

# 重启服务
docker-compose restart

# 重新构建并启动
docker-compose up -d --build

# 只重新构建不启动
docker-compose build
```

### 容器操作

```bash
# 进入容器Shell
docker-compose exec app bash

# 在容器中执行命令
docker-compose exec app python init_db.py

# 查看容器资源使用
docker stats
```

### 更新部署

```bash
# 1. 拉取最新代码
git pull

# 2. 停止服务
docker-compose down

# 3. 重新构建并启动
docker-compose up -d --build
```

---

## 🔥 防火墙配置

```bash
# 安装UFW防火墙
sudo apt install ufw -y

# 配置防火墙规则
sudo ufw allow 22      # SSH
sudo ufw allow 80      # HTTP
sudo ufw allow 443     # HTTPS

# 启用防火墙
sudo ufw enable

# 查看防火墙状态
sudo ufw status
```

---

## 🐛 故障排查

### 问题1：容器启动失败

```bash
# 查看详细日志
docker-compose logs app

# 检查容器状态
docker-compose ps

# 重新构建
docker-compose down
docker-compose up -d --build
```

### 问题2：无法访问Web界面

```bash
# 检查服务是否运行
docker-compose ps

# 检查端口是否开放
sudo netstat -tlnp | grep 5001

# 检查防火墙
sudo ufw status
```

### 问题3：邮件发送失败

```bash
# 进入容器检查配置
docker-compose exec app cat .env

# 测试邮件服务
docker-compose exec app python -c "from email_service import send_test_email; send_test_email('your@email.com')"
```

### 问题4：数据库连接错误

```bash
# 检查数据库文件
docker-compose exec app ls -la /app/data/

# 重新初始化数据库
docker-compose exec app python init_db.py
```

---

## 📊 监控和维护

### 查看资源使用

```bash
# Docker资源使用
docker stats

# 磁盘使用
df -h

# 内存使用
free -h
```

### 备份数据

```bash
# 备份数据库
cp auto_birthday_wisher/birthday.db backup/birthday-$(date +%Y%m%d).db

# 自动备份脚本（添加到crontab）
crontab -e
# 添加：0 2 * * * cp /root/邮件系统开发/auto_birthday_wisher/birthday.db /backup/birthday-$(date +\%Y\%m\%d).db
```

### 清理日志

```bash
# 清理Docker日志
docker system prune -a

# 清理应用日志（保留最近7天）
find auto_birthday_wisher/logs/ -name "*.log" -mtime +7 -delete
```

---

## 🔄 更新部署

```bash
cd 邮件系统开发

# 拉取最新代码
git pull origin main

# 重新部署
docker-compose down
docker-compose up -d --build
```

---

## 📞 获取帮助

如遇到问题，请检查：
1. Docker和Docker Compose版本是否正确
2. 端口5001是否被占用
3. 防火墙是否正确配置
4. 服务器资源是否充足

提交Issue时请附上：
- 服务器系统版本
- Docker版本信息
- 错误日志（`docker-compose logs`）
