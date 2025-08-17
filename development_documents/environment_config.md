# 环境变量配置文档

## 环境变量列表

### 数据源配置
```bash
# Yahoo Finance 数据源配置
YFINANCE_TIMEOUT=10  # API超时时间(秒)
YFINANCE_RETRY_COUNT=3  # 重试次数
YFINANCE_CACHE_TTL=3600  # 缓存时间(秒)

# 备用数据源 (可选)
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key  # Alpha Vantage API密钥
QUANDL_API_KEY=your_quandl_key  # Quandl API密钥
```

### 数据库配置
```bash
# SQLite 数据库配置
DATABASE_URL=sqlite:///./backtest.db  # 数据库文件路径
DATABASE_ECHO=false  # 是否打印SQL语句
DATABASE_POOL_SIZE=10  # 连接池大小
```

### 应用配置
```bash
# 应用基础配置
APP_ENV=development  # 环境: development/production/testing
APP_DEBUG=true  # 调试模式
APP_HOST=localhost  # 主机地址
APP_PORT=8000  # 端口号
APP_SECRET_KEY=your-secret-key-here  # 应用密钥

# 日志配置
LOG_LEVEL=INFO  # 日志级别: DEBUG/INFO/WARNING/ERROR
LOG_FILE=logs/backtest.log  # 日志文件路径
LOG_MAX_SIZE=10  # 日志文件最大大小(MB)
LOG_BACKUP_COUNT=5  # 日志文件备份数量
```

### 计算引擎配置
```bash
# 回测计算配置
MAX_ASSETS_COUNT=5  # 最大资产数量
MAX_BACKTEST_YEARS=5  # 最大回测年限
MIN_INITIAL_AMOUNT=1000  # 最小初始投资金额
MAX_INITIAL_AMOUNT=1000000  # 最大初始投资金额

# 性能配置
CALCULATION_TIMEOUT=30  # 计算超时时间(秒)
CACHE_ENABLED=true  # 是否启用缓存
CACHE_TTL=1800  # 缓存过期时间(秒)
```

### 安全配置
```bash
# 跨域配置
CORS_ORIGINS=["http://localhost:3000", "http://127.0.0.1:3000"]  # 允许的前端域名
CORS_METHODS=["GET", "POST", "PUT", "DELETE"]  # 允许的HTTP方法
CORS_HEADERS=["*"]  # 允许的请求头

# 限流配置
RATE_LIMIT_ENABLED=true  # 是否启用限流
RATE_LIMIT_REQUESTS=100  # 每小时请求限制
RATE_LIMIT_WINDOW=3600  # 限流时间窗口(秒)
```

### 静态文件配置
```bash
# 静态文件配置 (一体化部署)
STATIC_FILES_DIR=static  # 静态文件目录
TEMPLATES_DIR=templates  # 模板文件目录
UPLOAD_DIR=uploads  # 上传文件目录
```

## 环境配置文件

### 开发环境 (.env.development)
```bash
APP_ENV=development
APP_DEBUG=true
APP_HOST=localhost
APP_PORT=8000
DATABASE_URL=sqlite:///./backtest_dev.db
LOG_LEVEL=DEBUG
YFINANCE_TIMEOUT=5
CACHE_TTL=300
```

### 生产环境 (.env.production)
```bash
APP_ENV=production
APP_DEBUG=false
APP_HOST=0.0.0.0
APP_PORT=8000
DATABASE_URL=sqlite:///./backtest_prod.db
LOG_LEVEL=INFO
YFINANCE_TIMEOUT=10
CACHE_TTL=1800
```

### 测试环境 (.env.testing)
```bash
APP_ENV=testing
APP_DEBUG=true
APP_HOST=localhost
APP_PORT=8001
DATABASE_URL=sqlite:///./backtest_test.db
LOG_LEVEL=DEBUG
YFINANCE_TIMEOUT=3
CACHE_ENABLED=false
```

## 配置文件使用方法

### 1. 创建环境配置文件
```bash
# 复制示例配置文件
cp .env.example .env

# 根据环境选择对应配置
cp .env.development .env  # 开发环境
cp .env.production .env   # 生产环境
```

### 2. Python中加载环境变量
```python
# app/core/config.py
import os
from typing import List
from pydantic import BaseSettings

class Settings(BaseSettings):
    # 应用配置
    app_env: str = "development"
    app_debug: bool = True
    app_host: str = "localhost"
    app_port: int = 8000
    app_secret_key: str = "your-secret-key-here"
    
    # 数据库配置
    database_url: str = "sqlite:///./backtest.db"
    database_echo: bool = False
    
    # 数据源配置
    yfinance_timeout: int = 10
    yfinance_retry_count: int = 3
    yfinance_cache_ttl: int = 3600
    
    # 计算配置
    max_assets_count: int = 5
    max_backtest_years: int = 5
    min_initial_amount: float = 1000.0
    max_initial_amount: float = 1000000.0
    
    # 日志配置
    log_level: str = "INFO"
    log_file: str = "logs/backtest.log"
    
    # 安全配置
    cors_origins: List[str] = ["http://localhost:3000"]
    rate_limit_requests: int = 100
    rate_limit_window: int = 3600
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# 创建全局配置实例
settings = Settings()
```

### 3. 在应用中使用配置
```python
# app/main.py
from app.core.config import settings

# 使用配置
app = FastAPI(
    debug=settings.app_debug,
    title="Stock Backtest API"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 敏感信息处理

### 1. 不要提交到版本控制
```bash
# .gitignore
.env
.env.local
.env.production
*.log
backtest*.db
```

### 2. 使用环境变量注入
```bash
# 生产环境通过环境变量注入
export APP_SECRET_KEY="production-secret-key"
export DATABASE_URL="postgresql://user:pass@localhost/backtest"
```

### 3. 配置验证
```python
# app/core/config.py
def validate_config():
    """验证关键配置是否存在"""
    required_configs = [
        "app_secret_key",
        "database_url"
    ]
    
    for config in required_configs:
        if not getattr(settings, config):
            raise ValueError(f"Required config {config} is missing")

# 应用启动时验证
validate_config()
```

## 配置优先级

1. **环境变量** (最高优先级)
2. **.env文件**
3. **默认值** (最低优先级)

## 注意事项

1. **开发环境**: 使用 `.env.development`，启用调试模式
2. **生产环境**: 使用环境变量注入，关闭调试模式
3. **测试环境**: 使用独立的测试数据库，关闭缓存
4. **敏感信息**: 绝不提交密钥和密码到版本控制
5. **配置验证**: 应用启动时验证必要配置项