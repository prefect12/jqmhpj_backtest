"""
回测结果数据模型
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class BacktestConfig(Base):
    """回测配置模型"""
    __tablename__ = "backtest_configs"
    
    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(String(50), ForeignKey("portfolios.portfolio_id"), nullable=False)
    start_date = Column(String(10), nullable=False)  # YYYY-MM-DD
    end_date = Column(String(10), nullable=False)
    initial_amount = Column(Float, nullable=False)
    rebalance_frequency = Column(String(20), default="quarterly")  # none, monthly, quarterly, annually
    reinvest_dividends = Column(Integer, default=1)  # 0=False, 1=True
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "portfolio_id": self.portfolio_id,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "initial_amount": self.initial_amount,
            "rebalance_frequency": self.rebalance_frequency,
            "reinvest_dividends": bool(self.reinvest_dividends),
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class BacktestResult(Base):
    """回测结果模型"""
    __tablename__ = "backtest_results"
    
    id = Column(Integer, primary_key=True, index=True)
    backtest_id = Column(String(50), unique=True, index=True, nullable=False)
    portfolio_id = Column(String(50), ForeignKey("portfolios.portfolio_id"), nullable=False)
    config_id = Column(Integer, ForeignKey("backtest_configs.id"), nullable=False)
    
    # 配置摘要
    config_summary = Column(JSON, nullable=False)
    
    # 性能指标
    total_return = Column(Float)
    annualized_return = Column(Float)
    volatility = Column(Float)
    max_drawdown = Column(Float)
    sharpe_ratio = Column(Float)
    sortino_ratio = Column(Float)
    
    # 详细结果（JSON格式存储）
    performance_summary = Column(JSON)
    risk_metrics = Column(JSON)
    portfolio_decomposition = Column(JSON)
    annual_returns = Column(JSON)
    monthly_returns = Column(JSON)
    drawdown_periods = Column(JSON)
    time_series = Column(Text)  # 大数据，存储为压缩的JSON字符串
    
    # 状态和时间
    status = Column(String(20), default="processing")  # processing, completed, failed
    error_message = Column(Text)
    calculation_time_ms = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    
    def __repr__(self):
        return f"<BacktestResult(id={self.id}, backtest_id={self.backtest_id}, status={self.status})>"
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "backtest_id": self.backtest_id,
            "portfolio_id": self.portfolio_id,
            "config_id": self.config_id,
            "config_summary": self.config_summary,
            "total_return": self.total_return,
            "annualized_return": self.annualized_return,
            "volatility": self.volatility,
            "max_drawdown": self.max_drawdown,
            "sharpe_ratio": self.sharpe_ratio,
            "sortino_ratio": self.sortino_ratio,
            "performance_summary": self.performance_summary,
            "risk_metrics": self.risk_metrics,
            "portfolio_decomposition": self.portfolio_decomposition,
            "annual_returns": self.annual_returns,
            "monthly_returns": self.monthly_returns,
            "drawdown_periods": self.drawdown_periods,
            "status": self.status,
            "error_message": self.error_message,
            "calculation_time_ms": self.calculation_time_ms,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }