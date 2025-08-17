"""
StockDataDAO 单元测试
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import pandas as pd
from datetime import datetime

from app.dao.stock_data_dao import StockDataDAO


class TestStockDataDAO:
    """StockDataDAO 单元测试类"""
    
    def setup_method(self):
        """每个测试方法前的初始化"""
        self.stock_dao = StockDataDAO()
    
    def test_get_stock_data_success(self):
        """测试成功获取股票数据"""
        # Arrange
        symbol = "AAPL"
        start_date = "2020-01-01"
        end_date = "2020-01-03"
        
        # Mock yfinance返回数据
        mock_data = pd.DataFrame({
            'Open': [100.0, 101.0, 102.0],
            'High': [102.0, 103.0, 104.0],
            'Low': [99.0, 100.0, 101.0],
            'Close': [101.0, 102.0, 103.0],
            'Volume': [1000000, 1100000, 1200000]
        }, index=pd.date_range(start=start_date, periods=3))
        
        # Act
        with patch('yfinance.Ticker') as mock_ticker:
            mock_instance = MagicMock()
            mock_instance.history.return_value = mock_data
            mock_ticker.return_value = mock_instance
            
            result = self.stock_dao.get_stock_data(symbol, start_date, end_date)
        
        # Assert
        assert result is not None
        assert len(result) == 3
        assert result[0]['Close'] == 101.0
        assert 'Date' in result[0]
        mock_ticker.assert_called_once_with(symbol)
    
    def test_get_stock_data_empty_result(self):
        """测试返回空数据"""
        # Arrange
        symbol = "AAPL"
        start_date = "2020-01-01"
        end_date = "2020-01-02"
        
        # Act & Assert
        with patch('yfinance.Ticker') as mock_ticker:
            mock_instance = MagicMock()
            mock_instance.history.return_value = pd.DataFrame()
            mock_ticker.return_value = mock_instance
            
            with pytest.raises(Exception) as exc_info:
                self.stock_dao.get_stock_data(symbol, start_date, end_date)
            
            assert "No data available" in str(exc_info.value)
    
    def test_get_multiple_stocks_data(self):
        """测试获取多只股票数据"""
        # Arrange
        symbols = ["AAPL", "MSFT"]
        start_date = "2020-01-01"
        end_date = "2020-01-03"
        
        mock_data = pd.DataFrame({
            'Open': [100.0, 101.0],
            'High': [102.0, 103.0],
            'Low': [99.0, 100.0],
            'Close': [101.0, 102.0],
            'Volume': [1000000, 1100000]
        }, index=pd.date_range(start=start_date, periods=2))
        
        # Act
        with patch('yfinance.Ticker') as mock_ticker:
            mock_instance = MagicMock()
            mock_instance.history.return_value = mock_data
            mock_ticker.return_value = mock_instance
            
            result = self.stock_dao.get_multiple_stocks_data(symbols, start_date, end_date)
        
        # Assert
        assert len(result) == 2
        assert "AAPL" in result
        assert "MSFT" in result
        assert len(result["AAPL"]) == 2
        assert len(result["MSFT"]) == 2
    
    def test_validate_symbol_valid(self):
        """测试验证有效股票代码"""
        # Arrange
        symbol = "AAPL"
        
        # Act
        with patch('yfinance.Ticker') as mock_ticker:
            mock_instance = MagicMock()
            mock_instance.info = {'symbol': 'AAPL', 'shortName': 'Apple Inc.'}
            mock_ticker.return_value = mock_instance
            
            result = self.stock_dao.validate_symbol(symbol)
        
        # Assert
        assert result is True
    
    def test_validate_symbol_invalid(self):
        """测试验证无效股票代码"""
        # Arrange
        symbol = "INVALID"
        
        # Act
        with patch('yfinance.Ticker') as mock_ticker:
            mock_instance = MagicMock()
            mock_instance.info = {}
            mock_ticker.return_value = mock_instance
            
            result = self.stock_dao.validate_symbol(symbol)
        
        # Assert
        assert result is False
    
    def test_get_stock_info(self):
        """测试获取股票信息"""
        # Arrange
        symbol = "AAPL"
        
        # Act
        with patch('yfinance.Ticker') as mock_ticker:
            mock_instance = MagicMock()
            mock_instance.info = {
                'longName': 'Apple Inc.',
                'exchange': 'NASDAQ',
                'currency': 'USD',
                'currentPrice': 150.0,
                'marketCap': 2500000000000,
                'trailingPE': 25.5,
                'dividendYield': 0.005,
                'sector': 'Technology',
                'industry': 'Consumer Electronics'
            }
            mock_ticker.return_value = mock_instance
            
            result = self.stock_dao.get_stock_info(symbol)
        
        # Assert
        assert result['symbol'] == symbol
        assert result['name'] == 'Apple Inc.'
        assert result['current_price'] == 150.0
        assert result['sector'] == 'Technology'
    
    def test_search_stocks(self):
        """测试搜索股票"""
        # Arrange
        query = "apple"
        
        # Act
        result = self.stock_dao.search_stocks(query, limit=5)
        
        # Assert
        assert len(result) > 0
        assert result[0]['symbol'] == 'AAPL'
        assert 'Apple' in result[0]['name']
    
    def test_cache_operations(self):
        """测试缓存操作"""
        # Arrange
        symbol = "AAPL"
        start_date = "2020-01-01"
        end_date = "2020-01-03"
        test_data = [
            {'Date': '2020-01-01', 'Open': 100, 'Close': 101, 'Volume': 1000000}
        ]
        
        # Test save to cache
        self.stock_dao._save_to_cache(symbol, start_date, end_date, test_data)
        
        # Test get from cache
        cached_data = self.stock_dao._get_from_cache(symbol, start_date, end_date)
        
        # Assert
        assert cached_data is not None
        assert len(cached_data) == 1
        assert cached_data[0]['Close'] == 101