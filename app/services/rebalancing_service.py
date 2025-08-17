"""
再平衡服务
处理投资组合再平衡逻辑
"""
from typing import Dict, List
from datetime import datetime, timedelta
import pandas as pd
import numpy as np


class RebalancingService:
    """再平衡服务"""
    
    def apply_rebalancing(self, stock_data: Dict[str, pd.DataFrame], weights: Dict[str, float],
                          initial_amount: float, frequency: str) -> List[Dict]:
        """
        应用再平衡策略
        
        Args:
            stock_data: 股票价格数据
            weights: 目标权重
            initial_amount: 初始金额
            frequency: 再平衡频率 ('none', 'yearly', 'quarterly', 'monthly')
        
        Returns:
            包含再平衡后的投资组合价值序列
        """
        if frequency == 'none' or not frequency:
            return self._calculate_no_rebalance(stock_data, weights, initial_amount)
        elif frequency == 'yearly':
            return self._calculate_yearly_rebalance(stock_data, weights, initial_amount)
        elif frequency == 'quarterly':
            return self._calculate_quarterly_rebalance(stock_data, weights, initial_amount)
        elif frequency == 'monthly':
            return self._calculate_monthly_rebalance(stock_data, weights, initial_amount)
        else:
            return self._calculate_no_rebalance(stock_data, weights, initial_amount)
    
    def _calculate_no_rebalance(self, stock_data: Dict[str, pd.DataFrame], 
                                weights: Dict[str, float], initial_amount: float) -> List[Dict]:
        """不再平衡策略"""
        portfolio_values = []
        
        # 初始化每只股票的股数
        shares = {}
        first_date = None
        
        for symbol, data in stock_data.items():
            if data.empty:
                continue
            if first_date is None:
                first_date = data.index[0]
            initial_price = data.iloc[0]['Close']
            shares[symbol] = (initial_amount * weights[symbol] / 100) / initial_price
        
        # 计算每日组合价值
        date_sets = []
        for data in stock_data.values():
            if not data.empty:
                date_sets.append(set(data.index))
        
        if not date_sets:
            return []
        
        all_dates = sorted(set.union(*date_sets))
        
        for date in all_dates:
            portfolio_value = 0
            for symbol, data in stock_data.items():
                if date in data.index:
                    price = data.loc[date, 'Close']
                    portfolio_value += shares.get(symbol, 0) * price
            
            # 计算日收益率
            daily_return = 0
            if portfolio_values:
                prev_value = portfolio_values[-1]['value']
                if prev_value > 0:
                    daily_return = (portfolio_value - prev_value) / prev_value
            
            portfolio_values.append({
                'date': date.strftime('%Y-%m-%d'),
                'value': portfolio_value,
                'daily_return': daily_return
            })
        
        return portfolio_values
    
    def _calculate_yearly_rebalance(self, stock_data: Dict[str, pd.DataFrame],
                                   weights: Dict[str, float], initial_amount: float) -> List[Dict]:
        """年度再平衡策略"""
        return self._calculate_periodic_rebalance(stock_data, weights, initial_amount, 'yearly')
    
    def _calculate_quarterly_rebalance(self, stock_data: Dict[str, pd.DataFrame],
                                      weights: Dict[str, float], initial_amount: float) -> List[Dict]:
        """季度再平衡策略"""
        return self._calculate_periodic_rebalance(stock_data, weights, initial_amount, 'quarterly')
    
    def _calculate_monthly_rebalance(self, stock_data: Dict[str, pd.DataFrame],
                                    weights: Dict[str, float], initial_amount: float) -> List[Dict]:
        """月度再平衡策略"""
        return self._calculate_periodic_rebalance(stock_data, weights, initial_amount, 'monthly')
    
    def _calculate_periodic_rebalance(self, stock_data: Dict[str, pd.DataFrame],
                                     weights: Dict[str, float], initial_amount: float,
                                     frequency: str) -> List[Dict]:
        """周期性再平衡计算"""
        portfolio_values = []
        rebalance_history = []
        
        # 获取所有日期
        date_sets = []
        for symbol, data in stock_data.items():
            if not data.empty:
                date_sets.append(set(data.index))
        
        if not date_sets:
            return []
        
        all_dates = sorted(set.union(*date_sets))
        
        if not all_dates:
            return []
        
        # 初始化
        current_value = initial_amount
        shares = self._initialize_shares(stock_data, weights, initial_amount)
        last_rebalance_date = all_dates[0]
        
        for date in all_dates:
            # 计算当前组合价值
            portfolio_value = 0
            for symbol, data in stock_data.items():
                if date in data.index:
                    price = data.loc[date, 'Close']
                    portfolio_value += shares.get(symbol, 0) * price
            
            # 检查是否需要再平衡
            if self._should_rebalance(date, last_rebalance_date, frequency):
                # 执行再平衡
                shares = self._rebalance_portfolio(stock_data, weights, portfolio_value, date)
                last_rebalance_date = date
                rebalance_history.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'value_before': portfolio_value,
                    'action': 'rebalanced'
                })
            
            # 计算日收益率
            daily_return = 0
            if portfolio_values:
                prev_value = portfolio_values[-1]['value']
                if prev_value > 0:
                    daily_return = (portfolio_value - prev_value) / prev_value
            
            portfolio_values.append({
                'date': date.strftime('%Y-%m-%d'),
                'value': portfolio_value,
                'daily_return': daily_return,
                'rebalanced': date == last_rebalance_date
            })
        
        return portfolio_values
    
    def _initialize_shares(self, stock_data: Dict[str, pd.DataFrame],
                          weights: Dict[str, float], initial_amount: float) -> Dict[str, float]:
        """初始化股票份额"""
        shares = {}
        for symbol, data in stock_data.items():
            if not data.empty:
                initial_price = data.iloc[0]['Close']
                shares[symbol] = (initial_amount * weights[symbol] / 100) / initial_price
        return shares
    
    def _should_rebalance(self, current_date, last_rebalance_date, frequency: str) -> bool:
        """判断是否应该再平衡"""
        if frequency == 'yearly':
            return current_date.year > last_rebalance_date.year
        elif frequency == 'quarterly':
            current_quarter = (current_date.month - 1) // 3
            last_quarter = (last_rebalance_date.month - 1) // 3
            return (current_date.year > last_rebalance_date.year or 
                   (current_date.year == last_rebalance_date.year and current_quarter > last_quarter))
        elif frequency == 'monthly':
            return (current_date.year > last_rebalance_date.year or
                   (current_date.year == last_rebalance_date.year and current_date.month > last_rebalance_date.month))
        return False
    
    def _rebalance_portfolio(self, stock_data: Dict[str, pd.DataFrame],
                           weights: Dict[str, float], total_value: float,
                           date) -> Dict[str, float]:
        """执行再平衡"""
        new_shares = {}
        for symbol, weight in weights.items():
            if symbol in stock_data and date in stock_data[symbol].index:
                current_price = stock_data[symbol].loc[date, 'Close']
                target_value = total_value * weight / 100
                new_shares[symbol] = target_value / current_price
        return new_shares
    
    def calculate_rebalancing_metrics(self, portfolio_values_with_rebalance: List[Dict],
                                     portfolio_values_without_rebalance: List[Dict]) -> Dict:
        """计算再平衡效果指标"""
        if not portfolio_values_with_rebalance or not portfolio_values_without_rebalance:
            return {}
        
        with_rb_final = portfolio_values_with_rebalance[-1]['value']
        without_rb_final = portfolio_values_without_rebalance[-1]['value']
        initial = portfolio_values_with_rebalance[0]['value']
        
        return {
            'with_rebalancing_return_pct': (with_rb_final / initial - 1) * 100,
            'without_rebalancing_return_pct': (without_rb_final / initial - 1) * 100,
            'rebalancing_benefit_pct': ((with_rb_final - without_rb_final) / without_rb_final) * 100,
            'rebalance_count': sum(1 for v in portfolio_values_with_rebalance if v.get('rebalanced', False))
        }