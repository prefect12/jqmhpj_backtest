# 定投计划功能规范文档

## 1. 功能概述

定投计划（Dollar Cost Averaging, DCA）是一种投资策略，通过定期或按条件投入固定或变动金额，以降低市场波动风险，实现长期稳健投资。

## 2. 定期定投功能

### 2.1 投资频率设置
```json
{
  "frequency_type": "monthly|weekly|daily|biweekly|custom",
  "frequency_config": {
    "monthly": {
      "day_of_month": 1,  // 1-31, 或 "last"
      "months": [1,2,3,4,5,6,7,8,9,10,11,12]  // 可选择特定月份
    },
    "weekly": {
      "day_of_week": 1,  // 1-7 (周一到周日)
      "weeks_interval": 1  // 每N周
    },
    "daily": {
      "trading_days_only": true,
      "days_interval": 1  // 每N天
    },
    "biweekly": {
      "start_date": "2024-01-01",
      "day_of_week": 1
    },
    "custom": {
      "dates": ["2024-01-15", "2024-02-15", "2024-03-15"]
    }
  }
}
```

### 2.2 投资金额配置
```json
{
  "amount_type": "fixed|percentage|progressive",
  "amount_config": {
    "fixed": {
      "amount": 1000.00,
      "currency": "USD"
    },
    "percentage": {
      "base_amount": 10000.00,
      "percentage": 10.0,  // 每次投入基础金额的10%
      "recalculate": "monthly"  // 重新计算频率
    },
    "progressive": {
      "initial_amount": 1000.00,
      "increment_type": "fixed|percentage",
      "increment_value": 100.00,  // 每次增加100
      "max_amount": 5000.00  // 最大单次投入
    }
  }
}
```

## 3. 条件定投功能

### 3.1 市场条件触发
```json
{
  "condition_type": "price_drop|drawdown|valuation|technical|composite",
  "conditions": [
    {
      "type": "price_drop",
      "config": {
        "drop_percentage": 3.0,  // 单日下跌3%
        "reference": "previous_close",  // 参考价格
        "cooldown_days": 7,  // 触发后冷却期
        "amount_multiplier": 1.5  // 触发时投入金额倍数
      }
    },
    {
      "type": "drawdown",
      "config": {
        "drawdown_threshold": 10.0,  // 从高点回撤10%
        "lookback_days": 252,  // 回看天数
        "trigger_once": false,  // 是否只触发一次
        "amount_formula": "base * (1 + drawdown_pct/100)"
      }
    },
    {
      "type": "valuation",
      "config": {
        "indicator": "PE|PB|PS",
        "threshold_type": "absolute|percentile",
        "threshold_value": 15.0,  // PE < 15
        "historical_period": "5Y",  // 历史数据周期
        "comparison": "less_than"
      }
    },
    {
      "type": "technical",
      "config": {
        "indicator": "RSI|MACD|MA",
        "rsi_config": {
          "period": 14,
          "oversold_threshold": 30,
          "overbought_threshold": 70
        },
        "ma_config": {
          "short_period": 50,
          "long_period": 200,
          "signal": "golden_cross|death_cross"
        }
      }
    }
  ],
  "combination_logic": "AND|OR",  // 多条件组合逻辑
  "priority_order": [1, 2, 3]  // 条件优先级
}
```

### 3.2 条件定投执行规则
```json
{
  "execution_rules": {
    "max_triggers_per_month": 5,  // 每月最大触发次数
    "min_interval_days": 3,  // 最小触发间隔
    "total_investment_limit": 50000.00,  // 总投入上限
    "single_investment_limit": 5000.00,  // 单次投入上限
    "cash_reserve": 1000.00,  // 保留现金
    "insufficient_funds_action": "skip|partial|borrow"
  }
}
```

## 4. 投资组合配置模型

### 4.1 完整配置参数（参考Portfolio Visualizer）
```json
{
  "portfolio_config": {
    "assets": [
      {
        "symbol": "AAPL",
        "initial_weight": 40.0,
        "target_weight": 40.0,
        "min_weight": 30.0,
        "max_weight": 50.0
      }
    ],
    "time_period": {
      "start_year": 1985,
      "end_year": 2025,
      "include_ytd": false
    },
    "initial_amount": 10000.00,
    "cashflows": {
      "type": "none|periodic|conditional",
      "periodic_config": {
        // 定期定投配置
      },
      "conditional_config": {
        // 条件定投配置
      }
    },
    "rebalancing": {
      "frequency": "none|monthly|quarterly|annually",
      "threshold": 5.0,  // 偏离阈值触发再平衡
      "method": "target_weight|equal_weight"
    },
    "leverage": {
      "type": "none|fixed|dynamic",
      "ratio": 1.0
    },
    "dividends": {
      "reinvest": true,
      "tax_rate": 0.0
    },
    "display_options": {
      "show_income": true,
      "show_cashflows": true,
      "show_rebalancing": true
    }
  }
}
```

## 5. 回测计算逻辑

### 5.1 定期定投计算流程
```python
def calculate_dca_investment(portfolio, config):
    """
    定期定投回测计算
    """
    results = []
    total_invested = initial_amount
    current_shares = {}
    
    for date in trading_dates:
        # 检查是否是定投日
        if is_investment_day(date, config.frequency):
            # 计算投入金额
            investment_amount = calculate_investment_amount(date, config)
            
            # 按权重分配到各资产
            for asset in portfolio.assets:
                asset_amount = investment_amount * asset.weight
                shares = asset_amount / get_price(asset.symbol, date)
                current_shares[asset.symbol] += shares
            
            total_invested += investment_amount
        
        # 计算当前组合价值
        portfolio_value = calculate_portfolio_value(current_shares, date)
        
        # 记录结果
        results.append({
            'date': date,
            'invested': total_invested,
            'value': portfolio_value,
            'return': (portfolio_value - total_invested) / total_invested
        })
    
    return results
```

### 5.2 条件定投计算流程
```python
def calculate_conditional_dca(portfolio, config):
    """
    条件定投回测计算
    """
    results = []
    triggers = []
    last_trigger_date = None
    
    for date in trading_dates:
        # 检查所有条件
        for condition in config.conditions:
            if check_condition(condition, date, market_data):
                # 检查冷却期
                if can_trigger(date, last_trigger_date, condition.cooldown):
                    # 执行定投
                    amount = calculate_conditional_amount(condition, market_data)
                    execute_investment(portfolio, amount, date)
                    
                    triggers.append({
                        'date': date,
                        'condition': condition.type,
                        'amount': amount,
                        'trigger_value': get_trigger_value(condition, date)
                    })
                    
                    last_trigger_date = date
        
        # 记录每日结果
        results.append(calculate_daily_result(portfolio, date))
    
    return results, triggers
```

## 6. 统计指标计算

### 6.1 定投专属指标
```python
# 平均成本
average_cost = total_invested / total_shares

# 成本收益率
cost_return = (current_value - total_invested) / total_invested

# 内部收益率 (IRR)
irr = calculate_irr(cashflows, final_value)

# 投资效率
investment_efficiency = actual_return / buy_and_hold_return

# 定投改善率
dca_improvement = (dca_return - lump_sum_return) / lump_sum_return
```

### 6.2 风险调整指标
```python
# 调整后夏普比率（考虑现金流）
modified_sharpe = (portfolio_return - risk_free_rate) / portfolio_volatility

# 卡尔马比率
calmar_ratio = annualized_return / max_drawdown

# 信息比率
information_ratio = active_return / tracking_error
```

## 7. 用户界面设计

### 7.1 定投配置界面
- **基础设置区**
  - 投资频率选择（下拉菜单）
  - 投资金额输入
  - 起止日期选择
  
- **高级设置区**（可折叠）
  - 条件定投规则配置
  - 再平衡策略设置
  - 现金管理规则
  
- **预览区**
  - 显示预计投资计划
  - 估算总投入金额
  - 投资日历展示

### 7.2 结果展示增强
- **定投统计卡片**
  - 总投入 vs 当前价值
  - 平均成本 vs 当前价格
  - 定投次数和频率
  - IRR内部收益率
  
- **定投时间线图表**
  - 显示每次投入的时间和金额
  - 标记条件触发点
  - 成本线vs价值线对比

## 8. 数据结构设计

### 8.1 数据库表结构
```sql
-- 定投计划表
CREATE TABLE dca_plans (
    id INTEGER PRIMARY KEY,
    portfolio_id VARCHAR(50),
    plan_type VARCHAR(20),  -- periodic/conditional
    frequency VARCHAR(20),
    amount DECIMAL(10,2),
    start_date DATE,
    end_date DATE,
    config JSON,
    created_at TIMESTAMP
);

-- 定投执行记录表
CREATE TABLE dca_executions (
    id INTEGER PRIMARY KEY,
    plan_id INTEGER,
    execution_date DATE,
    amount DECIMAL(10,2),
    trigger_condition VARCHAR(50),
    portfolio_value DECIMAL(10,2),
    total_invested DECIMAL(10,2),
    FOREIGN KEY (plan_id) REFERENCES dca_plans(id)
);

-- 条件触发记录表
CREATE TABLE condition_triggers (
    id INTEGER PRIMARY KEY,
    plan_id INTEGER,
    trigger_date DATE,
    condition_type VARCHAR(50),
    trigger_value DECIMAL(10,4),
    threshold_value DECIMAL(10,4),
    executed BOOLEAN,
    FOREIGN KEY (plan_id) REFERENCES dca_plans(id)
);
```

## 9. API接口设计

### 9.1 定投计划管理
```python
# 创建定投计划
POST /api/dca/plans
{
    "portfolio_id": "port_123",
    "type": "periodic",
    "config": {...}
}

# 获取定投计划
GET /api/dca/plans/{plan_id}

# 更新定投计划
PUT /api/dca/plans/{plan_id}

# 删除定投计划
DELETE /api/dca/plans/{plan_id}
```

### 9.2 定投回测执行
```python
# 执行定投回测
POST /api/dca/backtest
{
    "portfolio": {...},
    "dca_config": {...},
    "time_period": {...}
}

# 获取回测结果
GET /api/dca/backtest/{backtest_id}

# 导出定投记录
GET /api/dca/backtest/{backtest_id}/export
```

## 10. 测试要求

### 10.1 单元测试
- 定投日期计算准确性
- 金额计算逻辑正确性
- 条件触发判断准确性
- IRR计算准确性

### 10.2 集成测试
- 完整定投流程测试
- 多条件组合测试
- 极端市场情况测试
- 性能压力测试

### 10.3 测试用例示例
```python
def test_monthly_dca():
    """测试月度定投"""
    config = {
        "frequency": "monthly",
        "day": 1,
        "amount": 1000
    }
    result = calculate_dca(portfolio, config)
    assert result.total_invested == 12000  # 12个月
    assert len(result.executions) == 12

def test_price_drop_trigger():
    """测试价格下跌触发"""
    config = {
        "type": "price_drop",
        "threshold": 3.0,
        "amount": 2000
    }
    # 模拟3%下跌
    market_data = create_mock_drop_data(3.0)
    result = check_condition(config, market_data)
    assert result.triggered == True
```

## 11. 注意事项

1. **数据完整性**：确保历史数据连续，处理节假日和停牌情况
2. **计算精度**：金额计算保留2位小数，百分比保留4位小数
3. **性能优化**：大量历史数据时采用增量计算
4. **用户体验**：提供清晰的投资计划预览和执行反馈
5. **风险提示**：明确提示历史表现不代表未来收益