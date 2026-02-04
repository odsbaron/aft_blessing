# Docker 部署指南

## 一键部署（推荐）

```bash
# 1. 上传项目到服务器后，进入项目目录
cd auto_birthday_wisher

# 2. 给脚本添加执行权限
chmod +x deploy.sh

# 3. 运行部署脚本
./deploy.sh
```

---

## 手动部署

### 步骤 1: 安装 Docker

```bash
curl -fsSL https://get.docker.com | sh
systemctl start docker
systemctl enable docker
```

### 步骤 2: 配置环境变量

```bash
# 复制配置文件
cp .env.example .env

# 编辑配置
nano .env
```

修改以下配置：

```bash
MAIL_SERVER=smtp.163.com        # 改成你的邮箱服务器
MAIL_PORT=465                    # 端口
MAIL_USER=你的邮箱@163.com       # 改成你的邮箱
MAIL_AUTH_CODE=邮箱授权码        # 改成你的授权码
MAIL_FROM_NAME=生日祝福助手      # 发件人名称
SECRET_KEY=随机字符串            # 安全密钥
```

### 步骤 3: 启动服务

```bash
# 构建并启动
docker-compose up -d

# 查看日志
docker-compose logs -f
```

### 步骤 4: 开放防火墙端口

**云服务器安全组开放 5001 端口**

或使用防火墙命令：

```bash
# firewall-cmd
firewall-cmd --permanent --add-port=5001/tcp
firewall-cmd --reload

# iptables
iptables -I INPUT -p tcp --dport 5001 -j ACCEPT
```

---

## 访问系统

```
http://你的服务器IP:5001
```

默认登录：
- 用户名: `admin`
- 密码: `admin123`

---

## 常用命令

| 命令 | 说明 |
|------|------|
| `docker-compose logs -f` | 查看实时日志 |
| `docker-compose restart` | 重启服务 |
| `docker-compose stop` | 停止服务 |
| `docker-compose down` | 停止并删除容器 |
| `docker-compose exec web bash` | 进入容器 |
| `docker-compose exec web python init_db.py` | 重新初始化数据库 |

---

## 数据备份

```bash
# 备份数据库
docker cp birthday-app:/app/data/birthday.db ./backup_$(date +%Y%m%d).db

# 恢复数据库
docker cp ./backup_20240203.db birthday-app:/app/data/birthday.db
```

---

## 更新代码

```bash
# 拉取最新代码
git pull

# 重新构建并启动
docker-compose up -d --build
```

---

## 故障排查

**问题：端口被占用**
```bash
# 查看占用端口的进程
lsof -i :5001
# 杀掉进程
kill -9 <PID>
```

**问题：容器无法启动**
```bash
# 查看容器日志
docker-compose logs

# 重新构建
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

**问题：数据库文件丢失**
- 数据存储在 `./data` 目录，确保此目录已挂载
- 检查 `docker-compose.yml` 中的 volumes 配置
