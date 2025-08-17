# API接口规范

## 接口概览

本文档定义了回测系统的REST API接口规范，包括请求格式、响应格式和错误处理。

## 基础信息

- **Base URL**: `http://localhost:8000/api`
- **Content-Type**: `application/json`
- **字符编码**: UTF-8

## 接口列表

### 1. 创建投资组合

**POST** `/portfolio/create`

创建新的投资组合配置。

#### 请求体
```json
{
  "name": "我的投资组合",
  "assets": [
    {
      "symbol": "AAPL",
      "weight": 30.0
    },
    {
      "symbol": "MSFT",
      "weight": 25.0
    },
    {
      "symbol": "GOOGL", 
      "weight": 20.0
    },
    {
      "symbol": "TSLA",
      "weight": 15.0
    },
    {
      "symbol": "NVDA",
      "weight": 10.0
    }
  ]
}
```

#### 响应
```json
{
  "success": true,
  "data": {
    "portfolio_id": "port_123456",
    "name": "我的投资组合",
    "assets": [
      {
        "symbol": "AAPL",
        "weight": 30.0,
        "name": "Apple Inc.",
        "current_price": 185.25,
        "currency": "USD"
      }
      // ... 其他资产
    ],
    "total_weight": 100.0,
    "created_at": "2024-08-16T10:30:00Z"
  }
}
```

### 2. 运行回测

**POST** `/backtest/run`

执行投资组合回测计算。

#### 请求体
```json
{
  "portfolio_id": "port_123456",
  "config": {
    "start_date": "2020-01-01",
    "end_date": "2024-12-31", 
    "initial_amount": 10000.00,
    "rebalance_frequency": "quarterly",
    "reinvest_dividends": true
  }
}
```

#### 响应
```json
{
  "success": true,
  "data": {
    "backtest_id": "bt_789012",
    "status": "processing",
    "estimated_completion_time": "2024-08-16T10:32:00Z",
    "message": "回测计算已开始，预计2分钟完成"
  }
}
```

### 3. 获取回测结果

**GET** `/backtest/result/{backtest_id}`

获取回测计算结果。

#### 路径参数
- `backtest_id`: 回测任务ID

#### 响应 (成功)
```json
{
  "success": true,
  "data": {
    "backtest_id": "bt_789012",
    "status": "completed",
    "result": {
      // 完整的回测结果数据（参考mvp_definition.md中的输出结构）
    }
  }
}
```

#### 响应 (处理中)
```json
{
  "success": true,
  "data": {
    "backtest_id": "bt_789012", 
    "status": "processing",
    "progress": 65,
    "estimated_remaining_time": 30
  }
}
```

### 4. 股票搜索

**GET** `/data/search?query={query}`

搜索股票代码和公司名称。

#### 查询参数
- `query`: 搜索关键词 (股票代码或公司名称)
- `limit`: 返回结果数量限制 (默认10，最大50)

#### 请求示例
```
GET /data/search?query=apple&limit=5
```

#### 响应
```json
{
  "success": true,
  "data": [
    {
      "symbol": "AAPL",
      "name": "Apple Inc.",
      "exchange": "NASDAQ",
      "currency": "USD",
      "market_cap": 2800000000000,
      "sector": "Technology"
    },
    {
      "symbol": "APLE", 
      "name": "Apple Hospitality REIT Inc.",
      "exchange": "NYSE",
      "currency": "USD",
      "market_cap": 3200000000,
      "sector": "Real Estate"
    }
  ]
}
```

### 5. 获取股票基本信息

**GET** `/data/stock/{symbol}`

获取单个股票的详细信息。

#### 路径参数
- `symbol`: 股票代码

#### 响应
```json
{
  "success": true,
  "data": {
    "symbol": "AAPL",
    "name": "Apple Inc.",
    "exchange": "NASDAQ",
    "currency": "USD",
    "current_price": 185.25,
    "market_cap": 2847562000000,
    "pe_ratio": 28.45,
    "dividend_yield": 0.52,
    "sector": "Technology",
    "industry": "Consumer Electronics",
    "description": "Apple Inc. designs, manufactures, and markets...",
    "data_available_from": "1980-12-12",
    "last_updated": "2024-08-16T16:00:00Z"
  }
}
```

### 6. 获取投资组合列表

**GET** `/portfolio/list`

获取用户的投资组合列表。

#### 响应
```json
{
  "success": true,
  "data": [
    {
      "portfolio_id": "port_123456",
      "name": "我的投资组合",
      "asset_count": 5,
      "total_weight": 100.0,
      "created_at": "2024-08-16T10:30:00Z",
      "last_backtest": "2024-08-16T10:45:00Z"
    },
    {
      "portfolio_id": "port_789012", 
      "name": "科技股组合",
      "asset_count": 3,
      "total_weight": 100.0,
      "created_at": "2024-08-15T14:20:00Z",
      "last_backtest": null
    }
  ]
}
```

## 错误处理

### 错误响应格式
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "投资组合权重总和必须等于100%",
    "details": {
      "field": "assets.weight",
      "current_total": 95.0,
      "expected_total": 100.0
    }
  }
}
```

### 错误代码定义

| 错误代码 | HTTP状态码 | 描述 |
|---------|-----------|------|
| `VALIDATION_ERROR` | 400 | 输入参数验证失败 |
| `INVALID_SYMBOL` | 400 | 无效的股票代码 |
| `INSUFFICIENT_DATA` | 400 | 股票历史数据不足 |
| `PORTFOLIO_NOT_FOUND` | 404 | 投资组合不存在 |
| `BACKTEST_NOT_FOUND` | 404 | 回测任务不存在 |
| `CALCULATION_ERROR` | 500 | 回测计算错误 |
| `DATA_SOURCE_ERROR` | 502 | 数据源访问失败 |
| `RATE_LIMIT_EXCEEDED` | 429 | 请求频率超限 |

### 常见错误示例

#### 1. 权重验证错误
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "投资组合权重总和必须等于100%",
    "details": {
      "current_total": 95.0,
      "expected_total": 100.0
    }
  }
}
```

#### 2. 股票代码无效
```json
{
  "success": false,
  "error": {
    "code": "INVALID_SYMBOL", 
    "message": "股票代码 'INVALID' 不存在或不支持",
    "details": {
      "symbol": "INVALID",
      "suggestion": "请检查股票代码是否正确"
    }
  }
}
```

#### 3. 历史数据不足
```json
{
  "success": false,
  "error": {
    "code": "INSUFFICIENT_DATA",
    "message": "股票 'TSLA' 在指定时间范围内数据不足",
    "details": {
      "symbol": "TSLA",
      "requested_start": "2010-01-01",
      "data_available_from": "2010-06-29", 
      "suggestion": "请调整开始日期到2010-06-29之后"
    }
  }
}
```

## 请求限制

### 频率限制
- **创建投资组合**: 100次/小时
- **运行回测**: 50次/小时  
- **获取结果**: 1000次/小时
- **股票搜索**: 300次/小时

### 数据限制
- **投资组合资产数量**: 最多5只
- **回测时间范围**: 最长5年
- **初始投资金额**: $1,000 - $1,000,000
- **搜索结果**: 最多50条

## 认证和安全

### 当前版本 (MVP)
- 暂无用户认证
- 基于IP的频率限制
- 基础输入验证和清理

### 未来版本规划
- JWT token认证
- 用户账户系统
- 高级权限控制
- API密钥管理

## 版本控制

当前版本: `v1`

版本在URL路径中体现: `/api/v1/portfolio/create`

向后兼容性保证：
- 现有字段不会删除
- 响应格式保持稳定
- 新功能通过新字段添加