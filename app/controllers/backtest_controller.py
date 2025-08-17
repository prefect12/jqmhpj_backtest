"""
回测控制器
处理回测相关的HTTP请求
"""
from flask import Blueprint, request, jsonify, send_file, make_response
from app.services.backtest_service import BacktestService
from app.services.dca_service import DCAService
from app.services.export_service import ExportService
from app.dao.backtest_dao import BacktestDAO
from app.dao.portfolio_dao import PortfolioDAO
from app.dao.stock_data_dao import StockDataDAO
import json


backtest_bp = Blueprint('backtest', __name__)
backtest_service = BacktestService()
dca_service = DCAService()
export_service = ExportService()
backtest_dao = BacktestDAO()
portfolio_dao = PortfolioDAO()
stock_dao = StockDataDAO()


@backtest_bp.route('/api/backtest/run', methods=['POST'])
def run_backtest():
    """执行基础回测"""
    try:
        data = request.json
        
        # 验证请求数据
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # 执行回测
        result = backtest_service.run_backtest(data)
        
        # 保存回测结果（简化处理，暂不保存到数据库）
        # if result['status'] == 'completed':
        #     backtest_dao.save_backtest_result(result)
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@backtest_bp.route('/api/backtest/dca/periodic', methods=['POST'])
def run_periodic_dca():
    """执行定期定投回测"""
    try:
        data = request.json
        
        # 验证请求数据
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # 执行定投回测
        result = dca_service.run_periodic_dca(data)
        
        # 保存结果（暂时注释）
        # if result['status'] == 'completed':
        #     backtest_dao.save_backtest(result)
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@backtest_bp.route('/api/backtest/dca/conditional', methods=['POST'])
def run_conditional_dca():
    """执行条件定投回测"""
    try:
        data = request.json
        
        # 验证请求数据
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # 执行条件定投回测
        result = dca_service.run_conditional_dca(data)
        
        # 保存结果（暂时注释）
        # if result['status'] == 'completed':
        #     backtest_dao.save_backtest(result)
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@backtest_bp.route('/api/backtest/<backtest_id>', methods=['GET'])
def get_backtest(backtest_id):
    """获取回测结果"""
    try:
        result = backtest_dao.get_backtest(backtest_id)
        
        if not result:
            return jsonify({'error': 'Backtest not found'}), 404
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@backtest_bp.route('/api/backtest/history', methods=['GET'])
def get_backtest_history():
    """获取回测历史记录"""
    try:
        limit = request.args.get('limit', 10, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        results = backtest_dao.get_backtest_history(limit, offset)
        
        return jsonify({
            'results': results,
            'limit': limit,
            'offset': offset,
            'total': len(results)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@backtest_bp.route('/api/stocks/search', methods=['GET'])
def search_stocks():
    """搜索股票"""
    try:
        query = request.args.get('q', '')
        limit = request.args.get('limit', 10, type=int)
        
        if not query:
            return jsonify({'error': 'Query parameter required'}), 400
        
        results = stock_dao.search_stocks(query, limit)
        
        return jsonify({
            'results': results,
            'query': query,
            'count': len(results)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@backtest_bp.route('/api/stocks/validate', methods=['POST'])
def validate_stocks():
    """验证股票代码"""
    try:
        data = request.json
        symbols = data.get('symbols', [])
        
        if not symbols:
            return jsonify({'error': 'No symbols provided'}), 400
        
        results = {}
        for symbol in symbols:
            results[symbol] = stock_dao.validate_symbol(symbol)
        
        return jsonify({
            'results': results,
            'valid_count': sum(1 for v in results.values() if v),
            'invalid_count': sum(1 for v in results.values() if not v)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@backtest_bp.route('/api/stocks/info/<symbol>', methods=['GET'])
def get_stock_info(symbol):
    """获取股票基本信息"""
    try:
        info = stock_dao.get_stock_info(symbol)
        return jsonify(info), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@backtest_bp.route('/api/stocks/batch-info', methods=['POST'])
def get_batch_stock_info():
    """批量获取股票信息"""
    try:
        data = request.json
        symbols = data.get('symbols', [])
        
        if not symbols:
            return jsonify({'error': 'No symbols provided'}), 400
        
        results = {}
        for symbol in symbols:
            try:
                results[symbol] = stock_dao.get_stock_info(symbol)
            except:
                results[symbol] = {'error': 'Failed to fetch info'}
        
        return jsonify(results), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@backtest_bp.route('/api/backtest/export/<format>', methods=['POST'])
def export_backtest(format):
    """导出回测结果"""
    try:
        data = request.json
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        if format == 'excel':
            # 导出Excel
            excel_file = export_service.export_to_excel(data)
            return send_file(
                excel_file,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                as_attachment=True,
                download_name=f'backtest_report_{data.get("backtest_id", "result")}.xlsx'
            )
        
        elif format == 'csv':
            # 导出CSV
            csv_content = export_service.export_to_csv(data)
            response = make_response(csv_content)
            response.headers['Content-Type'] = 'text/csv'
            response.headers['Content-Disposition'] = f'attachment; filename=backtest_report_{data.get("backtest_id", "result")}.csv'
            return response
        
        elif format == 'json':
            # 导出JSON
            json_content = export_service.export_to_json(data)
            response = make_response(json_content)
            response.headers['Content-Type'] = 'application/json'
            response.headers['Content-Disposition'] = f'attachment; filename=backtest_report_{data.get("backtest_id", "result")}.json'
            return response
        
        elif format == 'html':
            # 导出HTML报告
            html_content = export_service.generate_report_html(data)
            response = make_response(html_content)
            response.headers['Content-Type'] = 'text/html'
            return response
        
        else:
            return jsonify({'error': f'Unsupported format: {format}'}), 400
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500