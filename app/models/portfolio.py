"""
投资组合数据模型
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON
from app.core.database import Base


class Portfolio(Base):
    """投资组合模型"""
    __tablename__ = "portfolios"
    
    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    assets = Column(JSON, nullable=False)  # 存储资产配置 [{"symbol": "AAPL", "weight": 0.3}, ...]
    total_weight = Column(Float, default=100.0)
    asset_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Portfolio(id={self.id}, name={self.name}, assets={self.asset_count})>"
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "portfolio_id": self.portfolio_id,
            "name": self.name,
            "assets": self.assets,
            "total_weight": self.total_weight,
            "asset_count": self.asset_count,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }