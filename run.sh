#!/bin/bash

# 股票回测分析系统启动脚本

echo "========================================="
echo "   股票回测分析系统 - MVP版本"
echo "========================================="

# 激活虚拟环境
echo "激活Python虚拟环境..."
source /Users/kadewu/Documents/pythons/backtest_env/bin/activate

# 检查依赖
echo "检查依赖包..."
python -c "import fastapi; import pandas; import yfinance" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "缺少依赖包，正在安装..."
    pip install fastapi uvicorn pandas numpy yfinance python-dotenv sqlalchemy jinja2 python-multipart
fi

# 创建必要的目录
echo "创建必要的目录..."
mkdir -p logs data/cache app/static

# 启动应用
echo "启动应用..."
echo "访问地址: http://localhost:8000"
echo "API文档: http://localhost:8000/docs"
echo "按 Ctrl+C 停止服务"
echo "========================================="

# 运行应用
python -m uvicorn app.main:app --host localhost --port 8000 --reload