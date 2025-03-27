from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(128))
    created_at = Column(DateTime, default=datetime.utcnow)
    trial_count = Column(Integer, default=10)
    trial_seconds = Column(Integer, default=60)  # 总共60秒试用时长


class Subscription(Base):
    __tablename__ = 'subscriptions'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    plan_type = Column(String(50))  # basic, pro, enterprise
    minutes = Column(Integer)  # 每月可用分钟数
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    is_active = Column(Boolean, default=True)


class Payment(Base):
    __tablename__ = 'payments'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    amount = Column(Float)
    currency = Column(String(10))  # CNY, USD, etc
    payment_method = Column(String(20))  # wechat, alipay, stripe
    status = Column(String(20))
    created_at = Column(DateTime, default=datetime.utcnow)