# 单元测试规范文档

## 测试策略概述

每个模块开发完成后都必须编写对应的单元测试，确保代码质量和功能正确性。采用简单、直接的测试方法，专注于测试函数的基础功能。

## 测试文件命名规范

### 文件命名规则
```
源文件: {module_name}.py
测试文件: {module_name}_test.py
```

### 示例对应关系
```
app/dao/finance_dao.py          → tests/dao/finance_dao_test.py
app/services/backtest_service.py → tests/services/backtest_service_test.py
app/utils/financial_calculator.py → tests/utils/financial_calculator_test.py
app/controllers/portfolio_controller.py → tests/controllers/portfolio_controller_test.py
```

## 测试目录结构

```
backtest/
├── app/
│   ├── dao/
│   │   ├── finance_dao.py
│   │   ├── portfolio_dao.py
│   │   └── backtest_dao.py
│   ├── services/
│   │   ├── backtest_service.py
│   │   └── portfolio_service.py
│   └── utils/
│       └── financial_calculator.py
│
└── tests/                          # 测试根目录
    ├── __init__.py
    ├── conftest.py                 # pytest配置和fixture
    ├── dao/                        # DAO层测试
    │   ├── __init__.py
    │   ├── finance_dao_test.py
    │   ├── portfolio_dao_test.py
    │   └── backtest_dao_test.py
    ├── services/                   # 服务层测试
    │   ├── __init__.py
    │   ├── backtest_service_test.py
    │   └── portfolio_service_test.py
    ├── utils/                      # 工具类测试
    │   ├── __init__.py
    │   └── financial_calculator_test.py
    ├── controllers/                # 控制器测试
    │   ├── __init__.py
    │   └── portfolio_controller_test.py
    └── integration/                # 集成测试
        ├── __init__.py
        └── backtest_integration_test.py
```

## 测试编写规范

### 1. 基本测试模板

```python
# tests/dao/finance_dao_test.py
import pytest
from unittest.mock import Mock, patch
import pandas as pd
from datetime import datetime

from app.dao.finance_dao import FinanceDAO


class TestFinanceDAO:
    """FinanceDAO 单元测试类"""
    
    def setup_method(self):
        """每个测试方法前的初始化"""
        self.finance_dao = FinanceDAO()
    
    def test_get_stock_data_success(self):
        """测试成功获取股票数据"""
        # Arrange (准备)
        symbol = "AAPL"
        start_date = "2020-01-01"
        end_date = "2020-12-31"
        
        # Mock yfinance返回数据
        mock_data = pd.DataFrame({
            'Open': [100.0, 101.0],
            'High': [102.0, 103.0],
            'Low': [99.0, 100.0],
            'Close': [101.0, 102.0],
            'Volume': [1000000, 1100000]
        })
        
        # Act (执行)
        with patch('yfinance.Ticker') as mock_ticker:
            mock_ticker.return_value.history.return_value = mock_data
            result = self.finance_dao.get_stock_data(symbol, start_date, end_date)
        
        # Assert (断言)
        assert result is not None
        assert len(result) == 2
        assert 'Close' in result[0]
        mock_ticker.assert_called_once_with(symbol)
    
    def test_get_stock_data_invalid_symbol(self):
        """测试无效股票代码"""
        # Arrange
        symbol = "INVALID"
        start_date = "2020-01-01"
        end_date = "2020-12-31"
        
        # Act & Assert
        with patch('yfinance.Ticker') as mock_ticker:
            mock_ticker.return_value.history.side_effect = Exception("Invalid symbol")
            
            with pytest.raises(Exception) as exc_info:
                self.finance_dao.get_stock_data(symbol, start_date, end_date)
            
            assert "Invalid symbol" in str(exc_info.value)
    
    def test_get_stock_data_empty_result(self):
        """测试返回空数据"""
        # Arrange
        symbol = "AAPL"
        start_date = "2020-01-01"
        end_date = "2020-01-02"
        
        # Act
        with patch('yfinance.Ticker') as mock_ticker:
            mock_ticker.return_value.history.return_value = pd.DataFrame()
            result = self.finance_dao.get_stock_data(symbol, start_date, end_date)
        
        # Assert
        assert result == []
```

### 2. 财务计算测试示例

```python
# tests/utils/financial_calculator_test.py
import pytest
from app.utils.financial_calculator import FinancialCalculator


class TestFinancialCalculator:
    """财务计算器单元测试"""
    
    def setup_method(self):
        self.calculator = FinancialCalculator()
    
    def test_calculate_total_return(self):
        """测试总收益率计算"""
        # Arrange
        start_value = 10000.0
        end_value = 12000.0
        expected_return = 20.0  # 20%
        
        # Act
        result = self.calculator.calculate_total_return(start_value, end_value)
        
        # Assert
        assert result == expected_return
    
    def test_calculate_annualized_return(self):
        """测试年化收益率计算"""
        # Arrange
        start_value = 10000.0
        end_value = 12000.0
        years = 2.0
        expected_return = 9.54  # 约9.54%
        
        # Act
        result = self.calculator.calculate_annualized_return(start_value, end_value, years)
        
        # Assert
        assert abs(result - expected_return) < 0.1
    
    def test_calculate_volatility(self):
        """测试波动率计算"""
        # Arrange
        returns = [0.01, -0.02, 0.03, -0.01, 0.02]
        
        # Act
        result = self.calculator.calculate_volatility(returns)
        
        # Assert
        assert result > 0
        assert isinstance(result, float)
    
    def test_calculate_max_drawdown(self):
        """测试最大回撤计算"""
        # Arrange
        values = [10000, 11000, 9000, 8000, 10500]
        expected_drawdown = -27.27  # 从11000到8000
        
        # Act
        result = self.calculator.calculate_max_drawdown(values)
        
        # Assert
        assert abs(result - expected_drawdown) < 0.1
    
    def test_calculate_sharpe_ratio(self):
        """测试夏普比率计算"""
        # Arrange
        returns = [0.01, 0.02, -0.01, 0.03, 0.01]
        risk_free_rate = 0.0
        
        # Act
        result = self.calculator.calculate_sharpe_ratio(returns, risk_free_rate)
        
        # Assert
        assert isinstance(result, float)
        assert result > 0  # 正收益应该有正夏普比率
```

### 3. 服务层测试示例

```python
# tests/services/backtest_service_test.py
import pytest
from unittest.mock import Mock, AsyncMock, patch
from app.services.backtest_service import BacktestService


class TestBacktestService:
    """回测服务单元测试"""
    
    @pytest.fixture
    def mock_dependencies(self):
        """模拟依赖项"""
        with patch('app.services.backtest_service.FinanceDAO') as mock_dao, \
             patch('app.services.backtest_service.FinancialCalculator') as mock_calc:
            yield {
                'dao': mock_dao.return_value,
                'calculator': mock_calc.return_value
            }
    
    def test_run_backtest_success(self, mock_dependencies):
        """测试成功执行回测"""
        # Arrange
        service = BacktestService()
        portfolio_config = {
            'assets': [
                {'symbol': 'AAPL', 'weight': 0.6},
                {'symbol': 'MSFT', 'weight': 0.4}
            ],
            'start_date': '2020-01-01',
            'end_date': '2020-12-31',
            'initial_amount': 10000
        }
        
        # Mock数据
        mock_dependencies['dao'].get_stock_data.return_value = {
            'AAPL': [{'Close': 100}, {'Close': 110}],
            'MSFT': [{'Close': 200}, {'Close': 220}]
        }
        
        mock_dependencies['calculator'].calculate_total_return.return_value = 15.0
        mock_dependencies['calculator'].calculate_volatility.return_value = 12.5
        
        # Act
        result = service.run_backtest(portfolio_config)
        
        # Assert
        assert result is not None
        assert 'metrics' in result
        assert 'chart_data' in result
        assert result['metrics']['total_return'] == 15.0
    
    def test_validate_portfolio_config_invalid_weights(self):
        """测试无效权重验证"""
        # Arrange
        service = BacktestService()
        invalid_config = {
            'assets': [
                {'symbol': 'AAPL', 'weight': 0.6},
                {'symbol': 'MSFT', 'weight': 0.5}  # 总权重 > 1
            ]
        }
        
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            service._validate_portfolio_config(invalid_config)
        
        assert "权重总和必须等于100%" in str(exc_info.value)
```

## 测试配置

### pytest配置文件 (tests/conftest.py)

```python
# tests/conftest.py
import pytest
import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.models.database import Base


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
        'name': '测试投资组合',
        'assets': [
            {'symbol': 'AAPL', 'weight': 0.4},
            {'symbol': 'MSFT', 'weight': 0.3},
            {'symbol': 'GOOGL', 'weight': 0.3}
        ],
        'start_date': '2020-01-01',
        'end_date': '2020-12-31',
        'initial_amount': 10000.0
    }
```

## 测试运行命令

### 安装测试依赖
```bash
pip install pytest pytest-mock pytest-asyncio pytest-cov
```

### 运行测试命令
```bash
# 运行所有测试
pytest

# 运行特定模块测试
pytest tests/dao/finance_dao_test.py

# 运行特定测试类
pytest tests/dao/finance_dao_test.py::TestFinanceDAO

# 运行特定测试方法
pytest tests/dao/finance_dao_test.py::TestFinanceDAO::test_get_stock_data_success

# 运行测试并生成覆盖率报告
pytest --cov=app --cov-report=html

# 运行测试并显示详细输出
pytest -v -s
```

## 测试编写原则

### 1. FIRST原则
- **Fast (快速)**: 测试应该快速执行
- **Independent (独立)**: 测试之间不应有依赖关系
- **Repeatable (可重复)**: 测试结果应该一致
- **Self-Validating (自验证)**: 测试结果应该明确（通过/失败）
- **Timely (及时)**: 测试应该与代码同时编写

### 2. AAA模式
- **Arrange (准备)**: 设置测试数据和环境
- **Act (执行)**: 执行被测试的方法
- **Assert (断言)**: 验证结果是否符合预期

### 3. 测试覆盖重点
- **正常路径**: 测试函数的正常执行流程
- **边界条件**: 测试边界值和极限情况
- **异常处理**: 测试错误输入和异常情况
- **数据验证**: 测试输入验证和数据类型检查

### 4. Mock使用原则
- **外部依赖**: Mock外部API调用、数据库操作
- **复杂对象**: Mock复杂的第三方库对象
- **不确定结果**: Mock随机数、当前时间等
- **性能考虑**: Mock耗时操作

## 测试质量标准

### 代码覆盖率目标
- **整体覆盖率**: ≥ 80%
- **核心业务逻辑**: ≥ 90%
- **工具函数**: ≥ 95%
- **DAO层**: ≥ 85%

### 测试文件要求
- 每个模块都必须有对应的测试文件
- 每个公共方法都必须有测试用例
- 测试方法命名要清晰描述测试场景
- 测试代码要简洁、易读、易维护

## 持续集成配置

### GitHub Actions示例 (.github/workflows/test.yml)
```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.12'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-mock pytest-asyncio pytest-cov
    
    - name: Run tests
      run: |
        pytest --cov=app --cov-report=xml
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v1
```

这个测试规范确保每个开发的模块都有相应的单元测试，保证代码质量和功能正确性。