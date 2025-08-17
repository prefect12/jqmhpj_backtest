"""
定投服务单元测试
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import pandas as pd

from app.services.dca_service import DCAService


class TestDCAService:
    """定投服务测试类"""
    
    def setup_method(self):
        """每个测试方法前的初始化"""
        self.dca_service = DCAService()
    
    @patch('app.services.dca_service.StockDataDAO')
    def test_generate_investment_dates_monthly(self, mock_dao):
        """测试生成月度投资日期"""
        # Arrange
        start_date = "2024-01-01"
        end_date = "2024-03-31"
        frequency = "monthly"
        config = {"day_of_month": 15}
        
        # Act
        dates = self.dca_service._generate_investment_dates(
            start_date, end_date, frequency, config
        )
        
        # Assert
        assert len(dates) == 3
        assert "2024-01-15" in dates
        assert "2024-02-15" in dates
        assert "2024-03-15" in dates
    
    @patch('app.services.dca_service.StockDataDAO')
    def test_generate_investment_dates_weekly(self, mock_dao):
        """测试生成周度投资日期"""
        # Arrange
        start_date = "2024-01-01"
        end_date = "2024-01-31"
        frequency = "weekly"
        config = {}
        
        # Act
        dates = self.dca_service._generate_investment_dates(
            start_date, end_date, frequency, config
        )
        
        # Assert
        assert len(dates) >= 4  # 一月至少有4周
        assert dates[0] == "2024-01-01"
    
    @patch('app.services.dca_service.StockDataDAO')
    def test_calculate_dca_returns_basic(self, mock_dao):
        """测试基本定投收益计算"""
        # Arrange
        stock_data = {
            'AAPL': [
                {'Date': '2024-01-01', 'Close': 100.0},
                {'Date': '2024-01-15', 'Close': 105.0},
                {'Date': '2024-02-01', 'Close': 110.0}
            ]
        }
        assets = [{'symbol': 'AAPL', 'weight': 100.0}]
        initial_amount = 1000.0
        investment_amount = 500.0
        investment_dates = ['2024-01-15']
        
        # Act
        result = self.dca_service._calculate_dca_returns(
            stock_data, assets, initial_amount, 
            investment_amount, investment_dates
        )
        
        # Assert
        assert 'time_series' in result
        assert 'total_invested' in result
        assert result['total_invested'] == 1500.0  # 1000 + 500
        assert len(result['time_series']) == 3
    
    @patch('app.services.dca_service.StockDataDAO')
    def test_calculate_dca_metrics(self, mock_dao):
        """测试定投指标计算"""
        # Arrange
        results = {
            'time_series': [
                {'date': '2024-01-01', 'invested': 1000, 'value': 1000, 'return_pct': 0},
                {'date': '2024-01-15', 'invested': 1500, 'value': 1600, 'return_pct': 6.67},
                {'date': '2024-02-01', 'invested': 2000, 'value': 2200, 'return_pct': 10.0}
            ],
            'total_invested': 2000
        }
        
        # Act
        metrics = self.dca_service._calculate_dca_metrics(results)
        
        # Assert
        assert metrics['total_invested'] == 2000
        assert metrics['final_value'] == 2200
        assert metrics['total_return'] == 200
        assert metrics['total_return_pct'] == 10.0
        assert metrics['best_return'] == 10.0
        assert metrics['worst_return'] == 0
    
    @patch('app.services.dca_service.StockDataDAO')
    def test_run_periodic_dca_success(self, mock_dao):
        """测试成功执行定期定投"""
        # Arrange
        dca_config = {
            'assets': [{'symbol': 'AAPL', 'weight': 100.0}],
            'start_date': '2024-01-01',
            'end_date': '2024-02-29',
            'initial_amount': 10000.0,
            'investment_amount': 1000.0,
            'frequency': 'monthly',
            'frequency_config': {'day_of_month': 1}
        }
        
        # Mock股票数据
        mock_dao.return_value.get_multiple_stocks_data.return_value = {
            'AAPL': [
                {'Date': '2024-01-01', 'Close': 150.0},
                {'Date': '2024-02-01', 'Close': 160.0}
            ]
        }
        
        # Act
        result = self.dca_service.run_periodic_dca(dca_config)
        
        # Assert
        assert result['status'] == 'completed'
        assert 'dca_id' in result
        assert 'config_summary' in result
        assert 'performance' in result
        assert result['config_summary']['frequency'] == 'monthly'
    
    @patch('app.services.dca_service.StockDataDAO')
    def test_run_periodic_dca_error_handling(self, mock_dao):
        """测试定期定投错误处理"""
        # Arrange
        dca_config = {
            'assets': [{'symbol': 'INVALID', 'weight': 100.0}],
            'start_date': '2024-01-01',
            'end_date': '2024-02-29',
            'initial_amount': 10000.0,
            'investment_amount': 1000.0,
            'frequency': 'monthly'
        }
        
        # Mock错误
        mock_dao.return_value.get_multiple_stocks_data.side_effect = Exception("Invalid symbol")
        
        # Act
        result = self.dca_service.run_periodic_dca(dca_config)
        
        # Assert
        assert result['status'] == 'failed'
        assert 'error' in result
        assert "No valid stock data retrieved" in result['error']
    
    def test_detect_price_drop_trigger(self):
        """测试价格下跌触发条件检测"""
        # Arrange
        stock_data = {
            'AAPL': [
                {'Date': '2024-01-01', 'Close': 100.0},
                {'Date': '2024-01-02', 'Close': 96.0},  # 4% drop
                {'Date': '2024-01-03', 'Close': 95.0}
            ]
        }
        conditions = [{
            'type': 'price_drop',
            'config': {
                'drop_percentage': 3.0,
                'amount': 2000.0,
                'cooldown_days': 1
            }
        }]
        
        # Act
        triggers = self.dca_service._detect_condition_triggers(
            stock_data, conditions, '2024-01-01', '2024-01-03'
        )
        
        # Assert
        assert len(triggers) >= 1
        assert triggers[0]['type'] == 'price_drop'
        assert triggers[0]['amount'] == 2000.0
    
    def test_check_cooldown(self):
        """测试冷却期检查"""
        # Arrange
        current_date = "2024-01-10"
        last_trigger_date = "2024-01-05"
        cooldown_days = 7
        
        # Act
        result = self.dca_service._check_cooldown(
            current_date, last_trigger_date, cooldown_days
        )
        
        # Assert
        assert result == False  # 5天 < 7天冷却期
        
        # Test with enough cooldown
        current_date = "2024-01-13"
        result = self.dca_service._check_cooldown(
            current_date, last_trigger_date, cooldown_days
        )
        assert result == True  # 8天 >= 7天冷却期
    
    @patch('app.services.dca_service.StockDataDAO')
    def test_run_conditional_dca_success(self, mock_dao):
        """测试成功执行条件定投"""
        # Arrange
        dca_config = {
            'assets': [{'symbol': 'AAPL', 'weight': 100.0}],
            'start_date': '2024-01-01',
            'end_date': '2024-01-31',
            'initial_amount': 10000.0,
            'conditions': [{
                'type': 'price_drop',
                'config': {
                    'drop_percentage': 3.0,
                    'amount': 2000.0,
                    'cooldown_days': 7
                }
            }]
        }
        
        # Mock股票数据，包含价格下跌
        mock_dao.return_value.get_multiple_stocks_data.return_value = {
            'AAPL': [
                {'Date': '2024-01-01', 'Close': 100.0},
                {'Date': '2024-01-02', 'Close': 96.0},  # 4% drop - triggers
                {'Date': '2024-01-03', 'Close': 98.0}
            ]
        }
        
        # Act
        result = self.dca_service.run_conditional_dca(dca_config)
        
        # Assert
        assert result['status'] == 'completed'
        assert 'dca_id' in result
        assert 'triggers' in result
        assert result['config_summary']['condition_count'] == 1
    
    def test_calculate_portfolio_prices(self):
        """测试计算投资组合价格"""
        # Arrange
        stock_data = {
            'AAPL': [
                {'Date': '2024-01-01', 'Close': 100.0},
                {'Date': '2024-01-02', 'Close': 105.0}
            ],
            'MSFT': [
                {'Date': '2024-01-01', 'Close': 200.0},
                {'Date': '2024-01-02', 'Close': 210.0}
            ]
        }
        
        # Act
        prices = self.dca_service._calculate_portfolio_prices(stock_data)
        
        # Assert
        assert len(prices) == 2
        assert prices[0]['date'] == '2024-01-01'
        assert prices[0]['price'] == 150.0  # (100 + 200) / 2
        assert prices[1]['date'] == '2024-01-02'
        assert prices[1]['price'] == 157.5  # (105 + 210) / 2