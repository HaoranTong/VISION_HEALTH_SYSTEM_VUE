# 文件路径: E:\DEV_CONTEXT\1_Projects\VISION_HEALTH_SYSTEM_VUE\config\app\config.py
import os


class DevelopmentConfig:
    # 数据库配置
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(os.getcwd(), 'instance/app.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 安全密钥
    SECRET_KEY = "your-secret-key-here"

    # 文件上传配置
    UPLOAD_FOLDER = os.path.join(os.getcwd(), "instance/uploads")
    ALLOWED_EXTENSIONS = {"xlsx"}
