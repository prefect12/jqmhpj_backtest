#!/usr/bin/env python3
"""
API接口测试脚本
使用requests库测试所有API端点
"""
import requests
import json
import time
import sys
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"

class APITester:
    """API测试器"""
    
    def __init__(self, base_url=BASE_URL):
        self.base_url = base_url
        self.test_results = []
        self.portfolio_id = None
        
    def test_endpoint(self, name, method, path, data=None, params=None):
        """测试单个端点"""
        url = f"{self.base_url}{path}"
        try:
            if method == "GET":
                resp = requests.get(url, params=params)
            elif method == "POST":
                resp = requests.post(url, json=data)
            elif method == "PUT":
                resp = requests.put(url, json=data)
            elif method == "DELETE":
                resp = requests.delete(url)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            success = resp.status_code in [200, 201]
            self.test_results.append({
                'name': name,
                'method': method,
                'path': path,
                'status_code': resp.status_code,
                'success': success,
                'response': resp.json() if resp.text else None
            })
            
            if success:
                print(f"✅ {name}: {resp.status_code}")
            else:
                print(f"❌ {name}: {resp.status_code}")
                if resp.text:
                    print(f"   Error: {resp.text[:200]}")
            
            return resp.json() if resp.text else None
            
        except Exception as e:
            print(f"❌ {name}: {str(e)}")
            self.test_results.append({
                'name': name,
                'method': method,
                'path': path,
                'error': str(e),
                'success': False
            })
            return None
    
    def run_all_tests(self):
        """运行所有测试"""
        print("\n" + "="*60)
        print("API接口测试")
        print("="*60 + "\n")
        
        # 1. 健康检查
        print("1. 基础端点测试")
        print("-" * 40)
        self.test_endpoint("健康检查", "GET", "/api/health")
        
        # 2. 股票相关API
        print("\n2. 股票数据API测试")
        print("-" * 40)
        self.test_endpoint("股票搜索", "GET", "/api/stocks/search", params={"q": "AAPL", "limit": 5})
        self.test_endpoint("股票信息", "GET", "/api/stocks/info/AAPL")
        self.test_endpoint("股票验证", "POST", "/api/stocks/validate", 
                          data={"symbols": ["AAPL", "MSFT", "INVALID"]})
        self.test_endpoint("批量股票信息", "POST", "/api/stocks/batch-info",
                          data={"symbols": ["AAPL", "MSFT", "GOOGL"]})
        
        # 3. 投资组合管理API
        print("\n3. 投资组合管理API测试")
        print("-" * 40)
        portfolio_resp = self.test_endpoint("创建投资组合", "POST", "/api/portfolio/create",
                                           data={
                                               "name": "测试组合",
                                               "assets": [
                                                   {"symbol": "AAPL", "weight": 40},
                                                   {"symbol": "MSFT", "weight": 30},
                                                   {"symbol": "GOOGL", "weight": 30}
                                               ]
                                           })
        if portfolio_resp:
            self.portfolio_id = portfolio_resp.get("portfolio_id")
            
        if self.portfolio_id:
            self.test_endpoint("获取投资组合", "GET", f"/api/portfolio/{self.portfolio_id}")
            self.test_endpoint("更新投资组合", "PUT", f"/api/portfolio/{self.portfolio_id}",
                             data={
                                 "name": "更新的测试组合",
                                 "assets": [
                                     {"symbol": "AAPL", "weight": 50},
                                     {"symbol": "MSFT", "weight": 50}
                                 ]
                             })
        
        self.test_endpoint("列出投资组合", "GET", "/api/portfolio/list", params={"limit": 10})
        
        # 4. 基础回测API
        print("\n4. 基础回测API测试")
        print("-" * 40)
        
        # 测试无基准回测
        self.test_endpoint("基础回测(无基准)", "POST", "/api/backtest/run",
                          data={
                              "assets": [
                                  {"symbol": "AAPL", "weight": 50},
                                  {"symbol": "MSFT", "weight": 50}
                              ],
                              "start_date": "2023-01-01",
                              "end_date": "2023-06-30",
                              "initial_amount": 10000
                          })
        
        # 测试带基准回测
        self.test_endpoint("基础回测(带基准SPY)", "POST", "/api/backtest/run",
                          data={
                              "assets": [
                                  {"symbol": "AAPL", "weight": 40},
                                  {"symbol": "MSFT", "weight": 30},
                                  {"symbol": "GOOGL", "weight": 30}
                              ],
                              "start_date": "2023-01-01",
                              "end_date": "2023-06-30",
                              "initial_amount": 10000,
                              "benchmark": "SPY"
                          })
        
        # 测试再平衡策略
        self.test_endpoint("回测(月度再平衡)", "POST", "/api/backtest/run",
                          data={
                              "assets": [
                                  {"symbol": "AAPL", "weight": 50},
                                  {"symbol": "MSFT", "weight": 50}
                              ],
                              "start_date": "2023-01-01",
                              "end_date": "2023-12-31",
                              "initial_amount": 10000,
                              "rebalance_frequency": "monthly"
                          })
        
        # 5. 定投策略API
        print("\n5. 定投策略API测试")
        print("-" * 40)
        
        # 定期定投测试
        self.test_endpoint("定期定投(每月)", "POST", "/api/backtest/dca/periodic",
                          data={
                              "assets": [
                                  {"symbol": "AAPL", "weight": 60},
                                  {"symbol": "MSFT", "weight": 40}
                              ],
                              "start_date": "2023-01-01",
                              "end_date": "2023-12-31",
                              "initial_amount": 1000,
                              "investment_amount": 500,
                              "frequency": "monthly",
                              "frequency_config": {
                                  "day_of_month": 15
                              }
                          })
        
        self.test_endpoint("定期定投(每周)", "POST", "/api/backtest/dca/periodic",
                          data={
                              "assets": [
                                  {"symbol": "SPY", "weight": 100}
                              ],
                              "start_date": "2023-01-01",
                              "end_date": "2023-03-31",
                              "initial_amount": 1000,
                              "investment_amount": 200,
                              "frequency": "weekly",
                              "frequency_config": {
                                  "day_of_week": 1  # 周一
                              }
                          })
        
        # 条件定投测试
        self.test_endpoint("条件定投(下跌触发)", "POST", "/api/backtest/dca/conditional",
                          data={
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
                                          "drop_percentage": 3.0,
                                          "amount": 1000,
                                          "cooldown_days": 7
                                      }
                                  }
                              ]
                          })
        
        self.test_endpoint("条件定投(回撤触发)", "POST", "/api/backtest/dca/conditional",
                          data={
                              "assets": [
                                  {"symbol": "SPY", "weight": 50},
                                  {"symbol": "QQQ", "weight": 50}
                              ],
                              "start_date": "2023-01-01",
                              "end_date": "2023-06-30",
                              "initial_amount": 10000,
                              "conditions": [
                                  {
                                      "type": "drawdown",
                                      "config": {
                                          "drawdown_percentage": 5.0,
                                          "amount": 2000,
                                          "cooldown_days": 10
                                      }
                                  }
                              ]
                          })
        
        # 6. 回测历史
        print("\n6. 回测历史API测试")
        print("-" * 40)
        self.test_endpoint("获取回测历史", "GET", "/api/backtest/history", 
                          params={"limit": 5, "offset": 0})
        
        # 7. 错误处理测试
        print("\n7. 错误处理测试")
        print("-" * 40)
        self.test_endpoint("无效股票代码", "GET", "/api/stocks/info/INVALID_SYMBOL")
        self.test_endpoint("权重不等于100%", "POST", "/api/backtest/run",
                          data={
                              "assets": [
                                  {"symbol": "AAPL", "weight": 40},
                                  {"symbol": "MSFT", "weight": 30}
                              ],
                              "start_date": "2023-01-01",
                              "end_date": "2023-06-30",
                              "initial_amount": 10000
                          })
        self.test_endpoint("金额超出限制", "POST", "/api/backtest/run",
                          data={
                              "assets": [
                                  {"symbol": "AAPL", "weight": 100}
                              ],
                              "start_date": "2023-01-01",
                              "end_date": "2023-06-30",
                              "initial_amount": 10000000
                          })
        
        # 打印测试总结
        self.print_summary()
    
    def print_summary(self):
        """打印测试总结"""
        print("\n" + "="*60)
        print("测试总结")
        print("="*60)
        
        total = len(self.test_results)
        passed = sum(1 for r in self.test_results if r['success'])
        failed = total - passed
        
        print(f"总测试数: {total}")
        print(f"✅ 通过: {passed}")
        print(f"❌ 失败: {failed}")
        print(f"成功率: {passed/total*100:.1f}%")
        
        if failed > 0:
            print("\n失败的测试:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['name']}: {result.get('error', f'HTTP {result.get('status_code')}')}")
        
        # 保存测试结果
        with open('api_test_results.json', 'w', encoding='utf-8') as f:
            json.dump(self.test_results, f, indent=2, ensure_ascii=False)
        print(f"\n测试结果已保存到 api_test_results.json")

def main():
    """主函数"""
    print("检查服务是否运行...")
    try:
        resp = requests.get(f"{BASE_URL}/api/health", timeout=2)
        if resp.status_code == 200:
            print("✅ 服务正在运行")
        else:
            print("⚠️ 服务响应异常")
    except:
        print("❌ 无法连接到服务，请先启动服务:")
        print("   python -m app.flask_app")
        sys.exit(1)
    
    tester = APITester()
    tester.run_all_tests()

if __name__ == "__main__":
    main()