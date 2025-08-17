# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a stock backtest analysis website that provides portfolio backtesting and risk assessment tools for investors. The project uses Python 3.12 with FastAPI backend and includes comprehensive testing requirements.

## Development Setup

### Virtual Environment

This project uses a Python 3.12 virtual environment located at `/Users/kadewu/Documents/pythons/backtest_env`.

To activate the virtual environment:
```bash
source /Users/kadewu/Documents/pythons/backtest_env/bin/activate
```

To deactivate:
```bash
deactivate
```

### Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run development server
python app/main.py

# Run all tests
python -m pytest tests/ -v

# Run tests with coverage
python -m pytest tests/ -v --cov=app --cov-report=term-missing

# Run specific test modules
python -m pytest tests/services/backtest_service_test.py -v
python -m pytest tests/services/dca_service_test.py -v

# Test API endpoints with curl
# 1. Test portfolio creation
curl -X POST "http://localhost:8000/api/portfolio/create" \
  -H "Content-Type: application/json" \
  -d '{"name":"Test Portfolio","assets":[{"symbol":"AAPL","weight":50},{"symbol":"MSFT","weight":50}]}'

# 2. Test backtest execution
curl -X POST "http://localhost:8000/api/backtest/run" \
  -H "Content-Type: application/json" \
  -d '{"portfolio_id":"port_123","config":{"start_date":"2020-01-01","end_date":"2024-12-31","initial_amount":10000}}'
```

## Architecture

The project follows a **monolithic architecture** with layered design (DAO/Service/Controller) for better development efficiency and deployment simplicity.

### Directory Structure
```
backtest/
├── app/
│   ├── controllers/     # Presentation layer - API controllers
│   ├── services/        # Business logic layer
│   ├── dao/            # Data access layer
│   ├── models/         # Data models
│   ├── utils/          # Utility functions
│   ├── core/           # Core configuration
│   └── static/         # Static files
├── templates/          # HTML templates
├── tests/              # Test files (mirrors app structure)
│   ├── dao/           # DAO layer tests
│   ├── services/      # Service layer tests
│   ├── controllers/   # Controller tests
│   └── integration/   # Integration tests
├── logs/              # Log files
└── data/              # Data files and cache
```

## Development Guidelines

### 🚀 Feature Development Workflow

When implementing any new feature, you MUST follow this complete workflow:

#### 1. Frontend Development
- Create/modify HTML templates in `templates/` directory
- Add necessary JavaScript for interactivity
- Implement form validation and user feedback
- Use Bootstrap for consistent styling
- Test UI responsiveness

#### 2. Backend API Development
- Create/modify controller in `app/controllers/`
- Define API endpoints with proper HTTP methods
- Implement request/response models
- Add input validation
- Handle errors gracefully

#### 3. Service Layer Implementation
- Create/modify service in `app/services/`
- Implement core business logic
- Add data validation
- Handle business rule violations
- Ensure proper error propagation

#### 4. DAO Layer Implementation
- Create/modify DAO in `app/dao/`
- Implement data access methods
- Handle database operations
- Implement caching where appropriate
- Handle external API calls (e.g., yfinance)

#### 5. Unit Testing (REQUIRED)
- Write unit tests in corresponding `tests/` directory
- Follow naming convention: `{module_name}_test.py`
- Test normal paths, edge cases, and error conditions
- Use mocks for external dependencies
- Aim for >90% coverage on business logic
- Run tests: `python -m pytest tests/services/{service_name}_test.py -v`

#### 6. API Testing (REQUIRED)
- Test endpoints using curl commands
- Verify request/response formats
- Test error handling
- Check data validation
- Document curl commands for future reference

#### 7. Integration Testing (REQUIRED)
- Start the service: `python app/main.py`
- Test complete user workflows via UI
- Verify frontend changes are working
- Test API integration with frontend
- Ensure data flows correctly through all layers
- Use curl for systematic API testing:
  ```bash
  # Example: Test complete workflow
  # 1. Create portfolio
  curl -X POST "http://localhost:8000/api/portfolio/create" ...
  # 2. Run backtest
  curl -X POST "http://localhost:8000/api/backtest/run" ...
  # 3. Get results
  curl "http://localhost:8000/api/backtest/result/{id}"
  ```

### 📋 Testing Requirements

#### Test File Naming Convention
```
Source: app/services/backtest_service.py
Test:   tests/services/backtest_service_test.py
```

#### Test Structure
```python
class TestServiceName:
    def setup_method(self):
        # Initialize test objects
    
    def test_method_success(self):
        # Test normal execution
    
    def test_method_edge_case(self):
        # Test boundary conditions
    
    def test_method_error(self):
        # Test error handling
```

#### Running Tests
```bash
# Run all tests
python -m pytest tests/ -v

# Run specific service tests
python -m pytest tests/services/backtest_service_test.py -v

# Run with coverage report
python -m pytest tests/ -v --cov=app --cov-report=term-missing

# Run specific test method
python -m pytest tests/services/backtest_service_test.py::TestBacktestService::test_run_backtest -v
```

### 🔍 Code Quality Standards

1. **Type Hints**: Use type hints for all function parameters and return values
2. **Docstrings**: Add docstrings to all classes and public methods
3. **Error Handling**: Proper exception handling with meaningful error messages
4. **Logging**: Use appropriate logging levels (DEBUG, INFO, WARNING, ERROR)
5. **Code Format**: Follow PEP 8 style guidelines

### 📊 API Specification

All APIs follow RESTful design principles:

```python
# Portfolio APIs
POST   /api/portfolio/create      # Create new portfolio
GET    /api/portfolio/list         # List all portfolios
GET    /api/portfolio/{id}         # Get portfolio details
PUT    /api/portfolio/{id}         # Update portfolio
DELETE /api/portfolio/{id}         # Delete portfolio

# Backtest APIs  
POST   /api/backtest/run          # Execute backtest
GET    /api/backtest/result/{id}  # Get backtest results
GET    /api/backtest/status/{id}  # Check backtest status

# DCA (Dollar Cost Averaging) APIs
POST   /api/dca/plans             # Create DCA plan
GET    /api/dca/plans/{id}        # Get DCA plan details
POST   /api/dca/backtest          # Run DCA backtest

# Data APIs
GET    /api/data/search           # Search stocks
GET    /api/data/stock/{symbol}   # Get stock details
```

### 🗄️ Database Schema

Using SQLite with SQLAlchemy ORM:

```sql
-- portfolios table
CREATE TABLE portfolios (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100),
    assets TEXT (JSON),
    created_at TIMESTAMP
);

-- backtest_results table  
CREATE TABLE backtest_results (
    id INTEGER PRIMARY KEY,
    portfolio_id INTEGER,
    config TEXT (JSON),
    result TEXT (JSON),
    created_at TIMESTAMP
);

-- dca_plans table
CREATE TABLE dca_plans (
    id INTEGER PRIMARY KEY,
    portfolio_id VARCHAR(50),
    plan_type VARCHAR(20),
    frequency VARCHAR(20),
    amount DECIMAL(10,2),
    config JSON,
    created_at TIMESTAMP
);
```

### 🚦 Development Status

#### ✅ Completed Features (90%)
- Core backtest engine with calculations
- Portfolio management (CRUD operations)
- Rebalancing strategies (annual/quarterly/monthly)
- DCA functionality (periodic & conditional investing)
- Technical indicators (RSI, MACD, etc.)
- RESTful API endpoints
- Web UI (portfolio config, results display, DCA settings)
- Risk metrics calculation
- Comprehensive unit tests
- API test scripts

#### ⏸️ Pending Features (10%)
- Benchmark comparison (needs data enhancement)
- Dividend reinvestment (requires dividend data)
- Valuation-based DCA (needs PE/PB data)
- Data export (Excel/PDF)
- End-to-end tests

### 🔧 Environment Configuration

Environment variables (`.env` file):
```bash
# Application
APP_ENV=development
APP_DEBUG=true
APP_HOST=localhost
APP_PORT=8000

# Database
DATABASE_URL=sqlite:///./backtest.db

# Data Sources
YFINANCE_TIMEOUT=10
YFINANCE_RETRY_COUNT=3
YFINANCE_CACHE_TTL=3600

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/backtest.log
```

### 📝 Documentation

All project documentation is organized in the `development_documents/` folder:
- `requirements.md` - Project requirements and features
- `architecture_design.md` - System architecture (DAO/Service/Controller layers)
- `api_specification.md` - REST API specifications
- `testing_guidelines.md` - Unit testing standards
- `ui_design_analysis.md` - UI/UX design guidelines
- `mvp_definition.md` - MVP scope and data structures
- `dca_investment_spec.md` - DCA feature specifications
- `environment_config.md` - Environment configuration guide
- `tech_architecture.md` - Technology stack details

### 🎯 Development Principles

1. **Test-Driven Development**: Write tests before/alongside implementation
2. **Layered Architecture**: Maintain clear separation between layers
3. **API-First Design**: Design APIs before implementation
4. **Documentation**: Keep documentation up-to-date with code changes
5. **Code Review**: Test all changes thoroughly before committing

### 📌 Important Notes

- **Python version**: 3.12.7
- **Virtual environment**: `/Users/kadewu/Documents/pythons/backtest_env`
- **Main entry point**: `app/main.py`
- **Test coverage target**: >90% for business logic
- **API response format**: JSON with `success` flag and `data`/`error` fields

### 🔄 Typical Development Cycle

1. Review requirements in `development_documents/`
2. Implement feature following the 7-step workflow above
3. Write comprehensive unit tests
4. Test API endpoints with curl
5. Run integration tests with UI
6. Update documentation if needed
7. Commit changes with descriptive message