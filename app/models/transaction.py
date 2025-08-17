"""
交易记录模型
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum


class TransactionType(Enum):
    """交易类型"""
    BUY = "buy"
    SELL = "sell"
    REBALANCE = "rebalance"
    DCA = "dca"


class BuyReason(Enum):
    """买入原因"""
    INITIAL = "初始买入"
    REBALANCE = "再平衡"
    DCA_PERIODIC = "定期定投"
    PRICE_DROP = "价格下跌"
    DRAWDOWN = "回撤触发"
    VIX_HIGH = "VIX高位"
    RSI_OVERSOLD = "RSI超卖"
    MACD_GOLDEN_CROSS = "MACD金叉"
    SUPPORT_LEVEL = "支撑位"
    CUSTOM = "自定义条件"


@dataclass
class Transaction:
    """交易记录"""
    date: datetime
    symbol: str
    transaction_type: TransactionType
    shares: float
    price: float
    amount: float
    reason: str
    reason_code: BuyReason
    details: Dict[str, Any]
    portfolio_value_before: float
    portfolio_value_after: float
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'date': self.date.strftime('%Y-%m-%d'),
            'symbol': self.symbol,
            'type': self.transaction_type.value,
            'shares': round(self.shares, 4),
            'price': round(self.price, 2),
            'amount': round(self.amount, 2),
            'reason': self.reason,
            'reason_code': self.reason_code.value,
            'details': self.details,
            'portfolio_value_before': round(self.portfolio_value_before, 2),
            'portfolio_value_after': round(self.portfolio_value_after, 2)
        }


class TransactionAnalyzer:
    """交易分析器"""
    
    @staticmethod
    def check_buy_signals(
        current_price: float,
        price_history: list,
        indicators: Dict[str, Any],
        config: Dict[str, Any]
    ) -> tuple[bool, str, BuyReason, Dict[str, Any]]:
        """
        检查买入信号
        
        Returns:
            (是否买入, 原因描述, 原因代码, 详细信息)
        """
        details = {}
        
        # 1. 检查日内跌幅
        if len(price_history) >= 2:
            daily_return = (current_price - price_history[-2]) / price_history[-2]
            drop_threshold = config.get('daily_drop_threshold', -0.05)
            if daily_return <= drop_threshold:  # 跌幅超过阈值
                details['daily_return'] = f"{daily_return:.2%}"
                details['trigger_threshold'] = f"{drop_threshold:.1%}"
                return (True, 
                       f"当日跌幅{daily_return:.2%}，触发买入",
                       BuyReason.PRICE_DROP,
                       details)
        
        # 2. 检查回撤
        if 'drawdown' in indicators:
            drawdown = indicators['drawdown']
            drawdown_threshold = config.get('drawdown_threshold', -0.10)
            if drawdown <= drawdown_threshold:  # 回撤超过阈值
                details['drawdown'] = f"{drawdown:.2%}"
                details['trigger_threshold'] = f"{drawdown_threshold:.1%}"
                return (True,
                       f"回撤{drawdown:.2%}，触发买入",
                       BuyReason.DRAWDOWN,
                       details)
        
        # 3. 检查VIX指标
        if 'vix' in indicators:
            vix = indicators['vix']
            vix_threshold = config.get('vix_threshold', 30)
            if vix > vix_threshold:
                details['vix'] = f"{vix:.2f}"
                details['trigger_threshold'] = str(vix_threshold)
                return (True,
                       f"VIX指数{vix:.2f}超过阈值{vix_threshold}",
                       BuyReason.VIX_HIGH,
                       details)
        
        # 4. 检查RSI超卖
        if 'rsi' in indicators:
            rsi = indicators['rsi']
            rsi_threshold = config.get('rsi_oversold', 30)
            if rsi < rsi_threshold:  # RSI低于阈值视为超卖
                details['rsi'] = f"{rsi:.2f}"
                details['trigger_threshold'] = str(rsi_threshold)
                return (True,
                       f"RSI指标{rsi:.2f}，超卖信号",
                       BuyReason.RSI_OVERSOLD,
                       details)
        
        # 5. 检查MACD金叉
        if 'macd' in indicators and 'macd_signal' in indicators:
            macd = indicators['macd']
            signal = indicators['macd_signal']
            prev_macd = indicators.get('prev_macd', 0)
            prev_signal = indicators.get('prev_signal', 0)
            
            # 金叉：MACD从下向上穿过Signal线
            if prev_macd <= prev_signal and macd > signal:
                details['macd'] = f"{macd:.4f}"
                details['signal'] = f"{signal:.4f}"
                return (True,
                       f"MACD金叉信号",
                       BuyReason.MACD_GOLDEN_CROSS,
                       details)
        
        # 6. 检查支撑位
        if 'support_level' in indicators:
            support = indicators['support_level']
            if current_price <= support * 1.02:  # 接近支撑位（2%范围内）
                details['price'] = f"{current_price:.2f}"
                details['support_level'] = f"{support:.2f}"
                return (True,
                       f"价格{current_price:.2f}接近支撑位{support:.2f}",
                       BuyReason.SUPPORT_LEVEL,
                       details)
        
        return (False, "", BuyReason.CUSTOM, {})
    
    @staticmethod
    def analyze_transactions(transactions: list) -> Dict[str, Any]:
        """分析交易记录"""
        if not transactions:
            return {}
        
        buy_transactions = [t for t in transactions if t.transaction_type == TransactionType.BUY]
        sell_transactions = [t for t in transactions if t.transaction_type == TransactionType.SELL]
        
        # 按原因分组统计
        reason_stats = {}
        for t in buy_transactions:
            reason = t.reason_code.value
            if reason not in reason_stats:
                reason_stats[reason] = {
                    'count': 0,
                    'total_amount': 0,
                    'transactions': []
                }
            reason_stats[reason]['count'] += 1
            reason_stats[reason]['total_amount'] += t.amount
            reason_stats[reason]['transactions'].append(t.to_dict())
        
        # 计算收益
        total_buy_amount = sum(t.amount for t in buy_transactions)
        total_sell_amount = sum(t.amount for t in sell_transactions)
        
        return {
            'total_transactions': len(transactions),
            'buy_count': len(buy_transactions),
            'sell_count': len(sell_transactions),
            'total_buy_amount': total_buy_amount,
            'total_sell_amount': total_sell_amount,
            'reason_statistics': reason_stats,
            'all_transactions': [t.to_dict() for t in transactions]
        }