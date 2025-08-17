# 架构设计文档

## 项目架构概述

基于项目体量较小的考虑，采用**一体化架构**设计，而非前后端分离。使用传统的MVC模式和分层架构，提供更好的开发效率和部署简便性。

## 整体架构图

```
┌─────────────────────────────────────────┐
│              Web 浏览器                  │
└─────────────────┬───────────────────────┘
                  │ HTTP Request/Response
┌─────────────────▼───────────────────────┐
│              FastAPI 应用                │
├─────────────────────────────────────────┤
│            表现层 (Presentation)         │
│  - 路由控制器 (Controllers)              │
│  - 模板渲染 (Jinja2 Templates)          │
│  - 静态文件服务                          │
├─────────────────────────────────────────┤
│             服务层 (Service)             │
│  - 业务逻辑服务                          │
│  - 回测计算引擎                          │
│  - 数据验证服务                          │
├─────────────────────────────────────────┤
│             数据访问层 (DAO)             │
│  - 数据访问对象                          │
│  - 缓存管理                              │
│  - 外部数据源接口                        │
├─────────────────────────────────────────┤
│             数据层 (Data)                │
│  - SQLite 数据库                         │
│  - Yahoo Finance API                     │
│  - 本地缓存                              │
└─────────────────────────────────────────┘
```

## 分层架构设计

### 1. 表现层 (Presentation Layer)
负责用户界面和用户交互。

```python
# 职责
- HTTP请求处理
- 路由分发
- 模板渲染
- 表单验证
- 静态文件服务
- 错误页面处理
```

### 2. 服务层 (Service Layer)
包含核心业务逻辑。

```python
# 职责
- 投资组合管理
- 回测计算引擎
- 风险指标计算
- 数据格式化
- 业务规则验证
- 结果缓存管理
```

### 3. 数据访问层 (DAO Layer)
负责数据的读写操作。

```python
# 职责
- 数据库CRUD操作
- 外部API调用
- 数据缓存策略
- 数据源切换
- 连接池管理
```

### 4. 数据层 (Data Layer)
数据存储和外部数据源。

```python
# 组成
- SQLite 数据库
- Yahoo Finance API
- 本地文件缓存
- 日志文件
```

## 项目目录结构

```
backtest/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI应用入口
│   │
│   ├── controllers/            # 表现层 - 控制器
│   │   ├── __init__.py
│   │   ├── home_controller.py      # 首页控制器
│   │   ├── portfolio_controller.py # 投资组合控制器
│   │   └── backtest_controller.py  # 回测控制器
│   │
│   ├── services/               # 服务层 - 业务逻辑
│   │   ├── __init__.py
│   │   ├── portfolio_service.py    # 投资组合服务
│   │   ├── backtest_service.py     # 回测计算服务
│   │   ├── data_service.py         # 数据获取服务
│   │   ├── calculation_service.py  # 财务计算服务
│   │   └── validation_service.py   # 数据验证服务
│   │
│   ├── dao/                    # 数据访问层
│   │   ├── __init__.py
│   │   ├── portfolio_dao.py        # 投资组合数据访问
│   │   ├── backtest_dao.py         # 回测数据访问
│   │   ├── stock_data_dao.py       # 股票数据访问
│   │   └── cache_dao.py            # 缓存数据访问
│   │
│   ├── models/                 # 数据模型
│   │   ├── __init__.py
│   │   ├── database.py             # 数据库配置
│   │   ├── portfolio.py            # 投资组合模型
│   │   ├── backtest.py             # 回测模型
│   │   └── stock.py                # 股票数据模型
│   │
│   ├── utils/                  # 工具类
│   │   ├── __init__.py
│   │   ├── financial_calculator.py # 财务计算工具
│   │   ├── date_utils.py           # 日期工具
│   │   ├── validators.py           # 验证工具
│   │   └── formatters.py           # 格式化工具
│   │
│   ├── core/                   # 核心配置
│   │   ├── __init__.py
│   │   ├── config.py               # 应用配置
│   │   ├── database.py             # 数据库配置
│   │   ├── logging.py              # 日志配置
│   │   └── exceptions.py           # 异常定义
│   │
│   └── static/                 # 静态文件
│       ├── css/                    # 样式文件
│       ├── js/                     # JavaScript文件
│       ├── images/                 # 图片文件
│       └── lib/                    # 第三方库
│
├── templates/                  # 模板文件
│   ├── base.html                   # 基础模板
│   ├── index.html                  # 首页
│   ├── portfolio/                  # 投资组合相关页面
│   │   ├── create.html
│   │   ├── list.html
│   │   └── detail.html
│   └── backtest/                   # 回测相关页面
│       ├── config.html
│       ├── result.html
│       └── charts.html
│
├── tests/                      # 测试文件
│   ├── __init__.py
│   ├── conftest.py                 # pytest配置和fixture
│   ├── dao/                        # DAO层测试
│   │   ├── __init__.py
│   │   ├── finance_dao_test.py
│   │   ├── portfolio_dao_test.py
│   │   └── backtest_dao_test.py
│   ├── services/                   # 服务层测试
│   │   ├── __init__.py
│   │   ├── backtest_service_test.py
│   │   └── portfolio_service_test.py
│   ├── utils/                      # 工具类测试
│   │   ├── __init__.py
│   │   └── financial_calculator_test.py
│   ├── controllers/                # 控制器测试
│   │   ├── __init__.py
│   │   └── portfolio_controller_test.py
│   └── integration/                # 集成测试
│       ├── __init__.py
│       └── backtest_integration_test.py
│
├── logs/                       # 日志文件
├── data/                       # 数据文件
│   ├── cache/                      # 缓存文件
│   └── backtest.db                 # SQLite数据库
│
├── docs/                       # 文档
├── requirements.txt            # Python依赖
├── .env.example               # 环境变量示例
├── .gitignore                 # Git忽略文件
└── README.md                  # 项目说明
```

## 各层详细设计

### 1. 控制器层 (Controllers)

```python
# app/controllers/portfolio_controller.py
from fastapi import APIRouter, Request, Form, Depends
from fastapi.templating import Jinja2Templates
from app.services.portfolio_service import PortfolioService

router = APIRouter(prefix="/portfolio", tags=["portfolio"])
templates = Jinja2Templates(directory="templates")

@router.get("/create")
async def create_portfolio_page(request: Request):
    """显示创建投资组合页面"""
    return templates.TemplateResponse("portfolio/create.html", {
        "request": request
    })

@router.post("/create")
async def create_portfolio(
    request: Request,
    name: str = Form(...),
    assets: str = Form(...),  # JSON字符串
    portfolio_service: PortfolioService = Depends()
):
    """处理创建投资组合请求"""
    try:
        portfolio = await portfolio_service.create_portfolio(name, assets)
        return templates.TemplateResponse("portfolio/detail.html", {
            "request": request,
            "portfolio": portfolio,
            "success": "投资组合创建成功"
        })
    except Exception as e:
        return templates.TemplateResponse("portfolio/create.html", {
            "request": request,
            "error": str(e)
        })
```

### 2. 服务层 (Services)

```python
# app/services/backtest_service.py
from typing import Dict, List
from app.dao.stock_data_dao import StockDataDAO
from app.dao.backtest_dao import BacktestDAO
from app.utils.financial_calculator import FinancialCalculator

class BacktestService:
    def __init__(self):
        self.stock_dao = StockDataDAO()
        self.backtest_dao = BacktestDAO()
        self.calculator = FinancialCalculator()
    
    async def run_backtest(self, portfolio_config: Dict) -> Dict:
        """执行回测计算"""
        # 1. 获取股票历史数据
        stock_data = await self._get_stock_data(portfolio_config)
        
        # 2. 计算投资组合净值
        portfolio_values = self._calculate_portfolio_values(
            stock_data, portfolio_config
        )
        
        # 3. 计算风险收益指标
        metrics = self._calculate_metrics(portfolio_values)
        
        # 4. 保存回测结果
        backtest_id = await self.backtest_dao.save_result(
            portfolio_config, metrics
        )
        
        return {
            "backtest_id": backtest_id,
            "metrics": metrics,
            "chart_data": portfolio_values
        }
    
    def _calculate_portfolio_values(self, stock_data: Dict, config: Dict) -> List:
        """计算投资组合历史净值"""
        # 实现投资组合净值计算逻辑
        pass
    
    def _calculate_metrics(self, values: List) -> Dict:
        """计算风险收益指标"""
        return {
            "total_return": self.calculator.total_return(values),
            "annualized_return": self.calculator.annualized_return(values),
            "volatility": self.calculator.volatility(values),
            "max_drawdown": self.calculator.max_drawdown(values),
            "sharpe_ratio": self.calculator.sharpe_ratio(values)
        }
```

### 3. 数据访问层 (DAO)

```python
# app/dao/stock_data_dao.py
import yfinance as yf
from typing import Dict, List
from datetime import datetime
from app.core.config import settings
from app.dao.cache_dao import CacheDAO

class StockDataDAO:
    def __init__(self):
        self.cache = CacheDAO()
    
    async def get_stock_data(self, symbols: List[str], start_date: str, end_date: str) -> Dict:
        """获取股票历史数据"""
        result = {}
        
        for symbol in symbols:
            cache_key = f"stock_data_{symbol}_{start_date}_{end_date}"
            
            # 尝试从缓存获取
            cached_data = await self.cache.get(cache_key)
            if cached_data:
                result[symbol] = cached_data
                continue
            
            # 从Yahoo Finance获取数据
            try:
                ticker = yf.Ticker(symbol)
                data = ticker.history(
                    start=start_date,
                    end=end_date,
                    timeout=settings.yfinance_timeout
                )
                
                result[symbol] = data.to_dict('records')
                
                # 缓存数据
                await self.cache.set(
                    cache_key, 
                    result[symbol], 
                    ttl=settings.yfinance_cache_ttl
                )
                
            except Exception as e:
                raise Exception(f"获取股票 {symbol} 数据失败: {str(e)}")
        
        return result
    
    async def search_stocks(self, query: str) -> List[Dict]:
        """搜索股票"""
        # 实现股票搜索逻辑
        pass
```

### 4. 数据模型 (Models)

```python
# app/models/portfolio.py
from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Portfolio(Base):
    __tablename__ = "portfolios"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    assets = Column(Text, nullable=False)  # JSON字符串
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class BacktestResult(Base):
    __tablename__ = "backtest_results"
    
    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, nullable=False)
    config = Column(Text, nullable=False)  # JSON字符串
    result = Column(Text, nullable=False)  # JSON字符串
    created_at = Column(DateTime, default=datetime.utcnow)
```

## 技术栈选择

### 后端框架
- **FastAPI**: 现代、快速的Web框架
- **SQLAlchemy**: ORM映射
- **Jinja2**: 模板引擎
- **Pandas**: 数据处理
- **yfinance**: 股票数据

### 前端技术
- **HTML5 + CSS3**: 页面结构和样式
- **JavaScript (Vanilla)**: 交互逻辑
- **Chart.js**: 图表绘制
- **Bootstrap**: UI组件库

### 数据存储
- **SQLite**: 轻量级数据库
- **文件缓存**: 股票数据缓存

## 优势分析

### 1. 开发效率
- 单一技术栈，减少学习成本
- 统一的部署流程
- 简化的调试过程

### 2. 部署简便
- 单一应用包
- 无需配置反向代理
- 减少服务器资源消耗

### 3. 维护成本
- 代码集中管理
- 统一的错误处理
- 简化的监控体系

### 4. 性能优化
- 减少网络请求
- 服务器端渲染
- 本地缓存策略

## 扩展规划

如果未来需要扩展，可以考虑：

1. **微服务拆分**: 将计算引擎独立为服务
2. **前后端分离**: 增加React前端
3. **分布式缓存**: 使用Redis替代本地缓存
4. **负载均衡**: 多实例部署