# 股票回测分析系统 - MVP版本

## 项目概述

这是一个基于Python的股票投资组合回测分析系统，可以帮助投资者分析投资组合的历史表现。

## 功能特性

- ✅ 支持多股票投资组合配置
- ✅ 自定义时间范围和初始投资金额
- ✅ 计算核心财务指标（收益率、波动率、夏普比率、最大回撤等）
- ✅ 可视化投资组合增长曲线
- ✅ 年度收益表现分析
- ✅ 简洁直观的Web界面

## 技术架构

- **后端**: Python + FastAPI + SQLAlchemy
- **数据处理**: Pandas + NumPy + yfinance
- **前端**: HTML + Bootstrap + Chart.js
- **数据库**: SQLite

## 快速开始

### 1. 环境要求

- Python 3.12+
- pip包管理器

### 2. 安装依赖

```bash
# 激活虚拟环境
source /Users/kadewu/Documents/pythons/backtest_env/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 3. 配置环境变量

复制环境变量示例文件并根据需要修改：
```bash
cp .env.example .env
```

### 4. 启动应用

```bash
# 使用启动脚本
./run.sh

# 或直接运行
python -m uvicorn app.main:app --host localhost --port 8000 --reload
```

### 5. 访问应用

- 主页: http://localhost:8000
- API文档: http://localhost:8000/docs

## 使用说明

1. **配置投资组合**
   - 输入股票代码（如AAPL、MSFT、GOOGL）
   - 设置各股票权重（总和必须等于100%）
   - 选择回测时间范围
   - 设置初始投资金额

2. **运行回测**
   - 点击"运行回测"按钮
   - 等待计算完成（通常几秒钟）

3. **查看结果**
   - 核心指标卡片显示关键财务指标
   - 投资组合增长图展示净值变化
   - 年度收益图展示每年表现

## 项目结构

```
backtest/
├── app/                     # 应用主目录
│   ├── core/               # 核心配置
│   ├── dao/                # 数据访问层
│   ├── models/             # 数据模型
│   ├── services/           # 业务服务层
│   ├── utils/              # 工具类
│   └── main.py             # FastAPI主应用
├── templates/              # HTML模板
├── tests/                  # 单元测试
├── development_documents/  # 开发文档
├── .env                    # 环境变量
└── requirements.txt        # 依赖列表
```

## 测试

运行单元测试：
```bash
pytest tests/
```

运行测试覆盖率：
```bash
pytest --cov=app tests/
```

## 注意事项

1. **数据源**: 使用Yahoo Finance免费数据，部分股票可能无法获取
2. **性能**: MVP版本适合小规模投资组合（最多5只股票）
3. **时间范围**: 建议回测期间不超过5年
4. **股票市场**: 主要支持美股

## 开发文档

详细的开发文档请查看 `development_documents/` 目录：
- 需求文档: requirements.md
- 架构设计: architecture_design.md
- API规范: api_specification.md
- 测试规范: testing_guidelines.md

## 后续优化

- [ ] 添加更多技术指标
- [ ] 支持中国A股市场
- [ ] 实现投资组合优化功能
- [ ] 添加基准对比功能
- [ ] 支持导出Excel/PDF报告

## 许可证

MIT License

## 联系方式

如有问题或建议，请提交Issue或Pull Request。