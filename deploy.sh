#!/bin/bash
# Docker 部署脚本

set -e

echo "======================================"
echo "   生日祝福系统 - Docker 部署脚本"
echo "======================================"
echo ""

# 检查 Docker 是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安装，正在安装..."
    curl -fsSL https://get.docker.com | sh
    systemctl start docker
    systemctl enable docker
    echo "✅ Docker 安装完成"
fi

# 检查 Docker Compose
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose 未安装，正在安装..."
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    echo "✅ Docker Compose 安装完成"
fi

# 创建数据目录
echo "📁 创建数据目录..."
mkdir -p data

# 检查 .env 文件
if [ ! -f .env ]; then
    echo "⚠️  .env 文件不存在，从 .env.example 复制..."
    cp .env.example .env
    echo "⚠️  请编辑 .env 文件，填入你的配置信息！"
    echo "   nano .env"
    echo ""
    read -p "是否现在编辑配置文件？(y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        nano .env
    fi
fi

# 停止旧容器
echo "🛑 停止旧容器..."
docker-compose down 2>/dev/null || docker down 2>/dev/null || true

# 构建镜像
echo "🔨 构建 Docker 镜像..."
docker-compose build

# 启动容器
echo "🚀 启动容器..."
docker-compose up -d

# 初始化数据库
echo "📊 初始化数据库..."
docker-compose exec -T web python init_db.py || echo "数据库已初始化"

echo ""
echo "======================================"
echo "✅ 部署完成！"
echo "======================================"
echo ""
echo "📋 服务信息:"
echo "   访问地址: http://$(hostname -I | awk '{print $1}'):5001"
echo "   容器名称: birthday-app"
echo ""
echo "📝 常用命令:"
echo "   查看日志: docker-compose logs -f"
echo "   重启服务: docker-compose restart"
echo "   停止服务: docker-compose down"
echo "   进入容器: docker-compose exec web bash"
echo ""
