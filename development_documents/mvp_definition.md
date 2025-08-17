

## 回测系统输入输出定义

### 回测输入 (Input)

#### 1. 投资组合配置
```json
{
  "portfolio": {
    "name": "我的投资组合",
    "assets": [
      {
        "symbol": "AAPL",
        "weight": 30.0,
        "name": "Apple Inc."
      },
      {
        "symbol": "MSFT", 
        "weight": 25.0,
        "name": "Microsoft Corp."
      },
      {
        "symbol": "GOOGL",
        "weight": 20.0,
        "name": "Alphabet Inc."
      },
      {
        "symbol": "TSLA",
        "weight": 15.0,
        "name": "Tesla Inc."
      },
      {
        "symbol": "NVDA",
        "weight": 10.0,
        "name": "NVIDIA Corp."
      }
    ]
  }
}
```

#### 2. 回测参数
```json
{
  "backtest_config": {
    "start_date": "2020-01-01",
    "end_date": "2024-12-31",
    "initial_amount": 10000.00,
    "rebalance_frequency": "quarterly",
    "reinvest_dividends": true,
    "currency": "USD"
  }
}
```

#### 3. 输入验证规则
- **股票代码**: 必须是有效的股票代码，支持美股市场
- **权重**: 总和必须等于100%，单个权重范围0-100%
- **时间范围**: 开始日期 < 结束日期，最长回测期间5年
- **初始金额**: 最小$1,000，最大$1,000,000
- **再平衡频率**: monthly/quarterly/annually/none

### 回测输出 (Output)

#### 完整输出数据结构 (基于Portfolio Visualizer)
```json
{
  "backtest_result": {
    "metadata": {
      "portfolio_id": "port_123456",
      "backtest_id": "bt_789012",
      "created_at": "2024-08-16T10:30:00Z",
      "status": "completed",
      "calculation_time_ms": 1250
    },
    
    "input_summary": {
      "start_date": "2020-01-01",
      "end_date": "2024-12-31",
      "duration_years": 5.0,
      "initial_amount": 10000.00,
      "total_assets": 5,
      "rebalance_frequency": "quarterly"
    },
    
    "performance_summary": {
      "start_value": 10000.00,
      "end_value": 18345.67,
      "total_return_pct": 83.46,
      "annualized_return_pct": 12.88,
      "best_year": {
        "year": 2023,
        "return_pct": 35.24
      },
      "worst_year": {
        "year": 2022,
        "return_pct": -18.75
      }
    },
    
    "risk_metrics": {
      "volatility_annual_pct": 24.15,
      "max_drawdown_pct": -32.45,
      "max_drawdown_period": {
        "start_date": "2022-01-03",
        "end_date": "2022-10-12", 
        "duration_days": 283
      },
      "sharpe_ratio": 0.53,
      "sortino_ratio": 0.74,
      "positive_months": 38,
      "total_months": 60,
      "positive_rate_pct": 63.33
    },
    
    "portfolio_return_decomposition": [
      {
        "symbol": "AAPL",
        "name": "Apple Inc.",
        "final_value": 5894.32
      },
      {
        "symbol": "MSFT", 
        "name": "Microsoft Corp.",
        "final_value": 4523.18
      }
      // ... 其他资产
    ],
    
    "portfolio_risk_decomposition": [
      {
        "symbol": "AAPL",
        "name": "Apple Inc.", 
        "risk_contribution_pct": 32.12
      },
      {
        "symbol": "MSFT",
        "name": "Microsoft Corp.",
        "risk_contribution_pct": 24.66
      }
      // ... 其他资产
    ],
    
    "portfolio_assets": [
      {
        "symbol": "AAPL",
        "name": "Apple Inc.",
        "cagr_pct": 15.25,
        "volatility_pct": 28.45,
        "best_year_pct": 42.35,
        "worst_year_pct": -35.24,
        "max_drawdown_pct": -45.67,
        "sharpe_ratio": 0.54,
        "sortino_ratio": 0.78
      }
      // ... 其他资产详细指标
    ],
    
    "portfolio_asset_performance": [
      {
        "symbol": "AAPL",
        "name": "Apple Inc.",
        "total_return": {
          "3_month_pct": 14.26,
          "ytd_pct": 7.98,
          "1_year_pct": 15.49,
          "3_year_pct": 16.27,
          "5_year_pct": 14.99,
          "10_year_pct": 12.85
        },
        "annualized_return": {
          "3_year_pct": 16.27,
          "5_year_pct": 14.99
        },
        "expense_ratio": {
          "net_pct": 0.14,
          "gross_pct": 0.14
        }
      }
      // ... 其他资产表现
    ],
    
    "monthly_correlations": {
      "correlation_matrix": [
        ["AAPL", "MSFT", "GOOGL", "TSLA", "Portfolio"],
        ["AAPL", 1.00, 0.85, 0.64, 0.13, 0.96],
        ["MSFT", 0.85, 1.00, 0.61, 0.18, 0.92],
        ["GOOGL", 0.64, 0.61, 1.00, 0.31, 0.76],
        ["TSLA", 0.13, 0.18, 0.31, 1.00, 0.30]
      ]
    },
    
    "rolling_returns": {
      "summary": [
        {
          "period": "1 year",
          "portfolio_avg_pct": 7.89,
          "portfolio_high_pct": 44.58,
          "portfolio_low_pct": -33.58
        },
        {
          "period": "3 years", 
          "portfolio_avg_pct": 6.89,
          "portfolio_high_pct": 21.27,
          "portfolio_low_pct": -9.22
        },
        {
          "period": "5 years",
          "portfolio_avg_pct": 6.93,
          "portfolio_high_pct": 17.40,
          "portfolio_low_pct": -1.79
        }
      ],
      "time_series_3_year": [
        {
          "date": "2003-01-01",
          "portfolio_return_pct": 15.67
        }
        // ... 3年滚动收益率时间序列
      ],
      "time_series_5_year": [
        {
          "date": "2005-01-01", 
          "portfolio_return_pct": 12.45
        }
        // ... 5年滚动收益率时间序列
      ]
    },
    
    "annual_asset_returns": [
      {
        "year": 2024,
        "AAPL_return_pct": 23.61,
        "MSFT_return_pct": 5.09, 
        "GOOGL_return_pct": 4.76,
        "TSLA_return_pct": 1.14
      }
      // ... 每年各资产收益率
    ],
    
    "time_series": [
      {
        "date": "2020-01-01",
        "portfolio_value": 10000.00,
        "daily_return_pct": 0.0,
        "cumulative_return_pct": 0.0
      }
      // ... 每日数据
    ],
    
    "annual_returns": [
      {
        "year": 2020,
        "start_value": 10000.00,
        "end_value": 11567.89,
        "annual_return_pct": 15.68,
        "volatility_pct": 28.45
      }
      // ... 每年数据
    ],
    
    "drawdown_periods": [
      {
        "rank": 1,
        "start_date": "2022-01-03",
        "trough_date": "2022-10-12",
        "end_date": "2023-03-15",
        "drawdown_pct": -32.45,
        "duration_days": 283,
        "recovery_days": 154
      }
      // ... 最大的10次回撤
    ],
    
    "drawdown_chart_data": [
      {
        "date": "2020-01-01",
        "portfolio_drawdown_pct": 0.0
      },
      {
        "date": "2020-01-02",
        "portfolio_drawdown_pct": -1.25
      }
      // ... 每日回撤数据用于绘制回撤图
    ]
  }
}
```

## MVP回测结果范围

基于Portfolio Visualizer实际界面分析，MVP版本应包含以下核心展示模块：

### 1. Highlights摘要卡片 (必须)
顶部展示两个关键指标卡片：

```
┌─────────────────────────┬─────────────────────────┐
│        Return           │    Risk                 │
├─────────────────────────┼─────────────────────────┤
│ Annualized Return       │ Volatility & Drawdown  │
│ Portfolio Return: 7.5%  │ Std Dev: 11.0%         │
│ Benchmark Relative: -2.2%│ Max Drawdown: 39.6%    │
└─────────────────────────┴─────────────────────────┘
```

### 2. Performance Summary表格 (必须)
完整的性能统计对比：

```
Performance Summary
─────────────────────────────────────────────────────
Metric                    Portfolio 1    Benchmark
─────────────────────────────────────────────────────
Start Balance             $10,000        $10,000
End Balance               $78,316        $139,602
Annualized Return (CAGR)  7.47%          9.66%
Standard Deviation        10.96%         15.48%
Best Year                 25.37%         33.19%
Worst Year                -25.82%        -37.02%
Maximum Drawdown          -39.59%        -50.97%
Sharpe Ratio             0.51           0.53
Sortino Ratio            0.74           0.78
Benchmark Correlation    0.95           1.00
─────────────────────────────────────────────────────
```

### 3. Portfolio Growth图表 (必须)
展示投资组合价值增长曲线，带基准对比：
- 主线：Portfolio价值变化（蓝色）
- 对比线：Benchmark价值变化（绿色）
- 支持对数刻度和通胀调整选项
- 显示关键事件标记

### 4. Annual Returns表格 (必须)
年度收益详细数据，包含：

```
Annual Returns
─────────────────────────────────────────────────────────────────
Year  Inflation  Portfolio 1         Benchmark    各资产收益率
                Return  Balance  Yield  Income   Return  Balance  
─────────────────────────────────────────────────────────────────
2025  2.36%     7.92%   $78,316  1.33%  $964    8.49%   $139,602
2024  2.89%     11.28%  $72,566  2.69%  $1,752  24.84%  $128,673
2023  3.35%     16.28%  $65,212  2.73%  $1,529  26.11%  $103,069
2022  6.45%     -17.66% $56,079  1.89%  $1,287  -18.23% $81,728
...
─────────────────────────────────────────────────────────────────
```

### 5. Drawdowns分析 (必须)
包含历史压力测试期间和最大回撤排名：

```
Historical Market Stress Periods
─────────────────────────────────────────────────────
Stress Period         Start      End        Portfolio  Benchmark
─────────────────────────────────────────────────────
Asian Crisis          Jul 1997   Jan 1998   -3.61%    -5.61%
Russian Debt Default  Jul 1998   Oct 1998   -10.77%   -15.38%
Dotcom Crash         Mar 2000   Oct 2002   -20.74%   -44.82%
Subprime Crisis      Nov 2007   Mar 2009   -39.59%   -50.97%
COVID-19 Start       Jan 2020   Mar 2020   -14.71%   -19.63%

Top 10 Drawdowns
─────────────────────────────────────────────────────────────────
Rank  Start     End       Duration  Recovery  Underwater  Drawdown
1     Nov 2007  Feb 2009  16 mo     23 mo     39 mo      -39.59%
2     Jan 2022  Sep 2022  9 mo      18 mo     27 mo      -22.67%
...
```

### 6. Risk and Return Metrics表格 (必须)
详细的风险收益指标：

```
Risk and Return Metrics
─────────────────────────────────────────────────────
Metric                        Portfolio 1   Benchmark
─────────────────────────────────────────────────────
Arithmetic Mean (monthly)     0.65%        0.87%
Geometric Mean (annualized)   7.47%        9.66%
Standard Deviation           10.96%        15.48%
Downside Deviation           2.12%         2.97%
Maximum Drawdown            -39.59%       -50.97%
Beta                        0.67          1.00
Alpha (annualized)          0.80%         -0.00%
Sharpe Ratio               0.51          0.53
Sortino Ratio              0.74          0.78
Calmar Ratio               0.83          1.31
Information Ratio          -0.36         N/A
Upside Capture Ratio       67.87%        100.00%
Downside Capture Ratio     68.23%        100.00%
─────────────────────────────────────────────────────
```

### 7. Portfolio Assets分析 (必须)
各资产独立表现和贡献分解：

```
Portfolio Assets Performance
─────────────────────────────────────────────────────────────
Ticker  Name     CAGR    Stdev   Best    Worst   Max DD  Sharpe
─────────────────────────────────────────────────────────────
VTSMX   US Stock 9.65%   15.92%  33.35%  -37.04% -50.89% 0.52
VGTSX   Intl     5.32%   16.99%  40.34%  -44.10% -58.50% 0.26
VGSIX   REIT     8.08%   19.92%  40.19%  -37.05% -68.28% 0.38
VBMFX   Bond     3.99%   4.12%   11.39%  -13.25% -17.57% 0.44

Portfolio Return Decomposition
─────────────────────────────────────────────────────────────
Ticker  Contribution($)  Contribution(%)
VTSMX   $42,000         54.93%
VGTSX   $11,781         28.13%
VGSIX   $7,100          13.65%
VBMFX   $7,435          3.30%

Portfolio Risk Decomposition
─────────────────────────────────────────────────────────────
Ticker  Risk Contribution
VTSMX   54.93%
VGTSX   28.13%
VGSIX   13.65%
VBMFX   3.30%
```

### 8. Rolling Returns分析 (推荐)
滚动收益率统计和图表：

```
Rolling Returns Summary
─────────────────────────────────────────────────────────────
Roll Period   Portfolio 1                 Benchmark
             Average  High    Low        Average  High    Low
─────────────────────────────────────────────────────────────
1 year       7.89%   44.58%  -33.58%    10.51%   56.19%  -43.32%
3 years      6.89%   21.27%  -9.22%     8.43%    27.53%  -16.14%
5 years      6.93%   17.40%  -1.79%     8.10%    22.85%  -6.73%
10 years     7.03%   11.62%  1.74%      8.16%    16.52%  -3.51%
```

包含3年和5年滚动收益率时间序列图表

## MVP功能边界

### 包含功能 ✅
1. **基础投资组合配置**
   - 最多5只股票
   - 权重分配 (总和=100%)
   - 时间范围选择 (最长5年)

2. **核心回测计算**
   - 净值计算
   - 收益率计算 (总收益、年化收益)
   - 风险指标 (波动率、最大回撤、夏普比率)

3. **基础结果展示**
   - 统计摘要表格
   - 投资组合增长曲线图
   - 年度收益柱状图
   - 配置明细表

### 暂不包含 ❌
1. **高级功能**
   - 基准对比
   - 因子分析
   - 风格分析
   - 相关性分析

2. **复杂数据**
   - 月度详细数据
   - 滚动收益分析
   - 历史压力测试

3. **高级图表**
   - 回撤水下图
   - 滚动收益图
   - 多投资组合对比

4. **导出功能**
   - Excel导出
   - PDF报告
   - 数据下载

## 计算公式定义

### 1. 年化收益率 (CAGR)
```
CAGR = (End Value / Start Value)^(1/Years) - 1
```

### 2. 年化波动率
```
σ_annual = σ_daily × √252
```

### 3. 最大回撤
```
Max Drawdown = max(Peak_value - Trough_value) / Peak_value
```

### 4. 夏普比率
```
Sharpe Ratio = (Portfolio Return - Risk Free Rate) / Portfolio Volatility
* Risk Free Rate = 0% (简化版本)
```

### 5. 投资组合净值计算
```python
# 伪代码
portfolio_value[t] = Σ (weight[i] × price[i,t] × shares[i])
daily_return[t] = (portfolio_value[t] - portfolio_value[t-1]) / portfolio_value[t-1]
```

## 数据质量要求

### 股票数据要求
- **频率**: 日频数据
- **字段**: 开盘价、最高价、最低价、收盘价、成交量
- **质量**: 缺失数据 < 5%
- **来源**: Yahoo Finance (yfinance)

### 计算精度要求
- **收益率**: 保留4位小数 (0.0001)
- **金额**: 保留2位小数 ($0.01)
- **百分比**: 保留2位小数 (0.01%)

## 用户体验要求

### 性能要求
- **计算时间**: < 3秒 (5年数据，5只股票)
- **页面加载**: < 2秒
- **图表渲染**: < 1秒

### 界面要求
- **响应式**: 支持桌面端 (1200px+)
- **简洁性**: 一页展示所有核心结果
- **可读性**: 清晰的数据标签和格式化

## 成功标准

MVP版本成功的关键指标：
1. ✅ 能够准确计算5只股票组合的5年回测
2. ✅ 计算结果与主流工具偏差 < 1%
3. ✅ 用户能在30秒内完成一次回测
4. ✅ 结果展示清晰直观，无需额外解释