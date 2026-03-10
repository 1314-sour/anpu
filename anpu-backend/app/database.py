from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings
import pymysql

# 安装 pymysql 作为 MySQLdb
pymysql.install_as_MySQLdb()
# ... 你的其他 import 代码

# 找到你配置 URL 的变量，比如 SQLALCHEMY_DATABASE_URL
# 在 create_engine 之前加上这个 print：
print(f"------------->> DEBUG: 正在尝试连接数据库地址: {settings.DATABASE_URL}", flush=True)

# engine = create_engine(SQLALCHEMY_DATABASE_URL, ...)
# 创建数据库引擎
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=settings.DEBUG
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基类
Base = declarative_base()


def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
