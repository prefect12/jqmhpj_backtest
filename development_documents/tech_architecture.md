# 技术架构文档

## 项目架构概览

```
┌─────────────────┐    HTTP API    ┌─────────────────┐
│   React 前端    │ ◄──────────── │  Python 后端    │
│                 │               │                 │
│  - TypeScript   │               │  - FastAPI      │
│  - Chart.js     │               │  - Pandas       │
│  - Axios        │               │  - NumPy        │
└─────────────────┘               │  - yfinance     │
                                  └─────────────────┘
                                           │
                                           ▼
                                  ┌─────────────────┐
                                  │   SQLite 数据库  │
                                  │                 │
                                  │ - 配置缓存      │
                                  │ - 历史数据      │
                                  └─────────────────┘
```

## 后端架构 (Python)

### 核心技术栈
- **Web框架**: FastAPI
  - 自动API文档生成
  - 类型安全
  - 高性能异步处理
  - 现代Python特性支持

- **数据处理**: 
  - **Pandas**: 时间序列数据处理、财务计算
  - **NumPy**: 数值计算、统计分析
  - **yfinance**: Yahoo Finance数据获取

- **数据存储**: SQLite
  - 轻量级、无需配置
  - 适合MVP开发阶段

### 后端模块设计

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI应用入口
│   ├── models/              # 数据模型
│   │   ├── __init__.py
│   │   ├── portfolio.py     # 投资组合模型
│   │   └── backtest.py      # 回测结果模型
│   ├── services/            # 业务逻辑
│   │   ├── __init__.py
│   │   ├── data_service.py  # 数据获取服务
│   │   ├── backtest_service.py # 回测计算服务
│   │   └── portfolio_service.py # 投资组合服务
│   ├── api/                 # API路由
│   │   ├── __init__.py
│   │   ├── portfolio.py     # 投资组合相关API
│   │   └── backtest.py      # 回测相关API
│   ├── core/                # 核心配置
│   │   ├── __init__.py
│   │   ├── config.py        # 应用配置
│   │   └── database.py      # 数据库配置
│   └── utils/               # 工具函数
│       ├── __init__.py
│       ├── calculations.py  # 财务计算工具
│       └── validators.py    # 数据验证工具
├── requirements.txt
└── .env
```

### 核心API设计

```python
# 投资组合配置API
POST /api/portfolio/create
GET  /api/portfolio/{portfolio_id}
PUT  /api/portfolio/{portfolio_id}

# 回测API  
POST /api/backtest/run
GET  /api/backtest/result/{backtest_id}

# 数据API
GET  /api/data/stock/{symbol}
GET  /api/data/search/{query}
```

## 前端架构 (React)

### 核心技术栈
- **框架**: React 18 + TypeScript
  - 组件化开发
  - 类型安全
  - 现代React Hooks

- **状态管理**: React Context + useReducer
  - 轻量级状态管理
  - 适合MVP规模

- **HTTP客户端**: Axios
  - Promise based
  - 请求/响应拦截器
  - 错误处理

- **图表库**: Chart.js + react-chartjs-2
  - 丰富的图表类型
  - 响应式设计
  - 易于定制

### 前端目录结构

```
frontend/
├── public/
├── src/
│   ├── components/          # 可复用组件
│   │   ├── common/          # 通用组件
│   │   ├── charts/          # 图表组件
│   │   └── forms/           # 表单组件
│   ├── pages/               # 页面组件
│   │   ├── Portfolio.tsx    # 投资组合配置页
│   │   └── Backtest.tsx     # 回测结果页
│   ├── services/            # API服务
│   │   ├── api.ts           # API客户端配置
│   │   ├── portfolioApi.ts  # 投资组合API
│   │   └── backtestApi.ts   # 回测API
│   ├── types/               # TypeScript类型定义
│   │   ├── portfolio.ts
│   │   └── backtest.ts
│   ├── utils/               # 工具函数
│   │   ├── formatters.ts    # 数据格式化
│   │   └── validators.ts    # 表单验证
│   ├── hooks/               # 自定义Hooks
│   │   ├── usePortfolio.ts
│   │   └── useBacktest.ts
│   ├── context/             # React Context
│   │   └── AppContext.tsx
│   ├── App.tsx
│   └── index.tsx
├── package.json
└── tsconfig.json
```

## 数据流架构

### 典型用户流程
1. **配置投资组合**: 用户在前端输入股票代码和权重
2. **数据验证**: 前端验证输入，后端验证股票代码有效性
3. **数据获取**: 后端通过yfinance获取历史价格数据
4. **回测计算**: 后端计算投资组合表现指标
5. **结果展示**: 前端接收结果并生成图表和统计表

### 数据模型示例

```typescript
// 前端类型定义
interface Portfolio {
  id: string;
  name: string;
  assets: Array<{
    symbol: string;
    weight: number;
  }>;
  startDate: string;
  endDate: string;
  initialAmount: number;
}

interface BacktestResult {
  portfolioId: string;
  performance: {
    totalReturn: number;
    annualizedReturn: number;
    volatility: number;
    maxDrawdown: number;
    sharpeRatio: number;
  };
  timeSeries: Array<{
    date: string;
    value: number;
  }>;
  yearlyReturns: Array<{
    year: number;
    return: number;
  }>;
}
```

## 开发环境配置

### 后端环境
```bash
# Python虚拟环境
source /Users/kadewu/Documents/pythons/backtest_env/bin/activate

# 依赖安装
pip install fastapi uvicorn pandas numpy yfinance sqlalchemy

# 运行开发服务器
uvicorn app.main:app --reload --port 8000
```

### 前端环境
```bash
# 创建React应用
npx create-react-app frontend --template typescript

# 安装依赖
npm install axios chart.js react-chartjs-2

# 运行开发服务器  
npm start
```

## 部署架构
- **开发阶段**: 本地开发，前后端分离
- **生产阶段**: Docker容器化部署（后续规划）