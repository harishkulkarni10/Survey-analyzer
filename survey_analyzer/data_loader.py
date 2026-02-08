"""
Data loading utilities for Survey Analyzer
Supports: CSV, Excel (.xlsx/.xls), PDF, and dummy data generation.
"""

import os
import pandas as pd
import numpy as np
from typing import Dict, Optional, Union


class DataLoader:
    """Handles data loading and generation"""
    
    @staticmethod
    def generate_sample_data(n_responses: int = 150) -> Dict:
        """
        Generate sample survey data for testing
        
        Args:
            n_responses: Number of survey responses to generate
            
        Returns:
            Dictionary with survey data
        """
        np.random.seed(42)  # For reproducibility
        
        feedback_options = [
            'Excellent product quality!', 'Very satisfied with service', 'Could be better', 
            'Great experience overall', 'Amazing customer support', 'Product needs improvement',
            'Fantastic value!', 'Good but not great', 'Average experience', 'Highly recommend!',
            'Outstanding quality', 'Service was quick', 'Price is too high', 'Love the product',
            'Will buy again', 'Not satisfied', 'Perfect solution', 'Exceeded expectations',
            'Decent product', 'Could improve delivery'
        ]
        
        return {
            'timestamp': pd.date_range('2024-01-01', periods=n_responses, freq='D'),
            'respondent_id': [f'R{str(i).zfill(4)}' for i in range(1, n_responses + 1)],
            'age_group': np.random.choice(['18-25', '26-35', '36-45', '46-55', '55+'], n_responses),
            'gender': np.random.choice(['Male', 'Female', 'Non-binary', 'Prefer not to say'], n_responses),
            'satisfaction': np.random.choice([1, 2, 3, 4, 5], n_responses, p=[0.05, 0.10, 0.25, 0.35, 0.25]),
            'product_quality': np.random.choice([1, 2, 3, 4, 5], n_responses, p=[0.03, 0.07, 0.20, 0.40, 0.30]),
            'customer_service': np.random.choice([1, 2, 3, 4, 5], n_responses, p=[0.05, 0.15, 0.25, 0.30, 0.25]),
            'value_for_money': np.random.choice([1, 2, 3, 4, 5], n_responses, p=[0.08, 0.12, 0.30, 0.30, 0.20]),
            'likelihood_to_recommend': np.random.choice(range(0, 11), n_responses, p=[0.02, 0.03, 0.05, 0.05, 0.08, 0.10, 0.12, 0.15, 0.15, 0.15, 0.10]),
            'feedback': np.random.choice(feedback_options, n_responses),
            'region': np.random.choice(['North', 'South', 'East', 'West', 'Central'], n_responses),
            'purchase_frequency': np.random.choice(['First time', 'Occasional', 'Regular', 'Frequent'], n_responses)
        }
    
    @staticmethod
    def load_data(data: Optional[Union[pd.DataFrame, Dict, str]] = None) -> pd.DataFrame:
        """
        Load survey data from various sources
        
        Args:
            data: Can be one of:
                - None: generates dummy sample data
                - pd.DataFrame: uses it directly
                - dict: converts to DataFrame
                - str (file path): loads from CSV, Excel, or PDF based on extension
            
        Returns:
            DataFrame with survey data
        """
        if data is None:
            # Generate sample data
            data_dict = DataLoader.generate_sample_data()
            return pd.DataFrame(data_dict)
        elif isinstance(data, pd.DataFrame):
            return data.copy()
        elif isinstance(data, dict):
            return pd.DataFrame(data)
        elif isinstance(data, str):
            # It's a file path
            return DataLoader.load_from_file(data)
        else:
            raise ValueError("Data must be DataFrame, dict, file path (str), or None")
    
    @staticmethod
    def load_from_file(file_path: str) -> pd.DataFrame:
        """
        Auto-detect file type and load accordingly
        
        Args:
            file_path: Path to CSV, Excel, or PDF file
            
        Returns:
            DataFrame with loaded data
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext == '.csv':
            return DataLoader.load_from_csv(file_path)
        elif ext in ['.xlsx', '.xls']:
            return DataLoader.load_from_excel(file_path)
        elif ext == '.pdf':
            return DataLoader.load_from_pdf(file_path)
        else:
            raise ValueError(f"Unsupported file type: {ext}. Supported: .csv, .xlsx, .xls, .pdf")
    
    @staticmethod
    def load_from_csv(file_path: str) -> pd.DataFrame:
        """
        Load data from CSV file
        
        Args:
            file_path: Path to CSV file
            
        Returns:
            DataFrame with survey data
        """
        print(f"📂 Loading CSV: {file_path}")
        df = pd.read_csv(file_path)
        print(f"   ✅ Loaded {len(df)} rows, {len(df.columns)} columns")
        print(f"   Columns: {', '.join(df.columns.tolist())}")
        return df
    
    @staticmethod
    def load_from_excel(file_path: str, sheet_name: Optional[Union[str, int]] = 0) -> pd.DataFrame:
        """
        Load data from Excel file
        
        Args:
            file_path: Path to Excel file
            sheet_name: Sheet name or index (default: first sheet)
            
        Returns:
            DataFrame with survey data
        """
        print(f"📂 Loading Excel: {file_path}")
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        print(f"   ✅ Loaded {len(df)} rows, {len(df.columns)} columns")
        print(f"   Columns: {', '.join(df.columns.tolist())}")
        return df
    
    @staticmethod
    def load_from_pdf(file_path: str) -> pd.DataFrame:
        """
        Load tabular data from PDF file
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            DataFrame with extracted table data
        """
        try:
            import pdfplumber
        except ImportError:
            raise ImportError(
                "pdfplumber is required for PDF loading.\n"
                "Install it: pip install pdfplumber"
            )
        
        print(f"📂 Loading PDF: {file_path}")
        
        all_tables = []
        with pdfplumber.open(file_path) as pdf:
            for i, page in enumerate(pdf.pages):
                tables = page.extract_tables()
                for table in tables:
                    if table and len(table) > 1:
                        # First row as header, rest as data
                        header = table[0]
                        rows = table[1:]
                        df_table = pd.DataFrame(rows, columns=header)
                        all_tables.append(df_table)
                        print(f"   Found table on page {i+1}: {len(rows)} rows")
        
        if not all_tables:
            raise ValueError(f"No tables found in PDF: {file_path}")
        
        # Combine all tables (if multiple, stack them)
        if len(all_tables) == 1:
            df = all_tables[0]
        else:
            df = pd.concat(all_tables, ignore_index=True)
        
        print(f"   ✅ Loaded {len(df)} rows, {len(df.columns)} columns")
        print(f"   Columns: {', '.join(df.columns.tolist())}")
        return df
