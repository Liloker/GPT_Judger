# 使用官方的Python 3.8镜像作为基础镜像
FROM python:3.8

# 设置工作目录为/JudgeSys_app
WORKDIR /JudgeSys_app

# 将当前目录下的所有文件复制到容器的/app目录下
COPY . /JudgeSys_app

# 安装依赖包
RUN pip install --no-cache-dir -r requirements.txt

# 暴露容器的5431端口
EXPOSE 5431

# 设置环境变量
ENV NAME World

# 运行app.py文件
CMD ["python", "Server.py"]
