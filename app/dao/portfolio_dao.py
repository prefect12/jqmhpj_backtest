"""
投资组合数据访问对象
"""
from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.portfolio import Portfolio


class PortfolioDAO:
    """投资组合数据访问对象"""
    
    def __init__(self, db: Optional[Session] = None):
        self.db = db
        self.portfolios = {}  # 内存存储
        self.next_id = 1
    
    def create_portfolio(self, portfolio_data: dict) -> str:
        """创建投资组合"""
        # 简化版本，只使用内存存储
        portfolio_id = f"port_{self.next_id}"
        self.next_id += 1
        portfolio_data['portfolio_id'] = portfolio_id
        self.portfolios[portfolio_id] = portfolio_data
        return portfolio_id
    
    def get_portfolio(self, portfolio_id: str) -> Optional[dict]:
        """获取投资组合"""
        # 简化版本，只使用内存存储
        return self.portfolios.get(portfolio_id)
    
    def list_portfolios(self, limit: int = 10, offset: int = 0) -> List[dict]:
        """列出所有投资组合"""
        if self.db:
            return self.db.query(Portfolio).all()
        # 内存版本
        portfolios = list(self.portfolios.values())
        return portfolios[offset:offset + limit]
    
    def update_portfolio(self, portfolio_id: str, data: dict) -> bool:
        """更新投资组合"""
        if portfolio_id in self.portfolios:
            self.portfolios[portfolio_id].update(data)
            return True
        return False
    
    def delete_portfolio(self, portfolio_id: str) -> bool:
        """删除投资组合"""
        if portfolio_id in self.portfolios:
            del self.portfolios[portfolio_id]
            return True
        return False