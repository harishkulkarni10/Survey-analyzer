"""
Statistical analysis module for Survey Analyzer
Handles all statistical calculations and segment analysis
"""

import pandas as pd
from typing import Dict, Optional


class StatisticsCalculator:
    """Handles statistical calculations for survey data"""
    
    @staticmethod
    def calculate_nps(df: pd.DataFrame, nps_column: str = 'likelihood_to_recommend') -> float:
        """
        Calculate Net Promoter Score
        
        Args:
            df: DataFrame with survey data
            nps_column: Column name for NPS scores (0-10 scale)
            
        Returns:
            NPS score as percentage
        """
        total = len(df)
        if total == 0:
            return 0.0
        
        promoters = len(df[df[nps_column] >= 9])
        detractors = len(df[df[nps_column] <= 6])
        return ((promoters - detractors) / total) * 100
    
    @staticmethod
    def calculate_comprehensive_stats(df: pd.DataFrame) -> Dict:
        """
        Calculate comprehensive statistics from survey data
        
        Args:
            df: DataFrame with survey data
            
        Returns:
            Dictionary with all calculated statistics
        """
        stats = {
            # Basic info
            'total_responses': len(df),
            'date_range': f"{df['timestamp'].min().date()} to {df['timestamp'].max().date()}" if 'timestamp' in df.columns else "N/A",
            'completion_rate': StatisticsCalculator._calculate_completion_rate(df),
            
            # Core metrics
            'avg_satisfaction': df['satisfaction'].mean() if 'satisfaction' in df.columns else 0.0,
            'avg_product_quality': df['product_quality'].mean() if 'product_quality' in df.columns else 0.0,
            'avg_customer_service': df['customer_service'].mean() if 'customer_service' in df.columns else 0.0,
            'avg_value': df['value_for_money'].mean() if 'value_for_money' in df.columns else 0.0,
            'avg_nps': df['likelihood_to_recommend'].mean() if 'likelihood_to_recommend' in df.columns else 0.0,
            
            # Standard deviations
            'std_satisfaction': df['satisfaction'].std() if 'satisfaction' in df.columns else 0.0,
            'std_product_quality': df['product_quality'].std() if 'product_quality' in df.columns else 0.0,
            'std_customer_service': df['customer_service'].std() if 'customer_service' in df.columns else 0.0,
            
            # NPS breakdown
            'nps_score': StatisticsCalculator.calculate_nps(df),
            'promoters': len(df[df['likelihood_to_recommend'] >= 9]) if 'likelihood_to_recommend' in df.columns else 0,
            'passives': len(df[(df['likelihood_to_recommend'] >= 7) & (df['likelihood_to_recommend'] <= 8)]) if 'likelihood_to_recommend' in df.columns else 0,
            'detractors': len(df[df['likelihood_to_recommend'] <= 6]) if 'likelihood_to_recommend' in df.columns else 0,
            
            # Percentiles
            'satisfaction_p25': df['satisfaction'].quantile(0.25) if 'satisfaction' in df.columns else 0.0,
            'satisfaction_median': df['satisfaction'].median() if 'satisfaction' in df.columns else 0.0,
            'satisfaction_p75': df['satisfaction'].quantile(0.75) if 'satisfaction' in df.columns else 0.0,
        }
        
        # Top/bottom performers (if region and age_group columns exist)
        if 'region' in df.columns and 'satisfaction' in df.columns:
            region_stats = df.groupby('region')['satisfaction'].mean()
            stats['best_region'] = region_stats.idxmax()
            stats['best_region_score'] = region_stats.max()
        else:
            stats['best_region'] = "N/A"
            stats['best_region_score'] = 0.0
        
        if 'age_group' in df.columns and 'satisfaction' in df.columns:
            age_stats = df.groupby('age_group')['satisfaction'].mean()
            stats['top_age_group'] = age_stats.idxmax()
            stats['top_age_score'] = age_stats.max()
        else:
            stats['top_age_group'] = "N/A"
            stats['top_age_score'] = 0.0
        
        return stats
    
    @staticmethod
    def _calculate_completion_rate(df: pd.DataFrame) -> float:
        """Calculate data completion rate"""
        if len(df) == 0:
            return 0.0
        total_cells = len(df) * len(df.columns)
        missing_cells = df.isnull().sum().sum()
        return 100.0 - (missing_cells / total_cells * 100) if total_cells > 0 else 100.0
    
    @staticmethod
    def analyze_by_segment(df: pd.DataFrame, segment_column: str) -> pd.DataFrame:
        """
        Analyze metrics by segment
        
        Args:
            df: DataFrame with survey data
            segment_column: Column to segment by
            
        Returns:
            DataFrame with segment analysis
        """
        numeric_cols = ['satisfaction', 'product_quality', 'customer_service', 
                       'value_for_money', 'likelihood_to_recommend']
        
        # Filter to only numeric columns that exist
        available_cols = [col for col in numeric_cols if col in df.columns]
        
        if not available_cols:
            return pd.DataFrame()
        
        return df.groupby(segment_column)[available_cols].agg(['mean', 'std', 'count']).round(2)
    
    @staticmethod
    def get_sentiment_analysis(df: pd.DataFrame) -> Optional[Dict]:
        """
        Basic sentiment analysis of feedback
        
        Args:
            df: DataFrame with survey data
            
        Returns:
            Dictionary with sentiment counts or None if feedback column doesn't exist
        """
        if 'feedback' not in df.columns:
            return None
        
        positive_words = ['excellent', 'great', 'amazing', 'fantastic', 'love', 'perfect', 
                         'outstanding', 'wonderful', 'satisfied', 'recommend', 'exceeded']
        negative_words = ['poor', 'bad', 'terrible', 'disappointed', 'awful', 'horrible',
                         'worse', 'not satisfied', 'problem', 'issue', 'complaint']
        
        def classify_sentiment(text):
            if pd.isna(text):
                return 'neutral'
            text_lower = str(text).lower()
            pos_count = sum(word in text_lower for word in positive_words)
            neg_count = sum(word in text_lower for word in negative_words)
            
            if pos_count > neg_count:
                return 'positive'
            elif neg_count > pos_count:
                return 'negative'
            else:
                return 'neutral'
        
        df_copy = df.copy()
        df_copy['sentiment'] = df_copy['feedback'].apply(classify_sentiment)
        sentiment_counts = df_copy['sentiment'].value_counts()
        
        return {
            'positive': sentiment_counts.get('positive', 0),
            'neutral': sentiment_counts.get('neutral', 0),
            'negative': sentiment_counts.get('negative', 0),
            'positive_pct': (sentiment_counts.get('positive', 0) / len(df)) * 100
        }
