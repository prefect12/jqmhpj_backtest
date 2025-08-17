"""
股票数据访问对象
负责从外部数据源获取股票数据
"""
import yfinance as yf
import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import json
import os
import hashlib
from app.core.config import settings


class StockDataDAO:
    """股票数据访问对象"""
    
    def __init__(self):
        self.cache_dir = "data/cache"
        self.cache_ttl = settings.yfinance_cache_ttl
        self.timeout = settings.yfinance_timeout
        self.retry_count = settings.yfinance_retry_count
        
        # 确保缓存目录存在
        os.makedirs(self.cache_dir, exist_ok=True)
    
    def get_stock_data(self, symbol: str, start_date: str, end_date: str) -> List[Dict]:
        """
        获取股票历史数据
        
        Args:
            symbol: 股票代码
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
        
        Returns:
            股票历史数据列表
        """
        # 尝试从缓存获取
        cached_data = self._get_from_cache(symbol, start_date, end_date)
        if cached_data is not None:
            return cached_data
        
        # 从Yahoo Finance获取数据
        try:
            ticker = yf.Ticker(symbol)
            
            # 获取历史数据
            hist = ticker.history(
                start=start_date,
                end=end_date,
                interval="1d",
                timeout=self.timeout
            )
            
            if hist.empty:
                raise ValueError(f"No data available for {symbol} in the specified period")
            
            # 转换为字典列表
            data = []
            # 重置索引，让Date成为一列
            if hist.index.name:
                hist = hist.reset_index()
            
            for idx, row in hist.iterrows():
                # 获取日期
                if 'Date' in hist.columns:
                    date_value = row['Date']
                elif 'index' in hist.columns:
                    date_value = row['index']
                else:
                    date_value = idx
                
                # 格式化日期
                if hasattr(date_value, 'strftime'):
                    date_str = date_value.strftime('%Y-%m-%d')
                else:
                    date_str = str(date_value)[:10]  # 取前10个字符作为日期
                    
                data.append({
                    'Date': date_str,
                    'Open': float(row['Open']),
                    'High': float(row['High']),
                    'Low': float(row['Low']),
                    'Close': float(row['Close']),
                    'Volume': int(row['Volume']) if pd.notna(row['Volume']) else 0
                })
            
            # 缓存数据
            self._save_to_cache(symbol, start_date, end_date, data)
            
            return data
            
        except Exception as e:
            raise Exception(f"Failed to fetch data for {symbol}: {str(e)}")
    
    def get_multiple_stocks_dataframes(self, symbols: List[str], start_date: str, end_date: str) -> Dict[str, pd.DataFrame]:
        """
        获取多只股票的历史数据（DataFrame格式）
        
        Args:
            symbols: 股票代码列表
            start_date: 开始日期
            end_date: 结束日期
        
        Returns:
            股票数据字典 {symbol: DataFrame}
        """
        result = {}
        for symbol in symbols:
            try:
                ticker = yf.Ticker(symbol)
                data = ticker.history(
                    start=start_date,
                    end=end_date,
                    interval="1d",
                    timeout=self.timeout
                )
                if not data.empty:
                    result[symbol] = data
            except Exception as e:
                print(f"Warning: Failed to fetch data for {symbol}: {e}")
                continue
        return result
    
    def get_multiple_stocks_data(self, symbols: List[str], start_date: str, end_date: str) -> Dict[str, List[Dict]]:
        """
        获取多只股票的历史数据
        
        Args:
            symbols: 股票代码列表
            start_date: 开始日期
            end_date: 结束日期
        
        Returns:
            股票数据字典 {symbol: data}
        """
        result = {}
        
        for symbol in symbols:
            try:
                data = self.get_stock_data(symbol, start_date, end_date)
                result[symbol] = data
            except Exception as e:
                # 记录错误但继续处理其他股票
                print(f"Error fetching {symbol}: {e}")
                result[symbol] = []
        
        return result
    
    def validate_symbol(self, symbol: str) -> bool:
        """
        验证股票代码是否有效
        
        Args:
            symbol: 股票代码
        
        Returns:
            是否有效
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            return 'symbol' in info or 'shortName' in info
        except:
            return False
    
    def get_stock_info(self, symbol: str) -> Dict:
        """
        获取股票基本信息
        
        Args:
            symbol: 股票代码
        
        Returns:
            股票信息字典
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            return {
                'symbol': symbol,
                'name': info.get('longName', info.get('shortName', 'Unknown')),
                'exchange': info.get('exchange', 'Unknown'),
                'currency': info.get('currency', 'USD'),
                'current_price': info.get('currentPrice', info.get('regularMarketPrice', 0)),
                'market_cap': info.get('marketCap', 0),
                'pe_ratio': info.get('trailingPE', 0),
                'dividend_yield': info.get('dividendYield', 0),
                'sector': info.get('sector', 'Unknown'),
                'industry': info.get('industry', 'Unknown')
            }
        except Exception as e:
            raise Exception(f"Failed to fetch info for {symbol}: {str(e)}")
    
    def search_stocks(self, query: str, limit: int = 10) -> List[Dict]:
        """
        搜索股票
        
        Args:
            query: 搜索关键词
            limit: 返回结果数量限制
        
        Returns:
            搜索结果列表
        """
        # 这里简化处理，实际可以接入更完善的搜索API
        # 常见股票列表（示例）
        common_stocks = {
            'AAPL': 'Apple Inc.',
            'MSFT': 'Microsoft Corporation',
            'GOOGL': 'Alphabet Inc.',
            'AMZN': 'Amazon.com Inc.',
            'TSLA': 'Tesla Inc.',
            'META': 'Meta Platforms Inc.',
            'NVDA': 'NVIDIA Corporation',
            'JPM': 'JPMorgan Chase & Co.',
            'V': 'Visa Inc.',
            'JNJ': 'Johnson & Johnson'
        }
        
        results = []
        query_upper = query.upper()
        
        for symbol, name in common_stocks.items():
            if query_upper in symbol or query.lower() in name.lower():
                results.append({
                    'symbol': symbol,
                    'name': name
                })
                
                if len(results) >= limit:
                    break
        
        return results
    
    def _get_cache_key(self, symbol: str, start_date: str, end_date: str) -> str:
        """生成缓存键"""
        key_str = f"{symbol}_{start_date}_{end_date}"
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def _get_from_cache(self, symbol: str, start_date: str, end_date: str) -> Optional[List[Dict]]:
        """从缓存获取数据"""
        if not settings.cache_enabled:
            return None
        
        cache_key = self._get_cache_key(symbol, start_date, end_date)
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
        
        if os.path.exists(cache_file):
            # 检查缓存是否过期
            file_time = os.path.getmtime(cache_file)
            if (datetime.now().timestamp() - file_time) < self.cache_ttl:
                with open(cache_file, 'r') as f:
                    return json.load(f)
        
        return None
    
    def _save_to_cache(self, symbol: str, start_date: str, end_date: str, data: List[Dict]):
        """保存数据到缓存"""
        if not settings.cache_enabled:
            return
        
        cache_key = self._get_cache_key(symbol, start_date, end_date)
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
        
        with open(cache_file, 'w') as f:
            json.dump(data, f)