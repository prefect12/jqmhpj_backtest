# 开发文档目录

本目录包含股票回测分析网站项目的所有设计和开发文档。

## 📚 文档列表

### 1. 需求与规划
- **[requirements.md](requirements.md)** - 项目需求文档，定义核心功能模块
- **[mvp_definition.md](mvp_definition.md)** - MVP版本定义，包含输入输出数据结构

### 2. 技术架构
- **[architecture_design.md](architecture_design.md)** - 分层架构设计（DAO/Service/Controller）
- **[tech_architecture.md](tech_architecture.md)** - 技术栈选择和系统设计
- **[api_specification.md](api_specification.md)** - REST API接口规范

### 3. 配置与环境
- **[environment_config.md](environment_config.md)** - 环境变量配置规范

### 4. UI设计
- **[ui_design_analysis.md](ui_design_analysis.md)** - 基于Portfolio Visualizer的UI设计分析

### 5. 测试规范
- **[testing_guidelines.md](testing_guidelines.md)** - 单元测试编写规范和要求

## 🚀 快速开始

1. **阅读顺序建议**：
   - 先看 `requirements.md` 了解项目需求
   - 再看 `architecture_design.md` 理解系统架构
   - 查看 `mvp_definition.md` 了解具体的输入输出
   - 参考 `testing_guidelines.md` 编写测试

2. **开发流程**：
   - 每个模块开发前先查阅相关设计文档
   - 开发完成后按照测试规范编写单元测试
   - 遵循架构设计中的分层原则

## 📋 文档维护

- 文档应随着项目开发持续更新
- 重大设计变更需要更新相应文档
- 新增功能需要补充到需求文档中

## 🔗 相关资源

- 项目根目录的 `CLAUDE.md` 包含项目指导原则
- `design_image/` 文件夹包含UI设计参考图片
- `.env.example` 提供环境变量配置模板