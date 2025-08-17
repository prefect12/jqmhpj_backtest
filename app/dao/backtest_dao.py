"""
回测结果数据访问对象
"""
from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.backtest import BacktestResult, BacktestConfig


class BacktestDAO:
    """回测数据访问对象"""
    
    def __init__(self, db: Optional[Session] = None):
        self.db = db
        self.results_cache = {}  # 内存缓存
    
    def save_backtest_result(self, result_data: dict) -> BacktestResult:
        """保存回测结果"""
        result = BacktestResult(**result_data)
        if self.db:
            self.db.add(result)
            self.db.commit()
            self.db.refresh(result)
        return result
    
    def get_backtest_result(self, backtest_id: str) -> Optional[BacktestResult]:
        """获取回测结果"""
        if self.db:
            return self.db.query(BacktestResult).filter(BacktestResult.backtest_id == backtest_id).first()
        return None
    
    def save_backtest_config(self, config_data: dict) -> BacktestConfig:
        """保存回测配置"""
        config = BacktestConfig(**config_data)
        if self.db:
            self.db.add(config)
            self.db.commit()
            self.db.refresh(config)
        return config
    
    def get_backtest(self, backtest_id: str):
        """获取回测结果（内存版本）"""
        return self.results_cache.get(backtest_id)
    
    def get_backtest_history(self, limit: int = 10, offset: int = 0):
        """获取回测历史（内存版本）"""
        results = list(self.results_cache.values())
        return results[offset:offset + limit]