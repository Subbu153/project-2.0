
from sqlalchemy import Column, Integer, String, Text, Date, DateTime
from sqlalchemy.sql import func
from database import Base

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    summary = Column(Text, nullable=True)
    status = Column(String(50), default="Todo")
    priority = Column(String(50), default="Medium")
    due_date = Column(Date, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class WeatherLog(Base):
    __tablename__ = "weather_logs"

    id = Column(Integer, primary_key=True, index=True)
    city = Column(String(100), nullable=False)
    temperature = Column(String(50), nullable=False)
    condition = Column(String(100), nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

