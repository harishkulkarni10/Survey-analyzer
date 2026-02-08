"""
Main Survey Analyzer class
Orchestrates all analysis components
"""

import os
import json
import pandas as pd
from datetime import datetime
from typing import Optional, Union, Dict

from .data_loader import DataLoader
from .llm_providers import BaseLLMProvider, get_llm_provider
from .statistics import StatisticsCalculator
from .visualizations import VisualizationGenerator
from .report_generator import ReportGenerator
from .config import Config


class SurveyAnalyzer:
    """Main survey analysis engine"""
    
    def __init__(self, data: Optional[Union[pd.DataFrame, Dict]] = None,
                 llm_provider: Optional[BaseLLMProvider] = None,
                 output_dir: Optional[str] = None):
        """
        Initialize Survey Analyzer
        
        Args:
            data: DataFrame, dict, or None (for sample data)
            llm_provider: LLM provider instance (auto-detects if None)
            output_dir: Optional custom output directory (uses timestamped dir if None)
        """
        # Load data
        self.df = DataLoader.load_data(data)
        
        # Setup output directory (timestamped by default)
        if output_dir is None:
            self.output_dir = Config.get_timestamped_output_dir()
        else:
            self.output_dir = output_dir
            os.makedirs(self.output_dir, exist_ok=True)
        
        # Setup LLM (Gemini)
        self.llm_provider = llm_provider or get_llm_provider()
        
        # Initialize components
        self.stats_calc = StatisticsCalculator()
        self.visualizer = VisualizationGenerator(self.df)
        
        # Statistics cache
        self.stats = None
        
        print(f"📊 Initialized with {len(self.df)} responses")
        print(f"🤖 LLM Provider: {self.llm_provider.name}")
        
        # Show folder name clearly
        folder_name = os.path.basename(self.output_dir)
        abs_path = os.path.abspath(self.output_dir)
        print(f"📁 Output Folder: {folder_name}")
        print(f"📁 Full Path: {abs_path}")
        print()
    
    def calculate_statistics(self) -> Dict:
        """Calculate comprehensive statistics"""
        self.stats = self.stats_calc.calculate_comprehensive_stats(self.df)
        return self.stats
    
    def analyze_by_segment(self, segment_column: str) -> pd.DataFrame:
        """Analyze metrics by segment"""
        return self.stats_calc.analyze_by_segment(self.df, segment_column)
    
    def get_sentiment_analysis(self) -> Optional[Dict]:
        """Basic sentiment analysis of feedback"""
        return self.stats_calc.get_sentiment_analysis(self.df)
    
    def create_visualizations(self, save_path: Optional[str] = None):
        """Create comprehensive visualization dashboard"""
        if save_path is None:
            save_path = os.path.join(self.output_dir, "survey_visualizations.png")
        self.visualizer.create_dashboard(save_path)
        return save_path
    
    def get_llm_insights(self, insight_type: str = "summary") -> str:
        """Get AI-powered insights"""
        if self.stats is None:
            self.calculate_statistics()
        
        report_gen = ReportGenerator(self.df, self.stats, self.llm_provider)
        return report_gen.get_llm_insights(insight_type)
    
    def generate_report(self, save_path: Optional[str] = None) -> str:
        """Generate comprehensive text report"""
        if self.stats is None:
            self.calculate_statistics()
        
        sentiment = self.get_sentiment_analysis()
        
        age_analysis = None
        region_analysis = None
        
        if 'age_group' in self.df.columns:
            age_analysis = self.analyze_by_segment('age_group')
        if 'region' in self.df.columns:
            region_analysis = self.analyze_by_segment('region')
        
        if save_path is None:
            save_path = os.path.join(self.output_dir, "survey_report.txt")
        
        report_gen = ReportGenerator(self.df, self.stats, self.llm_provider)
        return report_gen.generate_report(save_path, sentiment, age_analysis, region_analysis)
    
    def export_data(self, base_path: Optional[str] = None) -> list:
        """Export all analysis data"""
        base_path = base_path or self.output_dir
        os.makedirs(base_path, exist_ok=True)
        
        exports = []
        
        if 'age_group' in self.df.columns:
            age_file = os.path.join(base_path, 'age_group_analysis.csv')
            self.analyze_by_segment('age_group').to_csv(age_file)
            exports.append(age_file)
        
        if 'region' in self.df.columns:
            region_file = os.path.join(base_path, 'regional_analysis.csv')
            self.analyze_by_segment('region').to_csv(region_file)
            exports.append(region_file)
        
        raw_file = os.path.join(base_path, 'survey_raw_data.csv')
        self.df.to_csv(raw_file, index=False)
        exports.append(raw_file)
        
        if self.stats:
            stats_file = os.path.join(base_path, 'statistics.json')
            with open(stats_file, 'w') as f:
                json.dump(self.stats, f, indent=2, default=str)
            exports.append(stats_file)
        
        print(f"✅ Exported {len(exports)} files to: {base_path}")
        return exports
    
    def generate_output_explanation(self, output_files: list) -> str:
        """Generate comprehensive LLM explanation of all output files"""
        if self.stats is None:
            self.calculate_statistics()
        
        explanation_prompt = f"""You are an expert business analyst explaining survey analysis results to a business stakeholder. 

SURVEY OVERVIEW:
- Total Responses: {self.stats['total_responses']}
- Average Satisfaction: {self.stats['avg_satisfaction']:.2f}/5.0
- Net Promoter Score: {self.stats['nps_score']:.2f}
- Best Region: {self.stats['best_region']} ({self.stats['best_region_score']:.2f}/5.0)
- Top Age Group: {self.stats['top_age_group']} ({self.stats['top_age_score']:.2f}/5.0)

OUTPUT FILES GENERATED:
1. survey_report.txt - Comprehensive analysis report with AI-generated insights
2. survey_visualizations.png - Dashboard with 8 charts (histograms, bar charts, pie charts, line charts, heatmap)
3. age_group_analysis.csv - Demographic breakdown by age group with mean, std dev, and counts
4. regional_analysis.csv - Geographic performance analysis by region
5. survey_raw_data.csv - Complete dataset with all survey responses
6. statistics.json - All calculated metrics in JSON format

CHART DETAILS (from survey_visualizations.png):
- Chart 1: Overall Satisfaction Distribution (histogram showing score frequencies 1-5)
- Chart 2: Average Scores by Metric (horizontal bar chart: Satisfaction, Quality, Service, Value)
- Chart 3: NPS Distribution (pie chart: Promoters, Passives, Detractors)
- Chart 4: Satisfaction by Region (horizontal bar chart showing regional averages)
- Chart 5: Metrics by Age Group (grouped bar chart: Satisfaction, Quality, Service across age groups)
- Chart 6: Likelihood to Recommend Distribution (histogram 0-10 scale)
- Chart 7: Satisfaction Trend Over Time (line chart with weekly averages)
- Chart 8: Metric Correlations (heatmap showing relationships between metrics)

Provide a comprehensive, business-friendly explanation that:

1. EXPLAIN THE REPORT (survey_report.txt):
   - What sections it contains
   - What insights are in each section
   - Why this report is valuable for decision-making

2. EXPLAIN THE CHARTS (survey_visualizations.png):
   - Describe what each of the 8 charts shows
   - Explain the key insights from each chart
   - Connect chart findings to business implications
   - Use simple language as if explaining to a non-technical business owner

3. EXPLAIN THE DATA FILES:
   - age_group_analysis.csv: What demographic insights it reveals
   - regional_analysis.csv: What geographic patterns it shows
   - survey_raw_data.csv: What's in the raw data
   - statistics.json: What metrics are tracked

4. PROVIDE EXECUTIVE SUMMARY:
   - Overall key findings across all outputs
   - Most important insights for business decisions
   - Action items based on the analysis

Write in clear, professional business language. Be specific about numbers and findings. 
Format as a comprehensive document that a business stakeholder can read to understand everything."""

        print("🤖 Generating comprehensive output explanation from Gemini...")
        explanation = self.llm_provider.generate(explanation_prompt)
        
        if not explanation:
            explanation = "[Error: Could not generate explanation. Check your Gemini API key in api_key.py]"
        
        explanation_path = os.path.join(self.output_dir, "output_explanation.txt")
        with open(explanation_path, 'w', encoding='utf-8') as f:
            f.write(f"""OUTPUT FILES EXPLANATION
{'='*80}
Generated by: {self.llm_provider.name}
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'='*80}

{explanation}

{'='*80}
This explanation was generated by AI (Google Gemini) to help you understand 
all the output files in this analysis folder.
{'='*80}
""")
        
        print(f"✅ Output explanation saved to: {explanation_path}")
        return explanation_path
