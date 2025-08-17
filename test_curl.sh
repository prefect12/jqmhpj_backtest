#!/bin/bash

# API测试脚本 - 使用curl测试所有端点和页面
# 使用方法: ./test_curl.sh

BASE_URL="http://localhost:8000"
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "======================================"
echo "API和页面测试脚本"
echo "======================================"

# 检查服务是否运行
echo -e "\n${YELLOW}检查服务状态...${NC}"
if curl -s "${BASE_URL}/api/health" > /dev/null; then
    echo -e "${GREEN}✅ 服务正在运行${NC}"
else
    echo -e "${RED}❌ 服务未运行，请先启动服务:${NC}"
    echo "   python -m app.flask_app"
    exit 1
fi

# 1. 测试API端点
echo -e "\n${YELLOW}=== 1. API端点测试 ===${NC}"

# 健康检查
echo -e "\n${YELLOW}健康检查:${NC}"
curl -X GET "${BASE_URL}/api/health" | python3 -m json.tool

# 股票搜索
echo -e "\n${YELLOW}股票搜索 (AAPL):${NC}"
curl -X GET "${BASE_URL}/api/stocks/search?q=AAPL&limit=3" | python3 -m json.tool

# 股票信息
echo -e "\n${YELLOW}获取股票信息 (AAPL):${NC}"
curl -X GET "${BASE_URL}/api/stocks/info/AAPL" | python3 -m json.tool

# 验证股票代码
echo -e "\n${YELLOW}验证股票代码:${NC}"
curl -X POST "${BASE_URL}/api/stocks/validate" \
  -H "Content-Type: application/json" \
  -d '{"symbols": ["AAPL", "MSFT", "INVALID"]}' | python3 -m json.tool

# 创建投资组合
echo -e "\n${YELLOW}创建投资组合:${NC}"
PORTFOLIO_RESPONSE=$(curl -X POST "${BASE_URL}/api/portfolio/create" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "测试组合",
    "assets": [
      {"symbol": "AAPL", "weight": 50},
      {"symbol": "MSFT", "weight": 50}
    ]
  }')
echo $PORTFOLIO_RESPONSE | python3 -m json.tool
PORTFOLIO_ID=$(echo $PORTFOLIO_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin).get('portfolio_id', ''))")

# 获取投资组合
if [ ! -z "$PORTFOLIO_ID" ]; then
    echo -e "\n${YELLOW}获取投资组合 (${PORTFOLIO_ID}):${NC}"
    curl -X GET "${BASE_URL}/api/portfolio/${PORTFOLIO_ID}" | python3 -m json.tool
fi

# 基础回测
echo -e "\n${YELLOW}执行基础回测:${NC}"
curl -X POST "${BASE_URL}/api/backtest/run" \
  -H "Content-Type: application/json" \
  -d '{
    "assets": [
      {"symbol": "AAPL", "weight": 40},
      {"symbol": "MSFT", "weight": 30},
      {"symbol": "GOOGL", "weight": 30}
    ],
    "start_date": "2023-01-01",
    "end_date": "2023-06-30",
    "initial_amount": 10000
  }' | python3 -m json.tool | head -50

# 带基准的回测
echo -e "\n${YELLOW}执行带基准的回测 (SPY):${NC}"
curl -X POST "${BASE_URL}/api/backtest/run" \
  -H "Content-Type: application/json" \
  -d '{
    "assets": [
      {"symbol": "AAPL", "weight": 50},
      {"symbol": "MSFT", "weight": 50}
    ],
    "start_date": "2023-01-01",
    "end_date": "2023-06-30",
    "initial_amount": 10000,
    "benchmark": "SPY"
  }' | python3 -m json.tool | head -50

# 定期定投
echo -e "\n${YELLOW}执行定期定投回测:${NC}"
curl -X POST "${BASE_URL}/api/backtest/dca/periodic" \
  -H "Content-Type: application/json" \
  -d '{
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
  }' | python3 -m json.tool | head -50

# 条件定投
echo -e "\n${YELLOW}执行条件定投回测:${NC}"
curl -X POST "${BASE_URL}/api/backtest/dca/conditional" \
  -H "Content-Type: application/json" \
  -d '{
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
  }' | python3 -m json.tool | head -50

# 2. 测试HTML页面
echo -e "\n${YELLOW}=== 2. HTML页面测试 ===${NC}"

# 测试页面响应
test_page() {
    local path=$1
    local name=$2
    
    echo -e "\n${YELLOW}测试页面: ${name}${NC}"
    response=$(curl -s -o /dev/null -w "%{http_code}" "${BASE_URL}${path}")
    
    if [ "$response" == "200" ]; then
        echo -e "${GREEN}✅ ${name}: HTTP ${response}${NC}"
        # 获取页面标题
        title=$(curl -s "${BASE_URL}${path}" | grep -o '<title>[^<]*</title>' | sed 's/<[^>]*>//g')
        echo "   标题: ${title}"
        # 检查页面大小
        size=$(curl -s "${BASE_URL}${path}" | wc -c)
        echo "   页面大小: ${size} bytes"
    else
        echo -e "${RED}❌ ${name}: HTTP ${response}${NC}"
    fi
}

# 测试所有页面
test_page "/" "首页"
test_page "/portfolio/config" "投资组合配置"
test_page "/backtest/result" "回测结果"
test_page "/backtest/dca" "定投设置"

# 3. 测试静态资源
echo -e "\n${YELLOW}=== 3. 静态资源测试 ===${NC}"

# 测试CSS文件
echo -e "\n${YELLOW}测试CSS文件:${NC}"
css_response=$(curl -s -o /dev/null -w "%{http_code}" "${BASE_URL}/static/css/style.css")
if [ "$css_response" == "200" ] || [ "$css_response" == "404" ]; then
    if [ "$css_response" == "200" ]; then
        echo -e "${GREEN}✅ CSS文件存在${NC}"
    else
        echo -e "${YELLOW}⚠️ CSS文件不存在（可能使用内联样式）${NC}"
    fi
else
    echo -e "${RED}❌ CSS文件访问失败: HTTP ${css_response}${NC}"
fi

# 4. 性能测试
echo -e "\n${YELLOW}=== 4. 性能测试 ===${NC}"

echo -e "\n${YELLOW}测试API响应时间:${NC}"

# 测试简单查询
start_time=$(date +%s%N)
curl -s "${BASE_URL}/api/health" > /dev/null
end_time=$(date +%s%N)
elapsed=$((($end_time - $start_time) / 1000000))
echo "健康检查: ${elapsed}ms"

# 测试回测计算
start_time=$(date +%s%N)
curl -s -X POST "${BASE_URL}/api/backtest/run" \
  -H "Content-Type: application/json" \
  -d '{
    "assets": [{"symbol": "AAPL", "weight": 100}],
    "start_date": "2023-01-01",
    "end_date": "2023-03-31",
    "initial_amount": 10000
  }' > /dev/null
end_time=$(date +%s%N)
elapsed=$((($end_time - $start_time) / 1000000))
echo "回测计算(3个月): ${elapsed}ms"

# 5. 错误处理测试
echo -e "\n${YELLOW}=== 5. 错误处理测试 ===${NC}"

echo -e "\n${YELLOW}测试无效股票代码:${NC}"
curl -X GET "${BASE_URL}/api/stocks/info/INVALID_SYMBOL" 2>/dev/null | python3 -m json.tool

echo -e "\n${YELLOW}测试权重错误:${NC}"
curl -X POST "${BASE_URL}/api/backtest/run" \
  -H "Content-Type: application/json" \
  -d '{
    "assets": [
      {"symbol": "AAPL", "weight": 40},
      {"symbol": "MSFT", "weight": 30}
    ],
    "start_date": "2023-01-01",
    "end_date": "2023-06-30",
    "initial_amount": 10000
  }' 2>/dev/null | python3 -m json.tool

# 6. 并发测试
echo -e "\n${YELLOW}=== 6. 并发测试 ===${NC}"

echo -e "\n${YELLOW}发送5个并发请求:${NC}"
for i in {1..5}; do
    curl -s "${BASE_URL}/api/health" > /dev/null &
done
wait
echo -e "${GREEN}✅ 并发请求完成${NC}"

# 总结
echo -e "\n${YELLOW}======================================"
echo "测试完成"
echo "======================================${NC}"

# 统计成功的测试
echo -e "\n${GREEN}测试总结:${NC}"
echo "- API端点测试: 完成"
echo "- HTML页面测试: 完成"
echo "- 静态资源测试: 完成"
echo "- 性能测试: 完成"
echo "- 错误处理测试: 完成"
echo "- 并发测试: 完成"

echo -e "\n${GREEN}所有测试已完成！${NC}"