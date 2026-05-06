# 使用 Python 3.10虚拟 环境
FROM python:3.10-slim

# 设置容器内工作目录
WORKDIR /app

# 先复制依赖清单（利用缓存加速）
COPY requirements.txt .

# 安装依赖 (使用清华源加速)
# 确保 requirements.txt 里写了 uvicorn
RUN python -m pip install --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.org/simple

# 复制所有代码进去
COPY . .

# 暴露端口 (根据你后端实际端口修改，比如 8000)
EXPOSE 8000

# 启动命令 (请修改为你实际的启动文件名，比如 app.py 或 main.py)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]