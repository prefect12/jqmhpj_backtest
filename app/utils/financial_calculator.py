"""
财务计算工具类
包含各种财务指标的计算方法
"""
import numpy as np
import pandas as pd
from typing import List, Dict, Tuple, Optional


class FinancialCalculator:
    """财务计算器"""
    
    def calculate_total_return(self, start_value: float, end_value: float) -> float:
        """
        计算总收益率
        
        Args:
            start_value: 起始价值
            end_value: 结束价值
        
        Returns:
            总收益率（百分比）
        """
        if start_value <= 0:
            return 0.0
        return ((end_value - start_value) / start_value) * 100
    
    def calculate_annualized_return(self, start_value: float, end_value: float, years: float) -> float:
        """
        计算年化收益率 (CAGR)
        
        Args:
            start_value: 起始价值
            end_value: 结束价值
            years: 年数
        
        Returns:
            年化收益率（百分比）
        """
        if start_value <= 0 or years <= 0:
            return 0.0
        
        return (((end_value / start_value) ** (1 / years)) - 1) * 100
    
    def calculate_volatility(self, returns: List[float], annualize: bool = True) -> float:
        """
        计算波动率（标准差）
        
        Args:
            returns: 收益率列表（日收益率或月收益率）
            annualize: 是否年化
        
        Returns:
            波动率（百分比）
        """
        if len(returns) < 2:
            return 0.0
        
        std_dev = np.std(returns, ddof=1)
        
        if annualize:
            # 假设252个交易日
            return std_dev * np.sqrt(252) * 100
        
        return std_dev * 100
    
    def calculate_max_drawdown(self, values: List[float]) -> Tuple[float, int, int]:
        """
        计算最大回撤
        
        Args:
            values: 净值列表
        
        Returns:
            (最大回撤百分比, 峰值索引, 谷值索引)
        """
        if len(values) < 2:
            return (0.0, 0, 0)
        
        peak = values[0]
        peak_idx = 0
        max_dd = 0.0
        max_dd_peak_idx = 0
        max_dd_trough_idx = 0
        
        for i, value in enumerate(values):
            if value > peak:
                peak = value
                peak_idx = i
            
            drawdown = ((peak - value) / peak) * 100 if peak > 0 else 0
            
            if drawdown > max_dd:
                max_dd = drawdown
                max_dd_peak_idx = peak_idx
                max_dd_trough_idx = i
        
        return (-max_dd, max_dd_peak_idx, max_dd_trough_idx)
    
    def calculate_sharpe_ratio(self, returns: List[float], risk_free_rate: float = 0.0) -> float:
        """
        计算夏普比率
        
        Args:
            returns: 收益率列表
            risk_free_rate: 无风险利率（年化）
        
        Returns:
            夏普比率
        """
        if len(returns) < 2:
            return 0.0
        
        # 计算超额收益
        excess_returns = [r - risk_free_rate/252 for r in returns]  # 假设日收益率
        
        mean_excess_return = np.mean(excess_returns)
        std_excess_return = np.std(excess_returns, ddof=1)
        
        if std_excess_return == 0:
            return 0.0
        
        # 年化夏普比率
        return (mean_excess_return / std_excess_return) * np.sqrt(252)
    
    def calculate_sortino_ratio(self, returns: List[float], risk_free_rate: float = 0.0, target_return: float = 0.0) -> float:
        """
        计算索提诺比率
        
        Args:
            returns: 收益率列表
            risk_free_rate: 无风险利率
            target_return: 目标收益率
        
        Returns:
            索提诺比率
        """
        if len(returns) < 2:
            return 0.0
        
        excess_returns = [r - risk_free_rate/252 for r in returns]
        mean_excess_return = np.mean(excess_returns)
        
        # 计算下行标准差
        downside_returns = [min(0, r - target_return/252) for r in returns]
        downside_std = np.sqrt(np.mean([r**2 for r in downside_returns]))
        
        if downside_std == 0:
            return 0.0
        
        return (mean_excess_return / downside_std) * np.sqrt(252)
    
    def calculate_portfolio_values(self, stock_data: Dict[str, List[Dict]], weights: Dict[str, float], 
                                 initial_amount: float) -> List[Dict]:
        """
        计算投资组合净值序列
        
        Args:
            stock_data: 股票数据字典 {symbol: [{'Date': ..., 'Close': ...}, ...]}
            weights: 权重字典 {symbol: weight}
            initial_amount: 初始投资金额
        
        Returns:
            净值序列 [{'date': ..., 'value': ..., 'return': ...}, ...]
        """
        # 确保所有股票有相同的日期
        dates = set()
        for symbol, data in stock_data.items():
            for row in data:
                dates.add(row['Date'])
        
        dates = sorted(list(dates))
        
        # 构建价格矩阵
        price_matrix = {}
        for date in dates:
            price_matrix[date] = {}
            for symbol in stock_data:
                # 找到该日期的价格
                for row in stock_data[symbol]:
                    if row['Date'] == date:
                        price_matrix[date][symbol] = row['Close']
                        break
        
        # 计算初始持仓
        if not dates:
            return []
        
        initial_prices = price_matrix[dates[0]]
        shares = {}
        for symbol, weight in weights.items():
            if symbol in initial_prices:
                investment = initial_amount * (weight / 100.0)
                shares[symbol] = investment / initial_prices[symbol]
        
        # 计算每日净值
        portfolio_values = []
        prev_value = initial_amount
        
        for date in dates:
            daily_prices = price_matrix[date]
            portfolio_value = 0.0
            
            for symbol, num_shares in shares.items():
                if symbol in daily_prices:
                    portfolio_value += num_shares * daily_prices[symbol]
            
            daily_return = ((portfolio_value - prev_value) / prev_value * 100) if prev_value > 0 else 0
            
            portfolio_values.append({
                'date': date,
                'value': portfolio_value,
                'daily_return': daily_return,
                'cumulative_return': ((portfolio_value - initial_amount) / initial_amount * 100)
            })
            
            prev_value = portfolio_value
        
        return portfolio_values
    
    def calculate_annual_returns(self, portfolio_values: List[Dict]) -> List[Dict]:
        """
        计算年度收益
        
        Args:
            portfolio_values: 投资组合净值序列
        
        Returns:
            年度收益列表
        """
        if not portfolio_values:
            return []
        
        # 按年分组
        df = pd.DataFrame(portfolio_values)
        df['date'] = pd.to_datetime(df['date'])
        df['year'] = df['date'].dt.year
        
        annual_returns = []
        
        for year in df['year'].unique():
            year_data = df[df['year'] == year]
            
            if len(year_data) > 0:
                start_value = year_data.iloc[0]['value']
                end_value = year_data.iloc[-1]['value']
                annual_return = self.calculate_total_return(start_value, end_value)
                
                # 计算年内波动率
                daily_returns = year_data['daily_return'].values
                volatility = np.std(daily_returns) * np.sqrt(252)
                
                annual_returns.append({
                    'year': int(year),
                    'start_value': start_value,
                    'end_value': end_value,
                    'annual_return': annual_return,
                    'volatility': volatility
                })
        
        return annual_returns
    
    def calculate_risk_metrics(self, portfolio_values: List[Dict]) -> Dict:
        """
        计算风险指标汇总
        
        Args:
            portfolio_values: 投资组合净值序列
        
        Returns:
            风险指标字典
        """
        if not portfolio_values:
            return {}
        
        values = [pv['value'] for pv in portfolio_values]
        returns = [pv['daily_return'] for pv in portfolio_values[1:]]  # 跳过第一天
        
        start_value = values[0]
        end_value = values[-1]
        
        # 计算交易天数和年数
        trading_days = len(values)
        years = trading_days / 252
        
        # 计算各项指标
        total_return = self.calculate_total_return(start_value, end_value)
        annualized_return = self.calculate_annualized_return(start_value, end_value, years)
        volatility = self.calculate_volatility(returns)
        max_drawdown, peak_idx, trough_idx = self.calculate_max_drawdown(values)
        sharpe_ratio = self.calculate_sharpe_ratio(returns)
        sortino_ratio = self.calculate_sortino_ratio(returns)
        
        # 计算正收益率
        positive_days = sum(1 for r in returns if r > 0)
        positive_rate = (positive_days / len(returns) * 100) if returns else 0
        
        return {
            'total_return': total_return,
            'annualized_return': annualized_return,
            'volatility': volatility,
            'max_drawdown': max_drawdown,
            'sharpe_ratio': sharpe_ratio,
            'sortino_ratio': sortino_ratio,
            'positive_days': positive_days,
            'total_days': len(returns),
            'positive_rate': positive_rate,
            'max_drawdown_peak_date': portfolio_values[peak_idx]['date'] if peak_idx < len(portfolio_values) else None,
            'max_drawdown_trough_date': portfolio_values[trough_idx]['date'] if trough_idx < len(portfolio_values) else None
        }