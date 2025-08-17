# UI设计分析文档

基于Portfolio Visualizer设计稿的分析，为我们的股票回测网站设计UI界面规范。

## 设计稿分析总结

### 1. 整体布局特点
- **清晰的信息层次**: 使用标题、副标题、表格等明确的信息结构
- **专业的数据展示**: 大量使用表格和图表展示财务数据
- **蓝色主色调**: 以蓝色为主色调，体现金融专业性
- **简洁的设计风格**: 注重内容而非装饰性元素

### 2. 核心展示模块

#### A. 滚动收益表 (Rolling Returns)
- **数据结构**: 时间周期 × 投资组合对比表格
- **颜色编码**: 负数用红色，正数用黑色
- **包含字段**: Average, High, Low 收益率

#### B. 风险收益指标表 (Risk and Return Metrics)
- **全面的指标**: 26个专业财务指标
- **对比展示**: 投资组合 vs 基准指数
- **指标分类**: 
  - 收益指标: 几何/算术平均收益
  - 风险指标: 标准差、最大回撤、VaR
  - 风险调整收益: 夏普比率、索提诺比率等
  - 相对指标: Alpha、Beta、相关性等

#### C. 投资组合分解分析
- **收益分解**: 各资产对总收益的贡献金额
- **风险分解**: 各资产对总风险的贡献百分比
- **资产表现**: 个股的详细表现指标

#### D. 相关性矩阵 (Monthly Correlations)
- **热力图样式**: 用颜色深浅表示相关性强弱
- **对称矩阵**: 标准的相关性展示格式

#### E. 图表组件
1. **滚动收益时间序列图**
   - 双线对比 (投资组合 vs 基准)
   - 时间轴清晰标注
   - 网格线辅助读数

2. **年度资产收益柱状图**
   - 多色彩区分不同资产
   - 正负收益颜色区分
   - 时间轴标注年份

3. **回撤图表**
   - 从0%基线向下显示回撤
   - 双线对比格式
   - 突出最大回撤期间

4. **饼图分析**
   - 资产配置饼图
   - 市值分布饼图
   - 行业配置饼图
   - 信用质量分布

## UI设计规范

### 1. 颜色体系

#### 主色调
```css
/* 主蓝色 - Portfolio Visualizer风格 */
--primary-blue: #3B82F6
--dark-blue: #1E40AF
--light-blue: #DBEAFE

/* 功能色彩 */
--success-green: #10B981
--warning-yellow: #F59E0B
--danger-red: #EF4444
--neutral-gray: #6B7280
```

#### 数据展示色彩
```css
/* 收益率颜色 */
--positive-return: #000000  /* 黑色 */
--negative-return: #EF4444  /* 红色 */
--neutral-return: #6B7280   /* 灰色 */

/* 图表色彩 */
--chart-primary: #3B82F6    /* 主线条 */
--chart-secondary: #10B981  /* 对比线条 */
--chart-background: #F8FAFC /* 图表背景 */
```

### 2. 表格设计规范

#### 标准数据表格
```css
.data-table {
  border-collapse: collapse;
  width: 100%;
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.data-table th {
  background-color: #F8FAFC;
  padding: 12px 16px;
  text-align: left;
  font-weight: 600;
  border-bottom: 1px solid #E5E7EB;
}

.data-table td {
  padding: 12px 16px;
  border-bottom: 1px solid #F3F4F6;
}

/* 数值对齐 */
.data-table .number {
  text-align: right;
  font-family: 'SF Mono', monospace;
}

/* 收益率着色 */
.positive { color: #000000; }
.negative { color: #EF4444; }
```

#### 指标表格样式
```css
.metrics-table {
  margin: 24px 0;
}

.metrics-table .metric-name {
  font-weight: 500;
  color: #374151;
}

.metrics-table .metric-value {
  font-weight: 600;
  font-family: 'SF Mono', monospace;
}
```

### 3. 图表设计规范

#### Chart.js 配置标准
```javascript
const chartConfig = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'bottom',
      labels: {
        usePointStyle: true,
        padding: 20
      }
    },
    title: {
      display: true,
      font: {
        size: 16,
        weight: '600'
      },
      color: '#1F2937'
    }
  },
  scales: {
    x: {
      grid: {
        color: '#F3F4F6'
      },
      ticks: {
        color: '#6B7280'
      }
    },
    y: {
      grid: {
        color: '#F3F4F6'
      },
      ticks: {
        color: '#6B7280',
        callback: function(value) {
          return value.toFixed(1) + '%';
        }
      }
    }
  }
};
```

### 4. 页面布局规范

#### 主要内容区域
```css
.main-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px;
}

.section {
  margin-bottom: 32px;
  background: white;
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  color: #1F2937;
  margin-bottom: 16px;
  border-bottom: 2px solid #3B82F6;
  padding-bottom: 8px;
}
```

#### 响应式布局
```css
/* 桌面端 */
@media (min-width: 1024px) {
  .two-column {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 24px;
  }
}

/* 移动端 */
@media (max-width: 768px) {
  .main-content {
    padding: 16px;
  }
  
  .section {
    padding: 16px;
  }
  
  .data-table {
    font-size: 14px;
  }
}
```

## 核心页面设计

### 1. 首页布局
```
┌─────────────────────────────────────────┐
│              导航栏                      │
├─────────────────────────────────────────┤
│              投资组合配置                │
│  - 股票选择                              │
│  - 权重设置                              │
│  - 时间范围                              │
│  - 初始金额                              │
├─────────────────────────────────────────┤
│              [开始回测] 按钮             │
└─────────────────────────────────────────┘
```

### 2. 回测结果页面布局
```
┌─────────────────────────────────────────┐
│              导航栏                      │
├─────────────────────────────────────────┤
│              核心指标摘要                │
│  收益率 | 风险 | 夏普比率 | 最大回撤      │
├─────────────────────────────────────────┤
│              投资组合增长图              │
│                                         │
├─────────────────┬───────────────────────┤
│  投资组合配置表  │     风险收益指标表     │
│                 │                       │
├─────────────────┴───────────────────────┤
│              年度收益表现                │
│                                         │
├─────────────────────────────────────────┤
│              滚动收益分析                │
│                                         │
└─────────────────────────────────────────┘
```

### 3. 组件优先级

#### MVP版本必需组件
1. **投资组合配置表单**
2. **核心指标摘要卡片**
3. **投资组合增长线图**
4. **年度收益柱状图** 
5. **基础数据表格**

#### 后续版本扩展组件
1. **滚动收益图表**
2. **回撤分析图表**
3. **相关性热力图**
4. **行业配置饼图**
5. **详细指标表格**

## 交互设计要求

### 1. 表单交互
- 实时输入验证
- 权重自动计算
- 股票代码自动补全
- 错误状态提示

### 2. 图表交互
- 鼠标悬停数据提示
- 图例点击显示/隐藏
- 缩放和平移功能
- 数据点高亮显示

### 3. 页面交互
- 加载状态指示器
- 结果数据懒加载
- 平滑滚动锚点
- 响应式菜单折叠

## 开发实现建议

### 1. CSS框架选择
推荐使用 **Tailwind CSS**:
- 与设计稿颜色体系匹配
- 灵活的工具类系统
- 优秀的响应式支持

### 2. 图表库选择
推荐使用 **Chart.js**:
- 轻量级且功能完整
- 良好的自定义能力
- 支持响应式设计

### 3. 组件化开发
建议创建可复用组件:
- `DataTable`: 数据表格组件
- `MetricCard`: 指标卡片组件
- `ChartContainer`: 图表容器组件
- `LoadingSpinner`: 加载动画组件