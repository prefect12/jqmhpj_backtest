"""
定投服务层
处理定期定投和条件定投的业务逻辑
"""
import uuid
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from app.dao.stock_data_dao import StockDataDAO
from app.utils.financial_calculator import FinancialCalculator
from app.utils.technical_indicators import TechnicalIndicators
from app.core.config import settings


class DCAService:
    """定投服务"""
    
    def __init__(self):
        self.stock_dao = StockDataDAO()
        self.calculator = FinancialCalculator()
        self.indicators = TechnicalIndicators()
    
    def run_periodic_dca(self, dca_config: Dict) -> Dict:
        """
        执行定期定投回测
        
        Args:
            dca_config: 定投配置
                {
                    'assets': [{'symbol': 'AAPL', 'weight': 40.0}, ...],
                    'start_date': '2020-01-01',
                    'end_date': '2024-12-31',
                    'initial_amount': 10000.0,
                    'investment_amount': 1000.0,  # 每次投入金额
                    'frequency': 'monthly',  # monthly/weekly/biweekly
                    'frequency_config': {
                        'day_of_month': 1  # 每月第几天
                    }
                }
        
        Returns:
            定投回测结果
        """
        try:
            # 1. 获取股票数据
            symbols = [asset['symbol'] for asset in dca_config['assets']]
            stock_data = self.stock_dao.get_multiple_stocks_data(
                symbols,
                dca_config['start_date'],
                dca_config['end_date']
            )
            
            # 检查是否有有效数据
            if not stock_data or all(not data for data in stock_data.values()):
                raise ValueError("No valid stock data retrieved")
            
            # 2. 生成投资日期列表
            investment_dates = self._generate_investment_dates(
                dca_config['start_date'],
                dca_config['end_date'],
                dca_config['frequency'],
                dca_config.get('frequency_config', {})
            )
            
            # 3. 执行定投计算
            results = self._calculate_dca_returns(
                stock_data,
                dca_config['assets'],
                dca_config['initial_amount'],
                dca_config['investment_amount'],
                investment_dates
            )
            
            # 4. 计算统计指标
            metrics = self._calculate_dca_metrics(results)
            
            # 5. 构建返回结果
            return {
                'dca_id': f"dca_{uuid.uuid4().hex[:12]}",
                'status': 'completed',
                'config_summary': {
                    'start_date': dca_config['start_date'],
                    'end_date': dca_config['end_date'],
                    'initial_amount': dca_config['initial_amount'],
                    'investment_amount': dca_config['investment_amount'],
                    'frequency': dca_config['frequency'],
                    'total_investments': len(investment_dates)
                },
                'performance': metrics,
                'investment_schedule': investment_dates[:20],  # 前20次投资
                'time_series': results['time_series'][:100],  # 限制返回数据量
                'created_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                'dca_id': f"dca_{uuid.uuid4().hex[:12]}",
                'status': 'failed',
                'error': str(e),
                'created_at': datetime.utcnow().isoformat()
            }
    
    def run_conditional_dca(self, dca_config: Dict) -> Dict:
        """
        执行条件定投回测
        
        Args:
            dca_config: 条件定投配置
                {
                    'assets': [...],
                    'start_date': '2020-01-01',
                    'end_date': '2024-12-31',
                    'initial_amount': 10000.0,
                    'conditions': [
                        {
                            'type': 'price_drop',
                            'config': {
                                'drop_percentage': 3.0,
                                'amount': 2000.0,
                                'cooldown_days': 7
                            }
                        }
                    ]
                }
        
        Returns:
            条件定投回测结果
        """
        try:
            # 1. 获取股票数据
            symbols = [asset['symbol'] for asset in dca_config['assets']]
            stock_data = self.stock_dao.get_multiple_stocks_data(
                symbols,
                dca_config['start_date'],
                dca_config['end_date']
            )
            
            # 检查是否有有效数据
            if not stock_data or all(not data for data in stock_data.values()):
                raise ValueError("No valid stock data retrieved")
            
            # 2. 检测触发条件
            triggers = self._detect_condition_triggers(
                stock_data,
                dca_config['conditions'],
                dca_config['start_date'],
                dca_config['end_date']
            )
            
            # 3. 执行条件定投计算
            results = self._calculate_conditional_dca_returns(
                stock_data,
                dca_config['assets'],
                dca_config['initial_amount'],
                triggers
            )
            
            # 4. 计算统计指标
            metrics = self._calculate_dca_metrics(results)
            
            # 5. 构建返回结果
            return {
                'dca_id': f"dca_cond_{uuid.uuid4().hex[:12]}",
                'status': 'completed',
                'config_summary': {
                    'start_date': dca_config['start_date'],
                    'end_date': dca_config['end_date'],
                    'initial_amount': dca_config['initial_amount'],
                    'condition_count': len(dca_config['conditions']),
                    'total_triggers': len(triggers)
                },
                'performance': metrics,
                'triggers': triggers[:20],  # 前20次触发
                'time_series': results['time_series'][:100],
                'created_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                'dca_id': f"dca_cond_{uuid.uuid4().hex[:12]}",
                'status': 'failed',
                'error': str(e),
                'created_at': datetime.utcnow().isoformat()
            }
    
    def _generate_investment_dates(self, start_date: str, end_date: str, 
                                  frequency: str, config: Dict) -> List[str]:
        """生成投资日期列表"""
        dates = []
        current = pd.to_datetime(start_date)
        end = pd.to_datetime(end_date)
        
        if frequency == 'monthly':
            day_of_month = config.get('day_of_month', 1)
            while current <= end:
                # 设置为每月特定日期
                investment_date = current.replace(day=min(day_of_month, 
                                                         current.days_in_month))
                if investment_date >= pd.to_datetime(start_date) and investment_date <= end:
                    dates.append(investment_date.strftime('%Y-%m-%d'))
                current = current + pd.DateOffset(months=1)
                
        elif frequency == 'weekly':
            while current <= end:
                dates.append(current.strftime('%Y-%m-%d'))
                current = current + pd.DateOffset(weeks=1)
                
        elif frequency == 'biweekly':
            while current <= end:
                dates.append(current.strftime('%Y-%m-%d'))
                current = current + pd.DateOffset(weeks=2)
                
        elif frequency == 'daily':
            while current <= end:
                # 只在交易日投资
                if current.weekday() < 5:  # 周一到周五
                    dates.append(current.strftime('%Y-%m-%d'))
                current = current + pd.DateOffset(days=1)
        
        return dates
    
    def _calculate_dca_returns(self, stock_data: Dict, assets: List[Dict], 
                              initial_amount: float, investment_amount: float,
                              investment_dates: List[str]) -> Dict:
        """计算定投收益"""
        # 初始化持仓
        shares = {asset['symbol']: 0 for asset in assets}
        weights = {asset['symbol']: asset['weight'] / 100.0 for asset in assets}
        
        total_invested = initial_amount
        results = []
        
        # 获取所有日期的价格数据
        all_dates = set()
        for symbol, data in stock_data.items():
            for row in data:
                all_dates.add(row['Date'])
        all_dates = sorted(list(all_dates))
        
        # 构建价格字典
        price_dict = {}
        for date in all_dates:
            price_dict[date] = {}
            for symbol, data in stock_data.items():
                for row in data:
                    if row['Date'] == date:
                        price_dict[date][symbol] = row['Close']
                        break
        
        # 初始投资
        if initial_amount > 0 and all_dates:
            first_date = all_dates[0]
            for symbol, weight in weights.items():
                if symbol in price_dict[first_date]:
                    investment = initial_amount * weight
                    shares[symbol] = investment / price_dict[first_date][symbol]
        
        # 执行定投
        for date in all_dates:
            # 检查是否是投资日
            if date in investment_dates:
                # 按权重买入
                for symbol, weight in weights.items():
                    if symbol in price_dict[date]:
                        investment = investment_amount * weight
                        shares[symbol] += investment / price_dict[date][symbol]
                total_invested += investment_amount
            
            # 计算当前组合价值
            portfolio_value = 0
            for symbol, num_shares in shares.items():
                if symbol in price_dict[date]:
                    portfolio_value += num_shares * price_dict[date][symbol]
            
            results.append({
                'date': date,
                'invested': total_invested,
                'value': portfolio_value,
                'return_pct': ((portfolio_value - total_invested) / total_invested * 100) 
                            if total_invested > 0 else 0
            })
        
        return {
            'time_series': results,
            'final_shares': shares,
            'total_invested': total_invested
        }
    
    def _detect_condition_triggers(self, stock_data: Dict, conditions: List[Dict],
                                  start_date: str, end_date: str) -> List[Dict]:
        """检测条件触发"""
        triggers = []
        
        # 计算组合整体表现
        portfolio_prices = self._calculate_portfolio_prices(stock_data)
        
        for i in range(1, len(portfolio_prices)):
            date = portfolio_prices[i]['date']
            current_price = portfolio_prices[i]['price']
            prev_price = portfolio_prices[i-1]['price']
            
            for condition in conditions:
                if condition['type'] == 'price_drop':
                    drop_pct = (prev_price - current_price) / prev_price * 100
                    threshold = condition['config']['drop_percentage']
                    
                    if drop_pct >= threshold:
                        # 检查冷却期
                        cooldown = condition['config'].get('cooldown_days', 0)
                        if not triggers or self._check_cooldown(date, triggers[-1]['date'], cooldown):
                            triggers.append({
                                'date': date,
                                'type': 'price_drop',
                                'trigger_value': drop_pct,
                                'threshold': threshold,
                                'amount': condition['config']['amount']
                            })
                
                elif condition['type'] == 'drawdown':
                    # 计算回撤
                    lookback = condition['config'].get('lookback_days', 252)
                    max_price = self._get_max_price(portfolio_prices, i, lookback)
                    drawdown = (max_price - current_price) / max_price * 100
                    threshold = condition['config']['drawdown_threshold']
                    
                    if drawdown >= threshold:
                        if not triggers or self._check_cooldown(date, triggers[-1]['date'], 7):
                            triggers.append({
                                'date': date,
                                'type': 'drawdown',
                                'trigger_value': drawdown,
                                'threshold': threshold,
                                'amount': condition['config'].get('amount', 1000)
                            })
        
        return triggers
    
    def _calculate_conditional_dca_returns(self, stock_data: Dict, assets: List[Dict],
                                          initial_amount: float, triggers: List[Dict]) -> Dict:
        """计算条件定投收益"""
        # 初始化持仓
        shares = {asset['symbol']: 0 for asset in assets}
        weights = {asset['symbol']: asset['weight'] / 100.0 for asset in assets}
        
        total_invested = initial_amount
        results = []
        
        # 获取所有日期的价格数据
        all_dates = set()
        for symbol, data in stock_data.items():
            for row in data:
                all_dates.add(row['Date'])
        all_dates = sorted(list(all_dates))
        
        # 构建价格字典
        price_dict = {}
        for date in all_dates:
            price_dict[date] = {}
            for symbol, data in stock_data.items():
                for row in data:
                    if row['Date'] == date:
                        price_dict[date][symbol] = row['Close']
                        break
        
        # 初始投资
        if initial_amount > 0 and all_dates:
            first_date = all_dates[0]
            for symbol, weight in weights.items():
                if symbol in price_dict[first_date]:
                    investment = initial_amount * weight
                    shares[symbol] = investment / price_dict[first_date][symbol]
        
        # 将触发器转换为日期字典
        trigger_dict = {t['date']: t for t in triggers}
        
        # 执行条件定投
        for date in all_dates:
            # 检查是否触发条件
            if date in trigger_dict:
                trigger = trigger_dict[date]
                investment_amount = trigger['amount']
                
                # 按权重买入
                for symbol, weight in weights.items():
                    if symbol in price_dict[date]:
                        investment = investment_amount * weight
                        shares[symbol] += investment / price_dict[date][symbol]
                total_invested += investment_amount
            
            # 计算当前组合价值
            portfolio_value = 0
            for symbol, num_shares in shares.items():
                if symbol in price_dict[date]:
                    portfolio_value += num_shares * price_dict[date][symbol]
            
            results.append({
                'date': date,
                'invested': total_invested,
                'value': portfolio_value,
                'return_pct': ((portfolio_value - total_invested) / total_invested * 100) 
                            if total_invested > 0 else 0,
                'triggered': date in trigger_dict
            })
        
        return {
            'time_series': results,
            'final_shares': shares,
            'total_invested': total_invested
        }
    
    def _calculate_portfolio_prices(self, stock_data: Dict) -> List[Dict]:
        """计算投资组合加权价格序列"""
        # 简化处理：等权重计算
        all_dates = set()
        for symbol, data in stock_data.items():
            for row in data:
                all_dates.add(row['Date'])
        all_dates = sorted(list(all_dates))
        
        portfolio_prices = []
        for date in all_dates:
            total_price = 0
            count = 0
            for symbol, data in stock_data.items():
                for row in data:
                    if row['Date'] == date:
                        total_price += row['Close']
                        count += 1
                        break
            if count > 0:
                portfolio_prices.append({
                    'date': date,
                    'price': total_price / count
                })
        
        return portfolio_prices
    
    def _check_cooldown(self, current_date: str, last_trigger_date: str, cooldown_days: int) -> bool:
        """检查冷却期"""
        current = pd.to_datetime(current_date)
        last = pd.to_datetime(last_trigger_date)
        return (current - last).days >= cooldown_days
    
    def _get_max_price(self, prices: List[Dict], current_idx: int, lookback_days: int) -> float:
        """获取回看期内的最高价格"""
        start_idx = max(0, current_idx - lookback_days)
        max_price = 0
        for i in range(start_idx, current_idx + 1):
            if prices[i]['price'] > max_price:
                max_price = prices[i]['price']
        return max_price
    
    def _calculate_dca_metrics(self, results: Dict) -> Dict:
        """计算定投统计指标"""
        time_series = results['time_series']
        if not time_series:
            return {}
        
        total_invested = results['total_invested']
        final_value = time_series[-1]['value']
        
        # 计算IRR (简化版本)
        cash_flows = [-total_invested]  # 初始投资为负
        cash_flows.append(final_value)  # 最终价值为正
        
        # 计算各项指标
        return {
            'total_invested': total_invested,
            'final_value': final_value,
            'total_return': final_value - total_invested,
            'total_return_pct': ((final_value - total_invested) / total_invested * 100) 
                              if total_invested > 0 else 0,
            'average_cost': total_invested / len(time_series) if time_series else 0,
            'investment_count': len([t for t in time_series if t.get('triggered', False)]) 
                              if 'triggered' in time_series[0] else len(results.get('investment_schedule', [])),
            'best_return': max([t['return_pct'] for t in time_series]),
            'worst_return': min([t['return_pct'] for t in time_series]),
            'current_return': time_series[-1]['return_pct']
        }