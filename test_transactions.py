#!/usr/bin/env python
"""
测试增强版回测（包含交易记录）
"""
import json
from app.services.backtest_service_enhanced import EnhancedBacktestService

def test_enhanced_backtest():
    """测试增强版回测功能"""
    
    # 创建服务实例
    service = EnhancedBacktestService()
    
    # 配置回测参数
    config = {
        "assets": [
            {"symbol": "AAPL", "weight": 50},
            {"symbol": "MSFT", "weight": 50}
        ],
        "start_date": "2023-01-01", 
        "end_date": "2023-06-30",
        "initial_amount": 10000,
        "buy_conditions": {
            "daily_drop_threshold": -0.03,  # 3%日跌幅触发
            "drawdown_threshold": -0.05,    # 5%回撤触发
            "rsi_oversold": 35              # RSI < 35触发
        }
    }
    
    print("开始执行增强版回测...")
    print(f"配置: {json.dumps(config, indent=2)}")
    
    # 执行回测
    result = service.run_backtest_with_transactions(config)
    
    # 检查结果
    if result['status'] == 'completed':
        print("\n✅ 回测成功!")
        
        # 显示性能指标
        perf = result['performance_summary']
        print(f"\n📊 性能指标:")
        print(f"  初始金额: ${perf['start_value']:,.2f}")
        print(f"  最终金额: ${perf['end_value']:,.2f}")
        print(f"  总收益率: {perf['total_return_pct']:.2f}%")
        print(f"  年化收益: {perf['annualized_return_pct']:.2f}%")
        
        # 显示风险指标
        risk = result['risk_metrics']
        print(f"\n📉 风险指标:")
        print(f"  波动率: {risk['volatility_annual_pct']:.2f}%")
        print(f"  最大回撤: {risk['max_drawdown_pct']:.2f}%")
        print(f"  夏普比率: {risk['sharpe_ratio']:.2f}")
        
        # 显示交易记录
        transactions = result.get('transactions', [])
        print(f"\n📝 交易记录: 共 {len(transactions)} 笔")
        
        if transactions:
            print("\n最近5笔交易:")
            for i, t in enumerate(transactions[:5], 1):
                print(f"\n  交易 {i}:")
                print(f"    日期: {t['date']}")
                print(f"    股票: {t['symbol']}")
                print(f"    类型: {t['type']}")
                print(f"    数量: {t['shares']:.4f} 股")
                print(f"    价格: ${t['price']:.2f}")
                print(f"    金额: ${t['amount']:.2f}")
                print(f"    原因: {t['reason']}")
                if t.get('details'):
                    print(f"    详情: {t['details']}")
        
        # 显示交易统计
        tx_summary = result.get('transaction_summary', {})
        if tx_summary:
            print(f"\n📈 交易统计:")
            print(f"  总交易次数: {tx_summary.get('total_transactions', 0)}")
            print(f"  买入次数: {tx_summary.get('buy_count', 0)}")
            print(f"  总买入金额: ${tx_summary.get('total_buy_amount', 0):,.2f}")
            
            # 按原因统计
            reason_stats = tx_summary.get('reason_statistics', {})
            if reason_stats:
                print(f"\n  按原因分类:")
                for reason, stats in reason_stats.items():
                    print(f"    {reason}: {stats['count']}次, 总金额 ${stats['total_amount']:,.2f}")
        
        # 保存结果到文件
        with open('enhanced_backtest_result.json', 'w') as f:
            json.dump(result, f, indent=2, default=str)
        print("\n💾 结果已保存到 enhanced_backtest_result.json")
        
    else:
        print(f"\n❌ 回测失败: {result.get('error', 'Unknown error')}")
    
    return result


if __name__ == "__main__":
    result = test_enhanced_backtest()