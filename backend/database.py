import os
from sqlalchemy import create_engine, Column, Integer, String, JSON, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
from sqlalchemy.pool import QueuePool
from tenacity import retry, stop_after_attempt, wait_exponential
import logging
from typing import Generator
from alembic import command
from alembic.config import Config
from pathlib import Path

# 配置日志
logger = logging.getLogger(__name__)

# 数据库连接池配置
POOL_SIZE = 5
MAX_OVERFLOW = 10
POOL_TIMEOUT = 30  # 秒
CONNECT_TIMEOUT = 10  # 秒

# 数据库配置
SQLALCHEMY_DATABASE_URL = "sqlite:///./game_history.db"

# 创建带连接池的引擎
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    poolclass=QueuePool,
    pool_size=POOL_SIZE,
    max_overflow=MAX_OVERFLOW,
    pool_timeout=POOL_TIMEOUT,
    connect_args={
        "check_same_thread": False,
        "timeout": CONNECT_TIMEOUT
    }
)

# 带重试机制的会话工厂
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    before_sleep=lambda retry_state: logger.warning(
        f"Retrying database connection (attempt {retry_state.attempt_number})..."
    )
)
def create_session() -> Session:
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 数据库模型
class GameHistory(Base):
    __tablename__ = "game_history"
    
    id = Column(Integer, primary_key=True, index=True)
    game_id = Column(String, index=True)
    game_type = Column(String)
    move = Column(String)
    player = Column(String)
    state = Column(JSON)
    timestamp = Column(DateTime, default=datetime.utcnow)

class LLMRecord(Base):
    __tablename__ = "llm_records"
    
    id = Column(Integer, primary_key=True, index=True)
    model = Column(String)
    prompt = Column(String)
    response = Column(String)
    usage = Column(JSON)
    timestamp = Column(DateTime, default=datetime.utcnow)

class ChatRecord(Base):
    __tablename__ = "chat_records"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True)
    role = Column(String)
    content = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)

class LLMConfig(Base):
    __tablename__ = "llm_config"
    
    id = Column(Integer, primary_key=True, index=True)
    model = Column(String, unique=True)
    api_key = Column(String)
    endpoint = Column(String)
    is_active = Column(Integer, default=0)
    timestamp = Column(DateTime, default=datetime.utcnow)

# 创建数据库表
Base.metadata.create_all(bind=engine)

# 数据库依赖
def get_db() -> Generator[Session, None, None]:
    db = None
    try:
        db = create_session()
        yield db
    except Exception as e:
        logger.error(f"Database connection failed: {str(e)}")
        raise
    finally:
        if db:
            db.close()

# 健康检查
def check_db_health() -> bool:
    try:
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        return True
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        return False

# 连接监控
def get_db_stats() -> dict:
    return {
        "pool_size": engine.pool.size(),
        "checked_out": engine.pool.checkedout(),
        "overflow": engine.pool.overflow(),
        "connections": engine.pool.status()
    }
