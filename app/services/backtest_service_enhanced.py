"""
增强版回测服务 - 包含交易记录
"""
import uuid
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import pandas as pd
import numpy as np

from app.dao.stock_data_dao import StockDataDAO
from app.utils.financial_calculator import FinancialCalculator
from app.utils.technical_indicators import TechnicalIndicators
from app.services.rebalancing_service import RebalancingService
from app.models.transaction import Transaction, TransactionType, BuyReason, TransactionAnalyzer
from app.core.config import settings


class EnhancedBacktestService:
    """增强版回测服务 - 支持交易记录和买入信号分析"""
    
    def __init__(self):
        self.stock_dao = StockDataDAO()
        self.calculator = FinancialCalculator()
        self.rebalancing_service = RebalancingService()
        self.transaction_analyzer = TransactionAnalyzer()
        self.transactions = []
    
    def run_backtest_with_transactions(self, portfolio_config: Dict) -> Dict:
        """
        执行带交易记录的回测
        
        Args:
            portfolio_config: 投资组合配置，包含买入条件设置
                {
                    'assets': [{'symbol': 'AAPL', 'weight': 40.0}, ...],
                    'start_date': '2020-01-01',
                    'end_date': '2020-12-31',
                    'initial_amount': 10000.0,
                    'buy_conditions': {
                        'daily_drop_threshold': -0.05,  # 日跌幅阈值
                        'drawdown_threshold': -0.10,    # 回撤阈值
                        'vix_threshold': 30,             # VIX阈值
                        'rsi_oversold': 30,              # RSI超卖阈值
                        'enable_macd': True,             # 启用MACD金叉
                        'enable_support': True           # 启用支撑位
                    }
                }
        """
        try:
            self.transactions = []  # 清空交易记录
            
            # 1. 验证配置
            self._validate_config(portfolio_config)
            
            # 2. 获取股票数据
            symbols = [asset['symbol'] for asset in portfolio_config['assets']]
            
            # 使用现有的get_multiple_stocks_dataframes方法
            stock_dataframes_raw = self.stock_dao.get_multiple_stocks_dataframes(
                symbols,
                portfolio_config['start_date'],
                portfolio_config['end_date']
            )
            
            # 计算技术指标
            stock_dataframes = {}
            for symbol, df in stock_dataframes_raw.items():
                if df is not None and not df.empty:
                    df = self._calculate_indicators(df)
                    stock_dataframes[symbol] = df
            
            # 3. 模拟交易过程
            portfolio_values = self._simulate_trading(
                stock_dataframes,
                portfolio_config
            )
            
            # 4. 计算风险收益指标
            risk_metrics = self.calculator.calculate_risk_metrics(portfolio_values)
            
            # 5. 计算年度收益
            annual_returns = self.calculator.calculate_annual_returns(portfolio_values)
            
            # 6. 分析交易记录
            transaction_analysis = self.transaction_analyzer.analyze_transactions(self.transactions)
            
            # 7. 构建返回结果
            backtest_id = f"bt_{uuid.uuid4().hex[:12]}"
            
            result = {
                'backtest_id': backtest_id,
                'status': 'completed',
                'config_summary': {
                    'start_date': portfolio_config['start_date'],
                    'end_date': portfolio_config['end_date'],
                    'initial_amount': portfolio_config['initial_amount'],
                    'asset_count': len(portfolio_config['assets']),
                    'buy_conditions': portfolio_config.get('buy_conditions', {})
                },
                'performance_summary': {
                    'start_value': portfolio_config['initial_amount'],
                    'end_value': portfolio_values[-1]['value'] if portfolio_values else 0,
                    'total_return_pct': risk_metrics.get('total_return', 0),
                    'annualized_return_pct': risk_metrics.get('annualized_return', 0)
                },
                'risk_metrics': {
                    'volatility_annual_pct': risk_metrics.get('volatility', 0),
                    'max_drawdown_pct': risk_metrics.get('max_drawdown', 0),
                    'sharpe_ratio': risk_metrics.get('sharpe_ratio', 0),
                    'sortino_ratio': risk_metrics.get('sortino_ratio', 0)
                },
                'transaction_summary': transaction_analysis,
                'transactions': [t.to_dict() for t in self.transactions],
                'portfolio_values': portfolio_values,
                'annual_returns': annual_returns,
                'created_at': datetime.utcnow().isoformat()
            }
            
            return result
            
        except Exception as e:
            return {
                'backtest_id': f"bt_{uuid.uuid4().hex[:12]}",
                'status': 'failed',
                'error': str(e),
                'created_at': datetime.utcnow().isoformat()
            }
    
    def _calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """计算技术指标"""
        # RSI
        df['RSI'] = TechnicalIndicators.calculate_rsi(df['Close'])
        
        # MACD
        macd_result = TechnicalIndicators.calculate_macd(df['Close'])
        df['MACD'] = macd_result['macd']
        df['MACD_Signal'] = macd_result['signal']
        df['MACD_Histogram'] = macd_result['histogram']
        
        # Bollinger Bands
        bb_result = TechnicalIndicators.calculate_bollinger_bands(df['Close'])
        df['BB_Upper'] = bb_result['upper']
        df['BB_Middle'] = bb_result['middle']
        df['BB_Lower'] = bb_result['lower']
        
        # 支撑位和阻力位
        df['Support'] = df['Low'].rolling(window=20).min()
        df['Resistance'] = df['High'].rolling(window=20).max()
        
        # 日收益率
        df['Daily_Return'] = df['Close'].pct_change()
        
        # 回撤
        df['Peak'] = df['Close'].cummax()
        df['Drawdown'] = (df['Close'] - df['Peak']) / df['Peak']
        
        return df
    
    def _simulate_trading(
        self,
        stock_dataframes: Dict[str, pd.DataFrame],
        portfolio_config: Dict
    ) -> List[Dict]:
        """模拟交易过程"""
        initial_amount = portfolio_config['initial_amount']
        weights = {
            asset['symbol']: asset['weight'] / 100.0
            for asset in portfolio_config['assets']
        }
        buy_conditions = portfolio_config.get('buy_conditions', {})
        
        # 获取所有交易日期
        all_dates = set()
        for df in stock_dataframes.values():
            all_dates.update(df.index)
        all_dates = sorted(all_dates)
        
        # 初始化投资组合
        cash = initial_amount
        holdings = {symbol: 0 for symbol in stock_dataframes.keys()}
        portfolio_values = []
        
        # 初始买入
        first_date = all_dates[0]
        for symbol, weight in weights.items():
            if symbol in stock_dataframes:
                df = stock_dataframes[symbol]
                if first_date in df.index:
                    price = df.loc[first_date, 'Close']
                    amount_to_invest = initial_amount * weight
                    shares = amount_to_invest / price
                    holdings[symbol] = shares
                    cash -= amount_to_invest
                    
                    # 记录初始买入
                    self._record_transaction(
                        date=first_date,
                        symbol=symbol,
                        transaction_type=TransactionType.BUY,
                        shares=shares,
                        price=price,
                        amount=amount_to_invest,
                        reason="初始建仓",
                        reason_code=BuyReason.INITIAL,
                        details={'initial_weight': weight * 100},
                        portfolio_value_before=initial_amount,
                        portfolio_value_after=initial_amount  # 第一天不变
                    )
        
        # 遍历每个交易日
        for date in all_dates:
            # 计算当前投资组合价值
            portfolio_value = cash
            for symbol, shares in holdings.items():
                if symbol in stock_dataframes and date in stock_dataframes[symbol].index:
                    price = stock_dataframes[symbol].loc[date, 'Close']
                    portfolio_value += shares * price
            
            # 检查每个资产的买入信号
            for symbol in stock_dataframes.keys():
                if date in stock_dataframes[symbol].index:
                    df = stock_dataframes[symbol]
                    current_row = df.loc[date]
                    
                    # 准备指标数据
                    indicators = {
                        'rsi': current_row.get('RSI', 50),
                        'macd': current_row.get('MACD', 0),
                        'macd_signal': current_row.get('MACD_Signal', 0),
                        'support_level': current_row.get('Support', 0),
                        'drawdown': current_row.get('Drawdown', 0)
                    }
                    
                    # 获取历史价格
                    price_history = df['Close'][:date].values.tolist()
                    
                    # 检查买入信号
                    should_buy, reason, reason_code, details = self.transaction_analyzer.check_buy_signals(
                        current_row['Close'],
                        price_history,
                        indicators,
                        buy_conditions
                    )
                    
                    # 如果触发买入信号且有现金
                    if should_buy and cash > 100:  # 至少100美元才买入
                        # 计算买入金额（使用剩余现金的一部分）
                        buy_amount = min(cash * 0.2, cash)  # 每次最多使用20%的现金
                        shares_to_buy = buy_amount / current_row['Close']
                        
                        # 更新持仓和现金
                        holdings[symbol] += shares_to_buy
                        cash -= buy_amount
                        
                        # 记录交易
                        self._record_transaction(
                            date=date,
                            symbol=symbol,
                            transaction_type=TransactionType.BUY,
                            shares=shares_to_buy,
                            price=current_row['Close'],
                            amount=buy_amount,
                            reason=reason,
                            reason_code=reason_code,
                            details=details,
                            portfolio_value_before=portfolio_value,
                            portfolio_value_after=portfolio_value  # 买入后立即更新
                        )
            
            # 记录每日投资组合价值
            portfolio_values.append({
                'date': date.strftime('%Y-%m-%d'),
                'value': portfolio_value,
                'cash': cash,
                'holdings_value': portfolio_value - cash
            })
        
        return portfolio_values
    
    def _record_transaction(self, **kwargs):
        """记录交易"""
        transaction = Transaction(
            date=kwargs['date'],
            symbol=kwargs['symbol'],
            transaction_type=kwargs['transaction_type'],
            shares=kwargs['shares'],
            price=kwargs['price'],
            amount=kwargs['amount'],
            reason=kwargs['reason'],
            reason_code=kwargs['reason_code'],
            details=kwargs['details'],
            portfolio_value_before=kwargs['portfolio_value_before'],
            portfolio_value_after=kwargs['portfolio_value_after']
        )
        self.transactions.append(transaction)
    
    def _validate_config(self, config: Dict):
        """验证配置"""
        required_fields = ['assets', 'start_date', 'end_date', 'initial_amount']
        for field in required_fields:
            if field not in config:
                raise ValueError(f"Missing required field: {field}")
        
        if not config['assets']:
            raise ValueError("At least one asset is required")
        
        total_weight = sum(asset['weight'] for asset in config['assets'])
        if abs(total_weight - 100.0) > 0.01:
            raise ValueError(f"Weights must sum to 100%, got {total_weight}%")