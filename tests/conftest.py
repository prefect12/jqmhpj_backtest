"""
pytest配置和通用fixture
"""
import pytest
import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.core.database import Base
from app.models import Portfolio, BacktestResult, BacktestConfig


@pytest.fixture(scope="session")
def test_database():
    """测试数据库fixture"""
    # 使用内存SQLite数据库
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    
    TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    yield TestSessionLocal
    
    engine.dispose()


@pytest.fixture
def db_session(test_database):
    """数据库会话fixture"""
    session = test_database()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture
def sample_portfolio_config():
    """示例投资组合配置"""
    return {
        'portfolio_id': 'port_test_001',
        'name': '测试投资组合',
        'assets': [
            {'symbol': 'AAPL', 'weight': 40.0},
            {'symbol': 'MSFT', 'weight': 30.0},
            {'symbol': 'GOOGL', 'weight': 30.0}
        ],
        'total_weight': 100.0,
        'asset_count': 3
    }


@pytest.fixture
def sample_backtest_config():
    """示例回测配置"""
    return {
        'portfolio_id': 'port_test_001',
        'start_date': '2020-01-01',
        'end_date': '2020-12-31',
        'initial_amount': 10000.0,
        'rebalance_frequency': 'quarterly',
        'reinvest_dividends': True
    }


@pytest.fixture
def sample_stock_data():
    """示例股票数据"""
    return {
        'AAPL': [
            {'Date': '2020-01-01', 'Open': 100.0, 'High': 102.0, 'Low': 99.0, 'Close': 101.0, 'Volume': 1000000},
            {'Date': '2020-01-02', 'Open': 101.0, 'High': 103.0, 'Low': 100.0, 'Close': 102.0, 'Volume': 1100000},
            {'Date': '2020-01-03', 'Open': 102.0, 'High': 104.0, 'Low': 101.0, 'Close': 103.0, 'Volume': 1200000},
        ],
        'MSFT': [
            {'Date': '2020-01-01', 'Open': 200.0, 'High': 202.0, 'Low': 199.0, 'Close': 201.0, 'Volume': 2000000},
            {'Date': '2020-01-02', 'Open': 201.0, 'High': 203.0, 'Low': 200.0, 'Close': 202.0, 'Volume': 2100000},
            {'Date': '2020-01-03', 'Open': 202.0, 'High': 204.0, 'Low': 201.0, 'Close': 203.0, 'Volume': 2200000},
        ],
        'GOOGL': [
            {'Date': '2020-01-01', 'Open': 1000.0, 'High': 1020.0, 'Low': 990.0, 'Close': 1010.0, 'Volume': 500000},
            {'Date': '2020-01-02', 'Open': 1010.0, 'High': 1030.0, 'Low': 1000.0, 'Close': 1020.0, 'Volume': 510000},
            {'Date': '2020-01-03', 'Open': 1020.0, 'High': 1040.0, 'Low': 1010.0, 'Close': 1030.0, 'Volume': 520000},
        ]
    }