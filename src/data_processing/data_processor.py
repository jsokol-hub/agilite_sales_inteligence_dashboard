import os
import json
import pandas as pd
from datetime import datetime
import re
from typing import List, Dict, Any, Optional
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AgiliteDataProcessor:
    def __init__(self, raw_data_dir: str = 'data/raw', processed_data_dir: str = 'data/processed'):
        """
        Инициализация процессора данных
        
        Args:
            raw_data_dir: Директория с сырыми данными
            processed_data_dir: Директория для сохранения обработанных данных
        """
        self.raw_data_dir = raw_data_dir
        self.processed_data_dir = processed_data_dir
        self._ensure_directories()
        
    def _ensure_directories(self):
        """Создание необходимых директорий, если они не существуют"""
        os.makedirs(self.raw_data_dir, exist_ok=True)
        os.makedirs(self.processed_data_dir, exist_ok=True)
    
    def _get_latest_raw_data_file(self) -> Optional[str]:
        """Получение пути к последнему файлу с сырыми данными"""
        try:
            files = [f for f in os.listdir(self.raw_data_dir) if f.startswith('products_') and f.endswith('.json')]
            if not files:
                return None
            return os.path.join(self.raw_data_dir, sorted(files)[-1])
        except Exception as e:
            logger.error(f"Error getting latest raw data file: {str(e)}")
            return None
    
    def _load_raw_data(self, file_path: str) -> List[Dict[str, Any]]:
        """Загрузка сырых данных из JSON файла"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading raw data from {file_path}: {str(e)}")
            return []
    
    def _clean_price(self, price_str: str) -> float:
        """Очистка и преобразование строки цены в число"""
        if not price_str:
            return 0.0
        try:
            # Удаляем все символы кроме цифр и точки/запятой
            cleaned = re.sub(r'[^\d.,]', '', price_str)
            # Заменяем запятую на точку
            cleaned = cleaned.replace(',', '.')
            return float(cleaned)
        except Exception:
            return 0.0
    
    def _extract_variant_info(self, variants: List[str]) -> Dict[str, Any]:
        """Извлечение информации о вариантах продукта"""
        if not variants:
            return {'variant_count': 0, 'variant_types': []}
        
        # Анализ вариантов для определения типов (цвет, размер и т.д.)
        variant_types = set()
        for variant in variants:
            # Здесь можно добавить более сложную логику определения типов вариантов
            if any(color in variant.lower() for color in ['black', 'white', 'red', 'blue', 'green']):
                variant_types.add('color')
            if any(size in variant.lower() for size in ['s', 'm', 'l', 'xl', 'xxl']):
                variant_types.add('size')
        
        return {
            'variant_count': len(variants),
            'variant_types': list(variant_types)
        }
    
    def _parse_stock_status(self, status_url: str) -> str:
        if status_url == "https://schema.org/InStock":
            return "In Stock"
        elif status_url == "https://schema.org/OutOfStock":
            return "Out of Stock"
        else:
            return "Unknown"
    
    def _process_product(self, product: Dict[str, Any]) -> Dict[str, Any]:
        """Обработка данных одного продукта"""
        try:
            # Базовая очистка данных
            processed = {
                'id': product.get('url', '').split('/')[-1],
                'url': product.get('url', ''),
                'title': product.get('title', '').strip(),
                'price': self._clean_price(product.get('price', '0')),
                'description': product.get('description', '').strip(),
                'image_count': len(product.get('images', [])),
                'first_image_url': product.get('images', [''])[0],
                'processing_timestamp': datetime.now().isoformat()
            }
            
            # Обработка вариантов
            variant_info = self._extract_variant_info(product.get('variants', []))
            processed.update(variant_info)
            
            # Обработка stock_status
            processed['stock_status'] = self._parse_stock_status(product.get('stock_status', ''))
            
            return processed
        except Exception as e:
            logger.error(f"Error processing product {product.get('url', 'unknown')}: {str(e)}")
            return {}
    
    def process_data(self) -> pd.DataFrame:
        """Основной метод обработки данных"""
        try:
            # Получение последнего файла с данными
            latest_file = self._get_latest_raw_data_file()
            if not latest_file:
                logger.error("No raw data files found")
                return pd.DataFrame()
            
            logger.info(f"Processing data from {latest_file}")
            
            # Загрузка и обработка данных
            raw_data = self._load_raw_data(latest_file)
            processed_data = [self._process_product(p) for p in raw_data]
            processed_data = [p for p in processed_data if p]  # Удаление пустых записей
            
            # Преобразование в DataFrame
            df = pd.DataFrame(processed_data)
            
            # Сохранение обработанных данных
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = os.path.join(self.processed_data_dir, f'processed_products_{timestamp}.csv')
            df.to_csv(output_file, index=False, encoding='utf-8')
            
            logger.info(f"Processed data saved to {output_file}")
            logger.info(f"Processed {len(df)} products")
            
            return df
            
        except Exception as e:
            logger.error(f"Error in data processing: {str(e)}")
            return pd.DataFrame()
    
    def get_basic_statistics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Получение базовой статистики по обработанным данным"""
        try:
            stats = {
                'total_products': len(df),
                'average_price': df['price'].mean(),
                'min_price': df['price'].min(),
                'max_price': df['price'].max(),
                'products_with_variants': len(df[df['variant_count'] > 0]),
                'average_variants_per_product': df['variant_count'].mean(),
                'products_with_images': len(df[df['image_count'] > 0]),
                'average_images_per_product': df['image_count'].mean()
            }
            
            # Сохранение статистики
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            stats_file = os.path.join(self.processed_data_dir, f'statistics_{timestamp}.json')
            
            with open(stats_file, 'w', encoding='utf-8') as f:
                json.dump(stats, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Statistics saved to {stats_file}")
            return stats
            
        except Exception as e:
            logger.error(f"Error calculating statistics: {str(e)}")
            return {}

if __name__ == "__main__":
    # Пример использования
    processor = AgiliteDataProcessor()
    processed_df = processor.process_data()
    
    if not processed_df.empty:
        stats = processor.get_basic_statistics(processed_df)
        print("\nBasic Statistics:")
        for key, value in stats.items():
            print(f"{key}: {value}") 