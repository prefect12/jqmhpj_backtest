# 股票回测分析系统 Makefile

# 变量定义
PYTHON = python
PIP = pip
VENV_PATH = /Users/kadewu/Documents/pythons/backtest_env
VENV_ACTIVATE = source $(VENV_PATH)/bin/activate
UVICORN = uvicorn
PYTEST = pytest

# 默认目标
.DEFAULT_GOAL := help

# 帮助信息
.PHONY: help
help:
	@echo "========================================="
	@echo "   股票回测分析系统 - 命令列表"
	@echo "========================================="
	@echo "make install    - 安装所有依赖"
	@echo "make test       - 运行所有测试"
	@echo "make test-v     - 运行测试（详细输出）"
	@echo "make test-cov   - 运行测试并生成覆盖率报告"
	@echo "make start      - 启动开发服务器"
	@echo "make run        - 启动生产服务器"
	@echo "make clean      - 清理缓存文件"
	@echo "make db-init    - 初始化数据库"
	@echo "make lint       - 运行代码检查"
	@echo "make format     - 格式化代码"
	@echo "make requirements - 更新requirements.txt"
	@echo "========================================="

# 安装依赖
.PHONY: install
install:
	@echo "安装项目依赖..."
	@$(VENV_ACTIVATE) && $(PIP) install -r requirements.txt
	@$(VENV_ACTIVATE) && $(PIP) install pytest pytest-cov pytest-mock pytest-asyncio
	@echo "依赖安装完成！"

# 运行测试
.PHONY: test
test:
	@echo "运行单元测试..."
	@$(VENV_ACTIVATE) && $(PYTEST) tests/ --tb=short

# 运行测试（详细输出）
.PHONY: test-v
test-v:
	@echo "运行单元测试（详细模式）..."
	@$(VENV_ACTIVATE) && $(PYTEST) tests/ -v -s

# 运行测试并生成覆盖率报告
.PHONY: test-cov
test-cov:
	@echo "运行测试并生成覆盖率报告..."
	@$(VENV_ACTIVATE) && $(PYTEST) tests/ --cov=app --cov-report=html --cov-report=term
	@echo "覆盖率报告已生成: htmlcov/index.html"

# 运行特定测试文件
.PHONY: test-file
test-file:
	@echo "运行特定测试文件..."
	@$(VENV_ACTIVATE) && $(PYTEST) $(FILE) -v

# 启动开发服务器
.PHONY: start
start:
	@echo "========================================="
	@echo "   启动开发服务器"
	@echo "========================================="
	@echo "访问地址: http://localhost:8000"
	@echo "API文档: http://localhost:8000/docs"
	@echo "按 Ctrl+C 停止服务"
	@echo "========================================="
	@$(VENV_ACTIVATE) && $(UVICORN) app.main:app --host localhost --port 8000 --reload

# 启动生产服务器
.PHONY: run
run:
	@echo "启动生产服务器..."
	@$(VENV_ACTIVATE) && $(UVICORN) app.main:app --host 0.0.0.0 --port 8000 --workers 4

# 清理缓存文件
.PHONY: clean
clean:
	@echo "清理缓存文件..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete
	@find . -type f -name "*.pyo" -delete
	@find . -type f -name ".coverage" -delete
	@rm -rf htmlcov/
	@rm -rf .pytest_cache/
	@rm -rf data/cache/*.json 2>/dev/null || true
	@echo "清理完成！"

# 初始化数据库
.PHONY: db-init
db-init:
	@echo "初始化数据库..."
	@$(VENV_ACTIVATE) && $(PYTHON) -c "from app.core.database import init_db; init_db()"
	@echo "数据库初始化完成！"

# 删除数据库
.PHONY: db-drop
db-drop:
	@echo "删除数据库..."
	@rm -f backtest.db
	@echo "数据库已删除！"

# 重置数据库
.PHONY: db-reset
db-reset: db-drop db-init
	@echo "数据库已重置！"

# 代码检查
.PHONY: lint
lint:
	@echo "运行代码检查..."
	@$(VENV_ACTIVATE) && flake8 app/ tests/ --max-line-length=120 --exclude=__pycache__ || true
	@$(VENV_ACTIVATE) && mypy app/ --ignore-missing-imports || true

# 格式化代码
.PHONY: format
format:
	@echo "格式化代码..."
	@$(VENV_ACTIVATE) && black app/ tests/ --line-length=120
	@echo "代码格式化完成！"

# 更新requirements.txt
.PHONY: requirements
requirements:
	@echo "更新requirements.txt..."
	@$(VENV_ACTIVATE) && $(PIP) freeze > requirements.txt
	@echo "requirements.txt已更新！"

# 检查环境
.PHONY: check
check:
	@echo "检查开发环境..."
	@$(VENV_ACTIVATE) && $(PYTHON) --version
	@$(VENV_ACTIVATE) && $(PIP) --version
	@$(VENV_ACTIVATE) && $(PYTHON) -c "import fastapi; print('FastAPI:', fastapi.__version__)"
	@$(VENV_ACTIVATE) && $(PYTHON) -c "import pandas; print('Pandas:', pandas.__version__)"
	@$(VENV_ACTIVATE) && $(PYTHON) -c "import yfinance; print('yfinance:', yfinance.__version__)"
	@echo "环境检查完成！"

# 创建必要的目录
.PHONY: setup
setup:
	@echo "创建必要的目录..."
	@mkdir -p logs
	@mkdir -p data/cache
	@mkdir -p app/static
	@mkdir -p uploads
	@echo "目录创建完成！"

# 开发环境初始化（首次使用）
.PHONY: init
init: setup install db-init
	@echo "========================================="
	@echo "   开发环境初始化完成！"
	@echo "   使用 'make start' 启动服务"
	@echo "   使用 'make test' 运行测试"
	@echo "========================================="

# 查看日志
.PHONY: logs
logs:
	@tail -f logs/backtest.log 2>/dev/null || echo "日志文件不存在"

# 运行单个测试模块
.PHONY: test-dao
test-dao:
	@$(VENV_ACTIVATE) && $(PYTEST) tests/dao/ -v

.PHONY: test-utils
test-utils:
	@$(VENV_ACTIVATE) && $(PYTEST) tests/utils/ -v

.PHONY: test-services
test-services:
	@$(VENV_ACTIVATE) && $(PYTEST) tests/services/ -v