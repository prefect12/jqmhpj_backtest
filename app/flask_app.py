"""
Flask应用主入口
"""
from flask import Flask, render_template
from flask_cors import CORS
import os
from pathlib import Path

# Import core modules
from app.core.config import settings
from app.core.database import init_db

# Import controllers
from app.controllers.backtest_controller import backtest_bp
from app.controllers.portfolio_controller import portfolio_bp


def create_app():
    """创建Flask应用"""
    app = Flask(__name__, 
                template_folder='../templates',
                static_folder='static')
    
    # 配置CORS
    CORS(app, origins=settings.cors_origins)
    
    # 配置应用
    app.config['SECRET_KEY'] = settings.app_secret_key
    app.config['JSON_SORT_KEYS'] = False
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
    
    # 注册蓝图
    app.register_blueprint(backtest_bp)
    app.register_blueprint(portfolio_bp)
    
    # 首页路由 - 直接显示高级配置页面
    @app.route('/')
    def index():
        """首页 - 高级投资组合配置"""
        return render_template('portfolio/advanced_config.html')
    
    @app.route('/portfolio')
    def portfolio():
        """投资组合配置页面 - 重定向到高级配置"""
        return render_template('portfolio/advanced_config.html')
    
    @app.route('/backtest')
    def backtest():
        """回测结果页面"""
        return render_template('backtest/result.html')
    
    @app.route('/dca')
    def dca():
        """定投设置页面 - 重定向到高级配置"""
        return render_template('portfolio/advanced_config.html')
    
    @app.route('/portfolio/advanced')
    def portfolio_advanced():
        """高级投资组合配置页面"""
        return render_template('portfolio/advanced_config.html')
    
    # 健康检查
    @app.route('/api/health')
    def health_check():
        """健康检查"""
        return {'status': 'healthy', 'version': '1.0.0'}
    
    return app


# 创建应用实例
app = create_app()


if __name__ == '__main__':
    # 初始化数据库
    init_db()
    
    # 运行应用
    app.run(
        host=settings.app_host,
        port=settings.app_port,
        debug=settings.app_debug
    )