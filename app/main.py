"""
FastAPI主应用入口
"""
from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import json
from typing import List
from app.core.config import settings
from app.core.database import init_db
from app.services.backtest_service import BacktestService

# 创建FastAPI应用
app = FastAPI(
    title="Stock Backtest Analysis",
    description="股票回测分析系统",
    version="1.0.0",
    debug=settings.app_debug
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 配置模板和静态文件
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# 初始化服务
backtest_service = BacktestService()


@app.on_event("startup")
async def startup_event():
    """应用启动时初始化数据库"""
    init_db()
    print("Database initialized")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """首页"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/api/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "version": "1.0.0"}


@app.post("/api/backtest/run")
async def run_backtest(
    assets: str = Form(...),
    start_date: str = Form(...),
    end_date: str = Form(...),
    initial_amount: float = Form(10000.0)
):
    """
    运行回测
    
    Args:
        assets: JSON字符串，格式: [{"symbol": "AAPL", "weight": 40}, ...]
        start_date: 开始日期
        end_date: 结束日期
        initial_amount: 初始金额
    """
    try:
        # 解析资产配置
        assets_list = json.loads(assets)
        
        # 构建回测配置
        portfolio_config = {
            'assets': assets_list,
            'start_date': start_date,
            'end_date': end_date,
            'initial_amount': initial_amount,
            'rebalance_frequency': 'quarterly'
        }
        
        # 执行回测
        result = backtest_service.run_backtest(portfolio_config)
        
        return JSONResponse(content=result)
        
    except json.JSONDecodeError:
        return JSONResponse(
            status_code=400,
            content={"error": "Invalid JSON format for assets"}
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )


@app.get("/api/stocks/search")
async def search_stocks(query: str, limit: int = 10):
    """搜索股票"""
    from app.dao.stock_data_dao import StockDataDAO
    stock_dao = StockDataDAO()
    results = stock_dao.search_stocks(query, limit)
    return results


@app.get("/api/stocks/{symbol}/info")
async def get_stock_info(symbol: str):
    """获取股票信息"""
    from app.dao.stock_data_dao import StockDataDAO
    stock_dao = StockDataDAO()
    try:
        info = stock_dao.get_stock_info(symbol)
        return info
    except Exception as e:
        return JSONResponse(
            status_code=404,
            content={"error": f"Stock {symbol} not found: {str(e)}"}
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.app_debug
    )