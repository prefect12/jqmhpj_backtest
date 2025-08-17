#!/usr/bin/env python
"""
简单测试交易记录功能
"""
import json
from datetime import datetime
from app.models.transaction import Transaction, TransactionType, BuyReason

def test_transaction_model():
    """测试交易记录模型"""
    
    # 创建一个交易记录
    transaction = Transaction(
        date=datetime(2023, 3, 15),
        symbol="AAPL",
        transaction_type=TransactionType.BUY,
        shares=10,
        price=150.50,
        amount=1505.00,
        reason="当日跌幅-3.5%，触发买入",
        reason_code=BuyReason.PRICE_DROP,
        details={'daily_return': '-3.5%', 'trigger_threshold': '-3.0%'},
        portfolio_value_before=10000,
        portfolio_value_after=11505
    )
    
    # 转换为字典
    tx_dict = transaction.to_dict()
    
    print("✅ 交易记录创建成功！")
    print(json.dumps(tx_dict, indent=2, ensure_ascii=False))
    
    # 测试多个交易记录
    transactions = [
        Transaction(
            date=datetime(2023, 1, 1),
            symbol="AAPL",
            transaction_type=TransactionType.BUY,
            shares=33.33,
            price=150,
            amount=5000,
            reason="初始建仓",
            reason_code=BuyReason.INITIAL,
            details={'initial_weight': 50},
            portfolio_value_before=10000,
            portfolio_value_after=10000
        ),
        Transaction(
            date=datetime(2023, 1, 1),
            symbol="MSFT",
            transaction_type=TransactionType.BUY,
            shares=16.67,
            price=300,
            amount=5000,
            reason="初始建仓",
            reason_code=BuyReason.INITIAL,
            details={'initial_weight': 50},
            portfolio_value_before=10000,
            portfolio_value_after=10000
        ),
        Transaction(
            date=datetime(2023, 2, 15),
            symbol="AAPL",
            transaction_type=TransactionType.BUY,
            shares=2,
            price=145,
            amount=290,
            reason="RSI指标28.5，超卖信号",
            reason_code=BuyReason.RSI_OVERSOLD,
            details={'rsi': '28.5', 'trigger_threshold': '30'},
            portfolio_value_before=10500,
            portfolio_value_after=10790
        )
    ]
    
    print("\n📊 交易记录列表：")
    for i, tx in enumerate(transactions, 1):
        print(f"\n交易 {i}:")
        tx_dict = tx.to_dict()
        print(f"  日期: {tx_dict['date']}")
        print(f"  股票: {tx_dict['symbol']}")
        print(f"  类型: {tx_dict['type']}")
        print(f"  原因: {tx_dict['reason']}")
        print(f"  金额: ${tx_dict['amount']:.2f}")
    
    return transactions

if __name__ == "__main__":
    test_transaction_model()