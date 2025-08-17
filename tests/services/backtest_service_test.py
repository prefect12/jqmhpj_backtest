"""
回测服务单元测试
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from app.services.backtest_service import BacktestService


class TestBacktestService:
    """回测服务测试类"""
    
    def setup_method(self):
        """每个测试方法前的初始化"""
        self.backtest_service = BacktestService()
    
    def test_validate_config_success(self):
        """测试成功验证配置"""
        # Arrange
        config = {
            'assets': [
                {'symbol': 'AAPL', 'weight': 60.0},
                {'symbol': 'MSFT', 'weight': 40.0}
            ],
            'start_date': '2020-01-01',
            'end_date': '2020-12-31',
            'initial_amount': 10000.0
        }
        
        # Act & Assert (不应抛出异常)
        self.backtest_service._validate_config(config)
    
    def test_validate_config_missing_field(self):
        """测试缺少必需字段"""
        # Arrange
        config = {
            'assets': [{'symbol': 'AAPL', 'weight': 100.0}],
            'start_date': '2020-01-01',
            # missing end_date
            'initial_amount': 10000.0
        }
        
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            self.backtest_service._validate_config(config)
        
        assert "Missing required field: end_date" in str(exc_info.value)
    
    def test_validate_config_invalid_weights(self):
        """测试无效权重总和"""
        # Arrange
        config = {
            'assets': [
                {'symbol': 'AAPL', 'weight': 60.0},
                {'symbol': 'MSFT', 'weight': 50.0}  # 总和110%
            ],
            'start_date': '2020-01-01',
            'end_date': '2020-12-31',
            'initial_amount': 10000.0
        }
        
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            self.backtest_service._validate_config(config)
        
        assert "Weights must sum to 100%" in str(exc_info.value)
    
    def test_validate_config_empty_assets(self):
        """测试空资产列表"""
        # Arrange
        config = {
            'assets': [],
            'start_date': '2020-01-01',
            'end_date': '2020-12-31',
            'initial_amount': 10000.0
        }
        
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            self.backtest_service._validate_config(config)
        
        assert "At least one asset is required" in str(exc_info.value)
    
    def test_validate_config_too_many_assets(self):
        """测试资产数量超限"""
        # Arrange
        config = {
            'assets': [
                {'symbol': f'STOCK{i}', 'weight': 10.0} 
                for i in range(11)  # 11个资产
            ],
            'start_date': '2020-01-01',
            'end_date': '2020-12-31',
            'initial_amount': 10000.0
        }
        
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            self.backtest_service._validate_config(config)
        
        assert "Maximum" in str(exc_info.value) and "assets allowed" in str(exc_info.value)
    
    def test_validate_config_invalid_initial_amount_too_low(self):
        """测试初始金额过低"""
        # Arrange
        config = {
            'assets': [{'symbol': 'AAPL', 'weight': 100.0}],
            'start_date': '2020-01-01',
            'end_date': '2020-12-31',
            'initial_amount': 500.0  # 低于最小值
        }
        
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            self.backtest_service._validate_config(config)
        
        assert "Minimum initial amount" in str(exc_info.value)
    
    def test_validate_config_invalid_initial_amount_too_high(self):
        """测试初始金额过高"""
        # Arrange
        config = {
            'assets': [{'symbol': 'AAPL', 'weight': 100.0}],
            'start_date': '2020-01-01',
            'end_date': '2020-12-31',
            'initial_amount': 2000000.0  # 高于最大值
        }
        
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            self.backtest_service._validate_config(config)
        
        assert "Maximum initial amount" in str(exc_info.value)
    
    def test_run_backtest_success(self):
        """测试成功执行回测"""
        # Arrange
        portfolio_config = {
            'assets': [
                {'symbol': 'AAPL', 'weight': 60.0},
                {'symbol': 'MSFT', 'weight': 40.0}
            ],
            'start_date': '2020-01-01',
            'end_date': '2020-12-31',
            'initial_amount': 10000.0
        }
        
        # Mock依赖
        self.backtest_service.stock_dao = Mock()
        self.backtest_service.calculator = Mock()
        
        # Mock股票数据
        self.backtest_service.stock_dao.get_multiple_stocks_data.return_value = {
            'AAPL': [
                {'Date': '2020-01-01', 'Close': 100.0},
                {'Date': '2020-01-02', 'Close': 105.0}
            ],
            'MSFT': [
                {'Date': '2020-01-01', 'Close': 200.0},
                {'Date': '2020-01-02', 'Close': 210.0}
            ]
        }
        
        # Mock计算结果
        self.backtest_service.calculator.calculate_portfolio_values.return_value = [
            {'date': '2020-01-01', 'value': 10000.0},
            {'date': '2020-01-02', 'value': 10500.0}
        ]
        
        self.backtest_service.calculator.calculate_risk_metrics.return_value = {
            'total_return': 5.0,
            'annualized_return': 15.0,
            'volatility': 20.0,
            'max_drawdown': -10.0,
            'sharpe_ratio': 0.75,
            'sortino_ratio': 1.0,
            'positive_rate': 60.0
        }
        
        self.backtest_service.calculator.calculate_annual_returns.return_value = [
            {'year': 2020, 'annual_return': 15.0}
        ]
        
        # Act
        result = self.backtest_service.run_backtest(portfolio_config)
        
        # Assert
        assert result['status'] == 'completed'
        assert 'backtest_id' in result
        assert result['performance_summary']['total_return_pct'] == 5.0
        assert result['risk_metrics']['volatility_annual_pct'] == 20.0
        assert len(result['portfolio_composition']) == 2
    
    def test_run_backtest_data_fetch_error(self):
        """测试数据获取失败"""
        # Arrange
        portfolio_config = {
            'assets': [{'symbol': 'INVALID', 'weight': 100.0}],
            'start_date': '2020-01-01',
            'end_date': '2020-12-31',
            'initial_amount': 10000.0
        }
        
        # Mock错误
        self.backtest_service.stock_dao = Mock()
        self.backtest_service.stock_dao.get_multiple_stocks_data.side_effect = Exception("Failed to fetch data")
        
        # Act
        result = self.backtest_service.run_backtest(portfolio_config)
        
        # Assert
        assert result['status'] == 'failed'
        assert 'error' in result
        assert "Failed to fetch data" in result['error']
    
    @patch('app.services.backtest_service.StockDataDAO')
    @patch('app.services.backtest_service.FinancialCalculator')
    def test_run_backtest_empty_stock_data(self, mock_calculator, mock_dao):
        """测试空股票数据处理"""
        # Arrange
        portfolio_config = {
            'assets': [{'symbol': 'AAPL', 'weight': 100.0}],
            'start_date': '2020-01-01',
            'end_date': '2020-01-02',
            'initial_amount': 10000.0
        }
        
        # Mock空数据
        mock_dao.return_value.get_multiple_stocks_data.return_value = {
            'AAPL': []
        }
        
        mock_calculator.return_value.calculate_portfolio_values.return_value = []
        mock_calculator.return_value.calculate_risk_metrics.return_value = {}
        mock_calculator.return_value.calculate_annual_returns.return_value = []
        
        # Act
        result = self.backtest_service.run_backtest(portfolio_config)
        
        # Assert
        assert result['status'] == 'completed'
        assert result['performance_summary']['end_value'] == 0
        assert result['time_series'] == []