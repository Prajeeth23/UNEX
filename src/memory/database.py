from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Float
from sqlalchemy.orm import declarative_base, sessionmaker
import datetime
import os

Base = declarative_base()

import json

class MemoryDB(Base):
    __tablename__ = 'memories'
    id = Column(String, primary_key=True, index=True)
    type = Column(String, index=True)
    content = Column(Text)
    importance = Column(String, default="MEDIUM")
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))
    last_accessed = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))
    tags = Column(Text) # JSON serialized list of strings

class MemoryEmbeddingDB(Base):
    __tablename__ = 'memory_embeddings'
    memory_id = Column(String, primary_key=True, index=True)
    embedding_vector = Column(Text) # JSON serialized numpy array

class MemoryAccessLogDB(Base):
    __tablename__ = 'memory_access_logs'
    id = Column(Integer, primary_key=True, autoincrement=True)
    memory_id = Column(String, index=True)
    accessed_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))
    context = Column(Text, nullable=True)

class AuditLogDB(Base):
    __tablename__ = 'audit_logs'
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))
    tool_name = Column(String, index=True)
    tool_args = Column(Text) # JSON serialized
    risk_level = Column(String)
    status = Column(String)
    user_query = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)

def init_db(db_path: str = "database/unex.db"):
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    engine = create_engine(f"sqlite:///{db_path}")
    Base.metadata.create_all(bind=engine)
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)
