"""
投资组合控制器
处理投资组合相关的HTTP请求
"""
from flask import Blueprint, request, jsonify
from app.dao.portfolio_dao import PortfolioDAO


portfolio_bp = Blueprint('portfolio', __name__)
portfolio_dao = PortfolioDAO()


@portfolio_bp.route('/api/portfolio/create', methods=['POST'])
def create_portfolio():
    """创建投资组合"""
    try:
        data = request.json
        
        # 验证请求数据
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # 验证必需字段
        required_fields = ['name', 'assets']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # 验证资产配置
        assets = data['assets']
        if not assets:
            return jsonify({'error': 'At least one asset is required'}), 400
        
        # 验证权重总和
        total_weight = sum(asset.get('weight', 0) for asset in assets)
        if abs(total_weight - 100.0) > 0.01:
            return jsonify({'error': f'Weights must sum to 100%, got {total_weight}%'}), 400
        
        # 创建投资组合
        portfolio_id = portfolio_dao.create_portfolio(data)
        
        return jsonify({
            'portfolio_id': portfolio_id,
            'message': 'Portfolio created successfully'
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@portfolio_bp.route('/api/portfolio/<portfolio_id>', methods=['GET'])
def get_portfolio(portfolio_id):
    """获取投资组合详情"""
    try:
        portfolio = portfolio_dao.get_portfolio(portfolio_id)
        
        if not portfolio:
            return jsonify({'error': 'Portfolio not found'}), 404
        
        return jsonify(portfolio), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@portfolio_bp.route('/api/portfolio/<portfolio_id>', methods=['PUT'])
def update_portfolio(portfolio_id):
    """更新投资组合"""
    try:
        data = request.json
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # 如果提供了资产配置，验证权重
        if 'assets' in data:
            assets = data['assets']
            if assets:
                total_weight = sum(asset.get('weight', 0) for asset in assets)
                if abs(total_weight - 100.0) > 0.01:
                    return jsonify({'error': f'Weights must sum to 100%, got {total_weight}%'}), 400
        
        # 更新投资组合
        success = portfolio_dao.update_portfolio(portfolio_id, data)
        
        if not success:
            return jsonify({'error': 'Portfolio not found'}), 404
        
        return jsonify({
            'portfolio_id': portfolio_id,
            'message': 'Portfolio updated successfully'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@portfolio_bp.route('/api/portfolio/<portfolio_id>', methods=['DELETE'])
def delete_portfolio(portfolio_id):
    """删除投资组合"""
    try:
        success = portfolio_dao.delete_portfolio(portfolio_id)
        
        if not success:
            return jsonify({'error': 'Portfolio not found'}), 404
        
        return jsonify({
            'portfolio_id': portfolio_id,
            'message': 'Portfolio deleted successfully'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@portfolio_bp.route('/api/portfolio/list', methods=['GET'])
def list_portfolios():
    """获取投资组合列表"""
    try:
        limit = request.args.get('limit', 10, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        portfolios = portfolio_dao.list_portfolios(limit, offset)
        
        return jsonify({
            'portfolios': portfolios,
            'limit': limit,
            'offset': offset,
            'total': len(portfolios)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@portfolio_bp.route('/api/portfolio/templates', methods=['GET'])
def get_portfolio_templates():
    """获取投资组合模板"""
    try:
        templates = [
            {
                'id': 'conservative',
                'name': 'Conservative Portfolio',
                'description': 'Low risk portfolio with focus on bonds',
                'assets': [
                    {'symbol': 'BND', 'name': 'Vanguard Total Bond Market ETF', 'weight': 60.0},
                    {'symbol': 'VTI', 'name': 'Vanguard Total Stock Market ETF', 'weight': 30.0},
                    {'symbol': 'VXUS', 'name': 'Vanguard Total International Stock ETF', 'weight': 10.0}
                ]
            },
            {
                'id': 'balanced',
                'name': 'Balanced Portfolio',
                'description': 'Balanced risk portfolio with mix of stocks and bonds',
                'assets': [
                    {'symbol': 'VTI', 'name': 'Vanguard Total Stock Market ETF', 'weight': 40.0},
                    {'symbol': 'BND', 'name': 'Vanguard Total Bond Market ETF', 'weight': 30.0},
                    {'symbol': 'VXUS', 'name': 'Vanguard Total International Stock ETF', 'weight': 20.0},
                    {'symbol': 'VNQ', 'name': 'Vanguard Real Estate ETF', 'weight': 10.0}
                ]
            },
            {
                'id': 'aggressive',
                'name': 'Aggressive Growth Portfolio',
                'description': 'High risk portfolio focused on growth stocks',
                'assets': [
                    {'symbol': 'QQQ', 'name': 'Invesco QQQ Trust', 'weight': 30.0},
                    {'symbol': 'VGT', 'name': 'Vanguard Information Technology ETF', 'weight': 25.0},
                    {'symbol': 'ARKK', 'name': 'ARK Innovation ETF', 'weight': 20.0},
                    {'symbol': 'VWO', 'name': 'Vanguard Emerging Markets ETF', 'weight': 15.0},
                    {'symbol': 'VNQ', 'name': 'Vanguard Real Estate ETF', 'weight': 10.0}
                ]
            },
            {
                'id': 'tech_focused',
                'name': 'Technology Focus Portfolio',
                'description': 'Portfolio focused on technology sector',
                'assets': [
                    {'symbol': 'AAPL', 'name': 'Apple Inc.', 'weight': 25.0},
                    {'symbol': 'MSFT', 'name': 'Microsoft Corporation', 'weight': 25.0},
                    {'symbol': 'GOOGL', 'name': 'Alphabet Inc.', 'weight': 20.0},
                    {'symbol': 'NVDA', 'name': 'NVIDIA Corporation', 'weight': 15.0},
                    {'symbol': 'META', 'name': 'Meta Platforms Inc.', 'weight': 15.0}
                ]
            }
        ]
        
        return jsonify(templates), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@portfolio_bp.route('/api/portfolio/<portfolio_id>/clone', methods=['POST'])
def clone_portfolio(portfolio_id):
    """克隆投资组合"""
    try:
        data = request.json
        new_name = data.get('name', 'Cloned Portfolio')
        
        # 获取原始投资组合
        original = portfolio_dao.get_portfolio(portfolio_id)
        
        if not original:
            return jsonify({'error': 'Portfolio not found'}), 404
        
        # 创建克隆
        clone_data = {
            'name': new_name,
            'assets': original['assets'],
            'description': f"Cloned from {original['name']}"
        }
        
        new_portfolio_id = portfolio_dao.create_portfolio(clone_data)
        
        return jsonify({
            'portfolio_id': new_portfolio_id,
            'message': 'Portfolio cloned successfully'
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500