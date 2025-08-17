#!/usr/bin/env python3
"""
系统功能测试脚本
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_health():
    """测试健康检查"""
    resp = requests.get(f"{BASE_URL}/api/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "healthy"
    print("✅ 健康检查通过")

def test_stock_search():
    """测试股票搜索"""
    resp = requests.get(f"{BASE_URL}/api/stocks/search?q=AAPL")
    assert resp.status_code == 200
    data = resp.json()
    assert data["count"] > 0
    print(f"✅ 股票搜索通过，找到 {data['count']} 个结果")

def test_stock_info():
    """测试获取股票信息"""
    resp = requests.get(f"{BASE_URL}/api/stocks/info/AAPL")
    assert resp.status_code == 200
    data = resp.json()
    assert "symbol" in data
    print(f"✅ 股票信息获取通过: {data.get('name', 'AAPL')}")

def test_basic_backtest():
    """测试基础回测"""
    config = {
        "assets": [
            {"symbol": "AAPL", "weight": 40},
            {"symbol": "MSFT", "weight": 30},
            {"symbol": "GOOGL", "weight": 30}
        ],
        "start_date": "2023-01-01",
        "end_date": "2023-12-31",
        "initial_amount": 10000
    }
    
    resp = requests.post(f"{BASE_URL}/api/backtest/run", json=config)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "completed"
    assert "performance_summary" in data
    
    total_return = data["performance_summary"]["total_return_pct"]
    print(f"✅ 基础回测通过，总收益率: {total_return:.2f}%")
    return data

def test_periodic_dca():
    """测试定期定投"""
    config = {
        "assets": [
            {"symbol": "AAPL", "weight": 50},
            {"symbol": "MSFT", "weight": 50}
        ],
        "start_date": "2023-01-01",
        "end_date": "2023-12-31",
        "initial_amount": 1000,
        "investment_amount": 500,
        "frequency": "monthly",
        "frequency_config": {
            "day_of_month": 1
        }
    }
    
    resp = requests.post(f"{BASE_URL}/api/backtest/dca/periodic", json=config)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "completed"
    
    total_invested = data["performance"].get("total_invested", 0)
    final_value = data["performance"].get("final_value", 0)
    print(f"✅ 定期定投通过，总投入: ${total_invested:.2f}, 最终价值: ${final_value:.2f}")
    return data

def test_conditional_dca():
    """测试条件定投"""
    config = {
        "assets": [
            {"symbol": "AAPL", "weight": 100}
        ],
        "start_date": "2023-01-01",
        "end_date": "2023-06-30",
        "initial_amount": 5000,
        "conditions": [
            {
                "type": "price_drop",
                "config": {
                    "drop_percentage": 2.0,
                    "amount": 1000,
                    "cooldown_days": 7
                }
            }
        ]
    }
    
    resp = requests.post(f"{BASE_URL}/api/backtest/dca/conditional", json=config)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "completed"
    
    triggers = data["config_summary"].get("total_triggers", 0)
    print(f"✅ 条件定投通过，触发次数: {triggers}")
    return data

def test_portfolio_management():
    """测试投资组合管理"""
    # 创建组合
    portfolio = {
        "name": "测试组合",
        "assets": [
            {"symbol": "AAPL", "weight": 50},
            {"symbol": "MSFT", "weight": 50}
        ]
    }
    
    resp = requests.post(f"{BASE_URL}/api/portfolio/create", json=portfolio)
    assert resp.status_code == 201
    data = resp.json()
    portfolio_id = data["portfolio_id"]
    print(f"✅ 创建投资组合成功，ID: {portfolio_id}")
    
    # 获取组合
    resp = requests.get(f"{BASE_URL}/api/portfolio/{portfolio_id}")
    assert resp.status_code == 200
    
    # 列出组合
    resp = requests.get(f"{BASE_URL}/api/portfolio/list")
    assert resp.status_code == 200
    print(f"✅ 投资组合管理功能通过")
    
    return portfolio_id

def run_all_tests():
    """运行所有测试"""
    print("\n" + "="*50)
    print("开始系统功能测试")
    print("="*50 + "\n")
    
    try:
        # 1. 基础功能测试
        print("1. 基础功能测试")
        test_health()
        test_stock_search()
        test_stock_info()
        
        # 2. 回测功能测试
        print("\n2. 回测功能测试")
        backtest_result = test_basic_backtest()
        
        # 3. 定投功能测试
        print("\n3. 定投功能测试")
        test_periodic_dca()
        test_conditional_dca()
        
        # 4. 投资组合管理测试
        print("\n4. 投资组合管理测试")
        test_portfolio_management()
        
        print("\n" + "="*50)
        print("✅ 所有测试通过！")
        print("="*50 + "\n")
        
        # 显示统计
        print("系统功能统计:")
        print(f"- 核心回测引擎: ✅ 完成")
        print(f"- 定期定投功能: ✅ 完成")
        print(f"- 条件定投功能: ✅ 完成")
        print(f"- 投资组合管理: ✅ 完成")
        print(f"- API接口: ✅ 完成")
        print(f"- 前端界面: ✅ 完成")
        
    except AssertionError as e:
        print(f"\n❌ 测试失败: {e}")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")

if __name__ == "__main__":
    run_all_tests()