FROM python:3.11-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制代码
COPY . .

# 创建数据目录
RUN mkdir -p /app/data

# 暴露端口
EXPOSE 5001

# 启动（容器运行后手动初始化数据库）
CMD ["sh", "-c", "if [ ! -f /app/data/birthday.db ]; then python init_db.py; fi && gunicorn app:app --bind 0.0.0.0:5001 --workers 2"]
