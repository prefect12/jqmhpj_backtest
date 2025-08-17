"""
回测服务层
处理回测业务逻辑
"""
import uuid
from typing import Dict, List
from datetime import datetime
from app.dao.stock_data_dao import StockDataDAO
from app.utils.financial_calculator import FinancialCalculator
from app.services.rebalancing_service import RebalancingService
from app.core.config import settings


class BacktestService:
    """回测服务"""
    
    def __init__(self):
        self.stock_dao = StockDataDAO()
        self.calculator = FinancialCalculator()
        self.rebalancing_service = RebalancingService()
    
    def run_backtest(self, portfolio_config: Dict) -> Dict:
        """
        执行回测
        
        Args:
            portfolio_config: 投资组合配置
                {
                    'assets': [{'symbol': 'AAPL', 'weight': 40.0}, ...],
                    'start_date': '2020-01-01',
                    'end_date': '2020-12-31',
                    'initial_amount': 10000.0,
                    'rebalance_frequency': 'quarterly',
                    'benchmark': 'SPY'  # 可选基准
                }
        
        Returns:
            回测结果字典
        """
        try:
            # 1. 验证配置
            self._validate_config(portfolio_config)
            
            # 2. 获取股票数据
            symbols = [asset['symbol'] for asset in portfolio_config['assets']]
            stock_data = self.stock_dao.get_multiple_stocks_data(
                symbols,
                portfolio_config['start_date'],
                portfolio_config['end_date']
            )
            
            # 3. 构建权重字典
            weights = {
                asset['symbol']: asset['weight'] 
                for asset in portfolio_config['assets']
            }
            
            # 4. 应用再平衡策略（如果指定）
            rebalance_frequency = portfolio_config.get('rebalance_frequency', 'none')
            if rebalance_frequency and rebalance_frequency != 'none':
                # 获取DataFrame格式的数据用于再平衡计算
                stock_dataframes = self.stock_dao.get_multiple_stocks_dataframes(
                    symbols,
                    portfolio_config['start_date'],
                    portfolio_config['end_date']
                )
                portfolio_values = self.rebalancing_service.apply_rebalancing(
                    stock_dataframes,
                    weights,
                    portfolio_config['initial_amount'],
                    rebalance_frequency
                )
            else:
                # 不再平衡，使用原有计算方法
                portfolio_values = self.calculator.calculate_portfolio_values(
                    stock_data,
                    weights,
                    portfolio_config['initial_amount']
                )
            
            # 5. 计算风险收益指标
            risk_metrics = self.calculator.calculate_risk_metrics(portfolio_values)
            
            # 6. 计算年度收益
            annual_returns = self.calculator.calculate_annual_returns(portfolio_values)
            
            # 7. 计算基准对比（如果指定）
            benchmark_comparison = None
            if 'benchmark' in portfolio_config and portfolio_config['benchmark']:
                benchmark_comparison = self._calculate_benchmark_comparison(
                    portfolio_config['benchmark'],
                    portfolio_config['start_date'],
                    portfolio_config['end_date'],
                    portfolio_config['initial_amount'],
                    portfolio_values
                )
            
            # 8. 构建返回结果
            backtest_id = f"bt_{uuid.uuid4().hex[:12]}"
            
            result = {
                'backtest_id': backtest_id,
                'status': 'completed',
                'config_summary': {
                    'start_date': portfolio_config['start_date'],
                    'end_date': portfolio_config['end_date'],
                    'initial_amount': portfolio_config['initial_amount'],
                    'asset_count': len(portfolio_config['assets']),
                    'benchmark': portfolio_config.get('benchmark')
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
                    'sortino_ratio': risk_metrics.get('sortino_ratio', 0),
                    'positive_rate_pct': risk_metrics.get('positive_rate', 0)
                },
                'portfolio_composition': portfolio_config['assets'],
                'annual_returns': annual_returns,
                'benchmark_comparison': benchmark_comparison,
                'time_series': portfolio_values[:100],  # 限制返回数据量
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
    
    def _validate_config(self, config: Dict):
        """验证配置"""
        # 验证必需字段
        required_fields = ['assets', 'start_date', 'end_date', 'initial_amount']
        for field in required_fields:
            if field not in config:
                raise ValueError(f"Missing required field: {field}")
        
        # 验证资产配置
        if not config['assets']:
            raise ValueError("At least one asset is required")
        
        if len(config['assets']) > settings.max_assets_count:
            raise ValueError(f"Maximum {settings.max_assets_count} assets allowed")
        
        # 验证权重总和
        total_weight = sum(asset['weight'] for asset in config['assets'])
        if abs(total_weight - 100.0) > 0.01:
            raise ValueError(f"Weights must sum to 100%, got {total_weight}%")
        
        # 验证初始金额
        if config['initial_amount'] < settings.min_initial_amount:
            raise ValueError(f"Minimum initial amount is ${settings.min_initial_amount}")
        
        if config['initial_amount'] > settings.max_initial_amount:
            raise ValueError(f"Maximum initial amount is ${settings.max_initial_amount}")
    
    def _calculate_benchmark_comparison(self, benchmark_symbol: str, start_date: str, 
                                       end_date: str, initial_amount: float, 
                                       portfolio_values: List[Dict]) -> Dict:
        """计算基准对比"""
        try:
            # 获取基准数据
            benchmark_data = self.stock_dao.get_stock_data(benchmark_symbol, start_date, end_date)
            
            if benchmark_data.empty:
                return None
            
            # 计算基准净值
            benchmark_values = []
            initial_price = benchmark_data.iloc[0]['Close']
            shares = initial_amount / initial_price
            
            for _, row in benchmark_data.iterrows():
                benchmark_values.append({
                    'date': row.name.strftime('%Y-%m-%d'),
                    'value': row['Close'] * shares
                })
            
            # 计算基准指标
            benchmark_metrics = self.calculator.calculate_risk_metrics(benchmark_values)
            
            # 计算相对表现
            portfolio_return = portfolio_values[-1]['value'] / initial_amount - 1
            benchmark_return = benchmark_values[-1]['value'] / initial_amount - 1
            
            return {
                'benchmark_symbol': benchmark_symbol,
                'benchmark_return_pct': benchmark_return * 100,
                'benchmark_annualized_return_pct': benchmark_metrics.get('annualized_return', 0),
                'benchmark_volatility_pct': benchmark_metrics.get('volatility', 0),
                'benchmark_sharpe_ratio': benchmark_metrics.get('sharpe_ratio', 0),
                'benchmark_max_drawdown_pct': benchmark_metrics.get('max_drawdown', 0),
                'excess_return_pct': (portfolio_return - benchmark_return) * 100,
                'tracking_error_pct': self._calculate_tracking_error(portfolio_values, benchmark_values),
                'information_ratio': self._calculate_information_ratio(portfolio_values, benchmark_values),
                'correlation': self._calculate_correlation(portfolio_values, benchmark_values),
                'benchmark_time_series': benchmark_values[:100]  # 限制数据量
            }
        except Exception as e:
            print(f"Benchmark comparison error: {e}")
            return None
    
    def _calculate_tracking_error(self, portfolio_values: List[Dict], 
                                 benchmark_values: List[Dict]) -> float:
        """计算跟踪误差"""
        try:
            import numpy as np
            
            # 确保数据长度一致
            min_len = min(len(portfolio_values), len(benchmark_values))
            
            # 计算日收益率
            portfolio_returns = []
            benchmark_returns = []
            
            for i in range(1, min_len):
                p_ret = (portfolio_values[i]['value'] / portfolio_values[i-1]['value'] - 1)
                b_ret = (benchmark_values[i]['value'] / benchmark_values[i-1]['value'] - 1)
                portfolio_returns.append(p_ret)
                benchmark_returns.append(b_ret)
            
            # 计算跟踪误差
            diff_returns = np.array(portfolio_returns) - np.array(benchmark_returns)
            tracking_error = np.std(diff_returns) * np.sqrt(252) * 100  # 年化
            
            return round(tracking_error, 2)
        except:
            return 0
    
    def _calculate_information_ratio(self, portfolio_values: List[Dict], 
                                    benchmark_values: List[Dict]) -> float:
        """计算信息比率"""
        try:
            tracking_error = self._calculate_tracking_error(portfolio_values, benchmark_values)
            if tracking_error == 0:
                return 0
            
            portfolio_return = portfolio_values[-1]['value'] / portfolio_values[0]['value'] - 1
            benchmark_return = benchmark_values[-1]['value'] / benchmark_values[0]['value'] - 1
            excess_return = (portfolio_return - benchmark_return) * 100
            
            return round(excess_return / tracking_error, 2)
        except:
            return 0
    
    def _calculate_correlation(self, portfolio_values: List[Dict], 
                              benchmark_values: List[Dict]) -> float:
        """计算相关性"""
        try:
            import numpy as np
            
            min_len = min(len(portfolio_values), len(benchmark_values))
            
            portfolio_returns = []
            benchmark_returns = []
            
            for i in range(1, min_len):
                p_ret = (portfolio_values[i]['value'] / portfolio_values[i-1]['value'] - 1)
                b_ret = (benchmark_values[i]['value'] / benchmark_values[i-1]['value'] - 1)
                portfolio_returns.append(p_ret)
                benchmark_returns.append(b_ret)
            
            correlation = np.corrcoef(portfolio_returns, benchmark_returns)[0, 1]
            return round(correlation, 2)
        except:
            return 0