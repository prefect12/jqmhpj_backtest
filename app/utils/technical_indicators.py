"""
技术指标计算工具
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional


class TechnicalIndicators:
    """技术指标计算器"""
    
    @staticmethod
    def calculate_rsi(data: pd.Series, period: int = 14) -> pd.Series:
        """
        计算相对强弱指标(RSI)
        
        Args:
            data: 价格序列
            period: RSI计算周期，默认14天
        
        Returns:
            RSI值序列
        """
        delta = data.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    @staticmethod
    def calculate_macd(data: pd.Series, fast_period: int = 12, 
                       slow_period: int = 26, signal_period: int = 9) -> Dict[str, pd.Series]:
        """
        计算MACD指标
        
        Args:
            data: 价格序列
            fast_period: 快速EMA周期，默认12
            slow_period: 慢速EMA周期，默认26
            signal_period: 信号线EMA周期，默认9
        
        Returns:
            包含MACD线、信号线和柱状图的字典
        """
        # 计算EMA
        ema_fast = data.ewm(span=fast_period, adjust=False).mean()
        ema_slow = data.ewm(span=slow_period, adjust=False).mean()
        
        # MACD线
        macd_line = ema_fast - ema_slow
        
        # 信号线
        signal_line = macd_line.ewm(span=signal_period, adjust=False).mean()
        
        # MACD柱状图
        macd_histogram = macd_line - signal_line
        
        return {
            'macd': macd_line,
            'signal': signal_line,
            'histogram': macd_histogram
        }
    
    @staticmethod
    def calculate_bollinger_bands(data: pd.Series, period: int = 20, 
                                 std_dev: float = 2) -> Dict[str, pd.Series]:
        """
        计算布林带
        
        Args:
            data: 价格序列
            period: 移动平均周期，默认20
            std_dev: 标准差倍数，默认2
        
        Returns:
            包含上轨、中轨、下轨的字典
        """
        middle_band = data.rolling(window=period).mean()
        std = data.rolling(window=period).std()
        
        upper_band = middle_band + (std * std_dev)
        lower_band = middle_band - (std * std_dev)
        
        return {
            'upper': upper_band,
            'middle': middle_band,
            'lower': lower_band
        }
    
    @staticmethod
    def calculate_sma(data: pd.Series, period: int) -> pd.Series:
        """计算简单移动平均"""
        return data.rolling(window=period).mean()
    
    @staticmethod
    def calculate_ema(data: pd.Series, period: int) -> pd.Series:
        """计算指数移动平均"""
        return data.ewm(span=period, adjust=False).mean()
    
    @staticmethod
    def calculate_stochastic(high: pd.Series, low: pd.Series, close: pd.Series,
                           k_period: int = 14, d_period: int = 3) -> Dict[str, pd.Series]:
        """
        计算随机指标(Stochastic)
        
        Args:
            high: 最高价序列
            low: 最低价序列
            close: 收盘价序列
            k_period: K线周期
            d_period: D线周期
        
        Returns:
            包含K线和D线的字典
        """
        lowest_low = low.rolling(window=k_period).min()
        highest_high = high.rolling(window=k_period).max()
        
        k_line = 100 * ((close - lowest_low) / (highest_high - lowest_low))
        d_line = k_line.rolling(window=d_period).mean()
        
        return {
            'k': k_line,
            'd': d_line
        }
    
    @staticmethod
    def calculate_atr(high: pd.Series, low: pd.Series, close: pd.Series, 
                     period: int = 14) -> pd.Series:
        """
        计算平均真实波幅(ATR)
        
        Args:
            high: 最高价序列
            low: 最低价序列
            close: 收盘价序列
            period: ATR周期
        
        Returns:
            ATR序列
        """
        high_low = high - low
        high_close = abs(high - close.shift())
        low_close = abs(low - close.shift())
        
        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr = true_range.rolling(window=period).mean()
        
        return atr
    
    @staticmethod
    def calculate_obv(close: pd.Series, volume: pd.Series) -> pd.Series:
        """
        计算成交量平衡指标(OBV)
        
        Args:
            close: 收盘价序列
            volume: 成交量序列
        
        Returns:
            OBV序列
        """
        obv = (np.sign(close.diff()) * volume).fillna(0).cumsum()
        return obv
    
    @staticmethod
    def calculate_momentum(data: pd.Series, period: int = 10) -> pd.Series:
        """
        计算动量指标
        
        Args:
            data: 价格序列
            period: 动量周期
        
        Returns:
            动量序列
        """
        return data.diff(period)
    
    @staticmethod
    def calculate_cci(high: pd.Series, low: pd.Series, close: pd.Series,
                     period: int = 20) -> pd.Series:
        """
        计算商品通道指数(CCI)
        
        Args:
            high: 最高价序列
            low: 最低价序列
            close: 收盘价序列
            period: CCI周期
        
        Returns:
            CCI序列
        """
        typical_price = (high + low + close) / 3
        sma = typical_price.rolling(window=period).mean()
        mean_deviation = abs(typical_price - sma).rolling(window=period).mean()
        
        cci = (typical_price - sma) / (0.015 * mean_deviation)
        return cci
    
    @staticmethod
    def detect_rsi_signals(rsi: pd.Series, oversold: float = 30, 
                          overbought: float = 70) -> pd.Series:
        """
        检测RSI买卖信号
        
        Args:
            rsi: RSI序列
            oversold: 超卖阈值
            overbought: 超买阈值
        
        Returns:
            信号序列 (1=买入, -1=卖出, 0=持有)
        """
        signals = pd.Series(0, index=rsi.index)
        signals[rsi < oversold] = 1  # 买入信号
        signals[rsi > overbought] = -1  # 卖出信号
        return signals
    
    @staticmethod
    def detect_macd_signals(macd: Dict[str, pd.Series]) -> pd.Series:
        """
        检测MACD买卖信号
        
        Args:
            macd: MACD指标字典
        
        Returns:
            信号序列 (1=买入, -1=卖出, 0=持有)
        """
        macd_line = macd['macd']
        signal_line = macd['signal']
        
        signals = pd.Series(0, index=macd_line.index)
        
        # 金叉买入，死叉卖出
        macd_above_signal = macd_line > signal_line
        macd_above_signal_prev = macd_above_signal.shift(1)
        
        # 金叉：MACD从下方穿越信号线
        signals[(~macd_above_signal_prev) & macd_above_signal] = 1
        
        # 死叉：MACD从上方穿越信号线
        signals[macd_above_signal_prev & (~macd_above_signal)] = -1
        
        return signals
    
    @staticmethod
    def calculate_pe_ratio(price: float, earnings_per_share: float) -> float:
        """计算市盈率"""
        if earnings_per_share <= 0:
            return float('inf')
        return price / earnings_per_share
    
    @staticmethod
    def calculate_pb_ratio(price: float, book_value_per_share: float) -> float:
        """计算市净率"""
        if book_value_per_share <= 0:
            return float('inf')
        return price / book_value_per_share