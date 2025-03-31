# 文件名称：database.py
# 完整路径：backend/infrastructure/database.py
# 功能说明：全局数据库实例管理

from flask_sqlalchemy import SQLAlchemy

# 创建全局唯一数据库实例
db = SQLAlchemy()
