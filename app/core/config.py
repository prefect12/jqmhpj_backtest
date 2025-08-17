"""
应用配置模块
从环境变量加载配置
"""
import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field
from dotenv import load_dotenv
import json

# 加载环境变量
load_dotenv()


class Settings(BaseSettings):
    """应用配置类"""
    
    # 应用配置
    app_env: str = "development"
    app_debug: bool = True
    app_host: str = "localhost"
    app_port: int = 8000
    app_secret_key: str = "dev-secret-key-change-in-production"
    
    # 数据库配置
    database_url: str = "sqlite:///./backtest.db"
    database_echo: bool = False
    database_pool_size: int = 10
    
    # 数据源配置
    yfinance_timeout: int = 10
    yfinance_retry_count: int = 3
    yfinance_cache_ttl: int = 3600
    
    # OpenAI配置
    openai_api_key: Optional[str] = None
    
    # 回测计算配置
    max_assets_count: int = 5
    max_backtest_years: int = 5
    min_initial_amount: float = 1000.0
    max_initial_amount: float = 1000000.0
    
    # 性能配置
    calculation_timeout: int = 30
    cache_enabled: bool = True
    cache_ttl: int = 1800
    
    # 日志配置
    log_level: str = "INFO"
    log_file: str = "logs/backtest.log"
    log_max_size: int = 10
    log_backup_count: int = 5
    
    # 安全配置
    cors_origins: List[str] = Field(default=["http://localhost:8000", "http://127.0.0.1:8000"])
    rate_limit_enabled: bool = False
    rate_limit_requests: int = 100
    rate_limit_window: int = 3600
    
    # 静态文件配置
    static_files_dir: str = "static"
    templates_dir: str = "templates"
    upload_dir: str = "uploads"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# 创建全局配置实例
settings = Settings()


def validate_config():
    """验证关键配置是否存在"""
    required_configs = ["app_secret_key", "database_url"]
    
    for config in required_configs:
        if not getattr(settings, config):
            raise ValueError(f"Required config {config} is missing")


# 验证配置（开发环境可选）
if settings.app_env == "production":
    validate_config()