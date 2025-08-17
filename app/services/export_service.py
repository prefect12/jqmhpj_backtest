"""
数据导出服务
支持Excel和PDF格式导出
"""
import pandas as pd
import json
from io import BytesIO
from typing import Dict, Any
from datetime import datetime
import xlsxwriter


class ExportService:
    """数据导出服务"""
    
    def export_to_excel(self, backtest_result: Dict[str, Any]) -> BytesIO:
        """
        导出回测结果到Excel
        
        Args:
            backtest_result: 回测结果数据
        
        Returns:
            Excel文件的字节流
        """
        output = BytesIO()
        
        # 创建Excel writer
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            workbook = writer.book
            
            # 定义格式
            header_format = workbook.add_format({
                'bold': True,
                'bg_color': '#667eea',
                'font_color': 'white',
                'border': 1
            })
            
            percent_format = workbook.add_format({
                'num_format': '0.00%',
                'border': 1
            })
            
            currency_format = workbook.add_format({
                'num_format': '$#,##0.00',
                'border': 1
            })
            
            # 1. 概览页
            summary_data = {
                '指标': [
                    '开始日期',
                    '结束日期',
                    '初始金额',
                    '最终金额',
                    '总收益率',
                    '年化收益率',
                    '最大回撤',
                    '夏普比率',
                    '索提诺比率',
                    '年化波动率'
                ],
                '值': [
                    backtest_result.get('config_summary', {}).get('start_date', ''),
                    backtest_result.get('config_summary', {}).get('end_date', ''),
                    backtest_result.get('performance_summary', {}).get('start_value', 0),
                    backtest_result.get('performance_summary', {}).get('end_value', 0),
                    backtest_result.get('performance_summary', {}).get('total_return_pct', 0) / 100,
                    backtest_result.get('performance_summary', {}).get('annualized_return_pct', 0) / 100,
                    backtest_result.get('risk_metrics', {}).get('max_drawdown_pct', 0) / 100,
                    backtest_result.get('risk_metrics', {}).get('sharpe_ratio', 0),
                    backtest_result.get('risk_metrics', {}).get('sortino_ratio', 0),
                    backtest_result.get('risk_metrics', {}).get('volatility_annual_pct', 0) / 100
                ]
            }
            
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='概览', index=False)
            
            # 格式化概览表
            worksheet = writer.sheets['概览']
            worksheet.set_column('A:A', 20)
            worksheet.set_column('B:B', 15)
            
            # 2. 投资组合构成
            if 'portfolio_composition' in backtest_result:
                portfolio_df = pd.DataFrame(backtest_result['portfolio_composition'])
                portfolio_df.to_excel(writer, sheet_name='投资组合', index=False)
                
                worksheet = writer.sheets['投资组合']
                worksheet.set_column('A:A', 15)
                worksheet.set_column('B:B', 15)
            
            # 3. 年度收益
            if 'annual_returns' in backtest_result:
                annual_df = pd.DataFrame(backtest_result['annual_returns'])
                annual_df.to_excel(writer, sheet_name='年度收益', index=False)
                
                worksheet = writer.sheets['年度收益']
                worksheet.set_column('A:F', 15)
            
            # 4. 时间序列数据
            if 'time_series' in backtest_result:
                ts_df = pd.DataFrame(backtest_result['time_series'])
                ts_df.to_excel(writer, sheet_name='净值走势', index=False)
                
                worksheet = writer.sheets['净值走势']
                worksheet.set_column('A:C', 15)
            
            # 5. 基准对比（如果有）
            if 'benchmark_comparison' in backtest_result and backtest_result['benchmark_comparison']:
                benchmark_data = backtest_result['benchmark_comparison']
                benchmark_summary = {
                    '指标': [
                        '基准代码',
                        '基准收益率',
                        '基准年化收益率',
                        '超额收益',
                        '跟踪误差',
                        '信息比率',
                        '相关性'
                    ],
                    '值': [
                        benchmark_data.get('benchmark_symbol', ''),
                        benchmark_data.get('benchmark_return_pct', 0) / 100,
                        benchmark_data.get('benchmark_annualized_return_pct', 0) / 100,
                        benchmark_data.get('excess_return_pct', 0) / 100,
                        benchmark_data.get('tracking_error_pct', 0) / 100,
                        benchmark_data.get('information_ratio', 0),
                        benchmark_data.get('correlation', 0)
                    ]
                }
                
                benchmark_df = pd.DataFrame(benchmark_summary)
                benchmark_df.to_excel(writer, sheet_name='基准对比', index=False)
        
        output.seek(0)
        return output
    
    def export_to_csv(self, backtest_result: Dict[str, Any]) -> str:
        """
        导出回测结果到CSV
        
        Args:
            backtest_result: 回测结果数据
        
        Returns:
            CSV格式的字符串
        """
        # 准备数据
        rows = []
        
        # 添加概览信息
        rows.append(['回测结果报告'])
        rows.append(['生成时间', datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
        rows.append([])
        
        rows.append(['基本信息'])
        rows.append(['开始日期', backtest_result.get('config_summary', {}).get('start_date', '')])
        rows.append(['结束日期', backtest_result.get('config_summary', {}).get('end_date', '')])
        rows.append(['初始金额', backtest_result.get('performance_summary', {}).get('start_value', 0)])
        rows.append([])
        
        rows.append(['收益指标'])
        rows.append(['最终金额', backtest_result.get('performance_summary', {}).get('end_value', 0)])
        rows.append(['总收益率(%)', backtest_result.get('performance_summary', {}).get('total_return_pct', 0)])
        rows.append(['年化收益率(%)', backtest_result.get('performance_summary', {}).get('annualized_return_pct', 0)])
        rows.append([])
        
        rows.append(['风险指标'])
        rows.append(['最大回撤(%)', backtest_result.get('risk_metrics', {}).get('max_drawdown_pct', 0)])
        rows.append(['年化波动率(%)', backtest_result.get('risk_metrics', {}).get('volatility_annual_pct', 0)])
        rows.append(['夏普比率', backtest_result.get('risk_metrics', {}).get('sharpe_ratio', 0)])
        rows.append(['索提诺比率', backtest_result.get('risk_metrics', {}).get('sortino_ratio', 0)])
        rows.append([])
        
        # 添加投资组合构成
        if 'portfolio_composition' in backtest_result:
            rows.append(['投资组合构成'])
            rows.append(['股票代码', '权重(%)'])
            for asset in backtest_result['portfolio_composition']:
                rows.append([asset['symbol'], asset['weight']])
            rows.append([])
        
        # 转换为CSV字符串
        df = pd.DataFrame(rows)
        csv_string = df.to_csv(index=False, header=False)
        
        return csv_string
    
    def export_to_json(self, backtest_result: Dict[str, Any]) -> str:
        """
        导出回测结果到JSON
        
        Args:
            backtest_result: 回测结果数据
        
        Returns:
            格式化的JSON字符串
        """
        # 添加导出时间戳
        export_data = {
            'export_time': datetime.now().isoformat(),
            'backtest_result': backtest_result
        }
        
        return json.dumps(export_data, indent=2, ensure_ascii=False)
    
    def generate_report_html(self, backtest_result: Dict[str, Any]) -> str:
        """
        生成HTML格式的报告
        
        Args:
            backtest_result: 回测结果数据
        
        Returns:
            HTML格式的报告字符串
        """
        perf = backtest_result.get('performance_summary', {})
        risk = backtest_result.get('risk_metrics', {})
        config = backtest_result.get('config_summary', {})
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>回测报告 - {config.get('start_date')} 至 {config.get('end_date')}</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 40px;
                    background: #f5f5f5;
                }}
                .container {{
                    max-width: 1000px;
                    margin: 0 auto;
                    background: white;
                    padding: 30px;
                    border-radius: 10px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }}
                h1 {{
                    color: #333;
                    border-bottom: 3px solid #667eea;
                    padding-bottom: 10px;
                }}
                h2 {{
                    color: #666;
                    margin-top: 30px;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin: 20px 0;
                }}
                th {{
                    background: #667eea;
                    color: white;
                    padding: 12px;
                    text-align: left;
                }}
                td {{
                    padding: 10px;
                    border-bottom: 1px solid #ddd;
                }}
                .positive {{
                    color: #28a745;
                    font-weight: bold;
                }}
                .negative {{
                    color: #dc3545;
                    font-weight: bold;
                }}
                .metric-card {{
                    display: inline-block;
                    background: #f8f9fa;
                    padding: 20px;
                    margin: 10px;
                    border-radius: 8px;
                    min-width: 200px;
                }}
                .metric-value {{
                    font-size: 24px;
                    font-weight: bold;
                    color: #333;
                }}
                .metric-label {{
                    color: #666;
                    margin-top: 5px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>回测分析报告</h1>
                
                <h2>核心指标</h2>
                <div>
                    <div class="metric-card">
                        <div class="metric-value {'positive' if perf.get('total_return_pct', 0) >= 0 else 'negative'}">
                            {perf.get('total_return_pct', 0):.2f}%
                        </div>
                        <div class="metric-label">总收益率</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value {'positive' if perf.get('annualized_return_pct', 0) >= 0 else 'negative'}">
                            {perf.get('annualized_return_pct', 0):.2f}%
                        </div>
                        <div class="metric-label">年化收益率</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value negative">
                            {risk.get('max_drawdown_pct', 0):.2f}%
                        </div>
                        <div class="metric-label">最大回撤</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">
                            {risk.get('sharpe_ratio', 0):.2f}
                        </div>
                        <div class="metric-label">夏普比率</div>
                    </div>
                </div>
                
                <h2>详细指标</h2>
                <table>
                    <tr>
                        <th>指标</th>
                        <th>值</th>
                    </tr>
                    <tr>
                        <td>投资期间</td>
                        <td>{config.get('start_date', '')} 至 {config.get('end_date', '')}</td>
                    </tr>
                    <tr>
                        <td>初始金额</td>
                        <td>${perf.get('start_value', 0):,.2f}</td>
                    </tr>
                    <tr>
                        <td>最终金额</td>
                        <td>${perf.get('end_value', 0):,.2f}</td>
                    </tr>
                    <tr>
                        <td>总收益</td>
                        <td>${perf.get('end_value', 0) - perf.get('start_value', 0):,.2f}</td>
                    </tr>
                    <tr>
                        <td>年化波动率</td>
                        <td>{risk.get('volatility_annual_pct', 0):.2f}%</td>
                    </tr>
                    <tr>
                        <td>索提诺比率</td>
                        <td>{risk.get('sortino_ratio', 0):.2f}</td>
                    </tr>
                    <tr>
                        <td>正收益率</td>
                        <td>{risk.get('positive_rate_pct', 0):.2f}%</td>
                    </tr>
                </table>
                
                <p style="text-align: center; color: #999; margin-top: 40px;">
                    报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                </p>
            </div>
        </body>
        </html>
        """
        
        return html