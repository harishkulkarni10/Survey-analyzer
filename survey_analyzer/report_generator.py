"""
Report generation module for Survey Analyzer
Creates comprehensive text reports with Gemini-powered insights
"""

import os
import pandas as pd
from datetime import datetime
from typing import Dict, Optional

from .config import Config
from .statistics import StatisticsCalculator


class ReportGenerator:
    """Handles generation of comprehensive text reports"""
    
    def __init__(self, df: pd.DataFrame, stats: Dict, llm_provider):
        """
        Initialize report generator
        
        Args:
            df: DataFrame with survey data
            stats: Dictionary with calculated statistics
            llm_provider: Gemini LLM provider instance
        """
        self.df = df
        self.stats = stats
        self.llm_provider = llm_provider
        self.stats_calc = StatisticsCalculator()
    
    def format_segment_table(self, segment_df: pd.DataFrame) -> str:
        """Format segment analysis table for report"""
        if isinstance(segment_df.columns, pd.MultiIndex):
            means = segment_df.xs('mean', level=1, axis=1)
        else:
            means = segment_df
        
        output = []
        cols = means.columns.tolist()
        header = f"{'Segment':<15} " + " ".join([f"{col[:8]:>8}" for col in cols])
        output.append(header)
        output.append("-" * len(header))
        
        for idx, row in means.iterrows():
            row_str = f"{str(idx):<15} " + " ".join([f"{val:>8.2f}" for val in row])
            output.append(row_str)
        
        return "\n".join(output)
    
    def get_llm_insights(self, insight_type: str = "summary") -> str:
        """Get AI-powered insights from Gemini"""
        if not self.llm_provider.available:
            return "[Gemini not available - check api_key.py]"
        
        prompts = {
            "summary": f"""You are an expert data analyst. Analyze this survey data and provide a comprehensive executive summary.

SURVEY DATA:
- Total Responses: {self.stats['total_responses']}
- Average Satisfaction: {self.stats['avg_satisfaction']:.2f}/5.0
- Product Quality: {self.stats['avg_product_quality']:.2f}/5.0
- Customer Service: {self.stats['avg_customer_service']:.2f}/5.0
- Value for Money: {self.stats['avg_value']:.2f}/5.0
- Net Promoter Score (NPS): {self.stats['nps_score']:.2f}
- Best Performing Region: {self.stats['best_region']} (Score: {self.stats['best_region_score']:.2f}/5.0)
- Promoters: {self.stats['promoters']} ({self.stats['promoters']/self.stats['total_responses']*100:.1f}%)
- Detractors: {self.stats['detractors']} ({self.stats['detractors']/self.stats['total_responses']*100:.1f}%)

Provide a professional executive summary (4-5 sentences) that:
1. Highlights the overall performance level
2. Identifies the strongest metric
3. Points out the biggest opportunity for improvement
4. Gives a clear assessment of customer loyalty (NPS)
5. Mentions any notable regional or demographic patterns

Write in a business-professional tone suitable for executive stakeholders.""",

            "trends": f"""You are a data analyst expert. Analyze these survey metrics and identify critical trends.

DETAILED METRICS:
- Overall Satisfaction: {self.stats['avg_satisfaction']:.2f}/5.0 (Std Dev: {self.stats['std_satisfaction']:.2f})
- Product Quality: {self.stats['avg_product_quality']:.2f}/5.0 (Std Dev: {self.stats['std_product_quality']:.2f})
- Customer Service: {self.stats['avg_customer_service']:.2f}/5.0 (Std Dev: {self.stats['std_customer_service']:.2f})
- Value for Money: {self.stats['avg_value']:.2f}/5.0
- Net Promoter Score: {self.stats['nps_score']:.2f}
- Average Recommendation Score: {self.stats['avg_nps']:.2f}/10.0

SEGMENT PERFORMANCE:
- Top Age Group: {self.stats['top_age_group']} (Satisfaction: {self.stats['top_age_score']:.2f}/5.0)
- Top Region: {self.stats['best_region']} (Satisfaction: {self.stats['best_region_score']:.2f}/5.0)

SATISFACTION DISTRIBUTION:
- 25th Percentile: {self.stats['satisfaction_p25']:.1f}
- Median: {self.stats['satisfaction_median']:.1f}
- 75th Percentile: {self.stats['satisfaction_p75']:.1f}

Identify and explain 5-6 critical trends or patterns. For each trend:
1. Describe what the data shows
2. Explain why this trend matters
3. Note any correlations or relationships between metrics

Format as a numbered list with clear explanations.""",

            "recommendations": f"""You are a strategic business consultant. Based on this survey analysis, provide actionable recommendations.

CURRENT PERFORMANCE STATE:
- Overall Satisfaction: {self.stats['avg_satisfaction']:.2f}/5.0
- Net Promoter Score: {self.stats['nps_score']:.2f}
- Promoters: {self.stats['promoters']} ({self.stats['promoters']/self.stats['total_responses']*100:.1f}%)
- Passives: {self.stats['passives']} ({self.stats['passives']/self.stats['total_responses']*100:.1f}%)
- Detractors: {self.stats['detractors']} ({self.stats['detractors']/self.stats['total_responses']*100:.1f}%)

METRIC GAPS:
- Service Gap: {abs(self.stats['avg_product_quality'] - self.stats['avg_customer_service']):.2f} points (Quality vs Service)
- Value Perception: {self.stats['avg_value']:.2f}/5.0
- Best Region: {self.stats['best_region']} ({self.stats['best_region_score']:.2f}/5.0)

Provide 6-8 specific, actionable strategic recommendations organized by:
1. IMMEDIATE ACTIONS (0-30 days) - Quick wins
2. SHORT-TERM INITIATIVES (30-90 days) - Medium impact
3. LONG-TERM STRATEGY (90+ days) - Transformational

For each recommendation, include:
- What action to take
- Why it matters (based on the data)
- Expected impact/outcome
- Priority level

Write in a professional, executive-ready format."""
        }
        
        prompt = prompts.get(insight_type, prompts["summary"])
        response = self.llm_provider.generate(prompt)
        return response if response else f"[Error generating {insight_type} insights]"
    
    def generate_report(self, save_path: Optional[str] = None, sentiment: Optional[Dict] = None,
                       age_analysis: Optional[pd.DataFrame] = None,
                       region_analysis: Optional[pd.DataFrame] = None) -> str:
        """Generate comprehensive text report"""
        
        report = f"""
╔═══════════════════════════════════════════════════════════════════════╗
║                  COMPREHENSIVE SURVEY ANALYSIS REPORT                 ║
║                     AI-POWERED INSIGHTS (GEMINI)                      ║
╚═══════════════════════════════════════════════════════════════════════╝

{'='*75}
📊 EXECUTIVE SUMMARY
{'='*75}
Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
LLM Provider: {self.llm_provider.name}
Total Responses: {self.stats['total_responses']:,}
Survey Period: {self.stats['date_range']}
Data Completeness: {self.stats['completion_rate']:.1f}%

{'='*75}
📈 KEY PERFORMANCE INDICATORS
{'='*75}

SATISFACTION METRICS:
  Overall Satisfaction:      {self.stats['avg_satisfaction']:.2f} / 5.00  (σ = {self.stats['std_satisfaction']:.2f})
  Product Quality:           {self.stats['avg_product_quality']:.2f} / 5.00  (σ = {self.stats['std_product_quality']:.2f})
  Customer Service:          {self.stats['avg_customer_service']:.2f} / 5.00  (σ = {self.stats['std_customer_service']:.2f})
  Value for Money:           {self.stats['avg_value']:.2f} / 5.00
  
  Satisfaction Distribution:
    - 25th Percentile:       {self.stats['satisfaction_p25']:.1f}
    - Median:                {self.stats['satisfaction_median']:.1f}
    - 75th Percentile:       {self.stats['satisfaction_p75']:.1f}

NET PROMOTER SCORE (NPS):
  Overall NPS:               {self.stats['nps_score']:.2f}
  Average Recommendation:    {self.stats['avg_nps']:.2f} / 10.00
  
  Breakdown:
    • Promoters (9-10):      {self.stats['promoters']:>4} ({(self.stats['promoters']/self.stats['total_responses']*100):.1f}%)
    • Passives (7-8):        {self.stats['passives']:>4} ({(self.stats['passives']/self.stats['total_responses']*100):.1f}%)
    • Detractors (0-6):      {self.stats['detractors']:>4} ({(self.stats['detractors']/self.stats['total_responses']*100):.1f}%)
"""
        
        if sentiment:
            report += f"""
SENTIMENT ANALYSIS:
    • Positive Feedback:     {sentiment['positive']:>4} ({sentiment['positive_pct']:.1f}%)
    • Neutral Feedback:      {sentiment['neutral']:>4} ({(sentiment['neutral']/self.stats['total_responses']*100):.1f}%)
    • Negative Feedback:     {sentiment['negative']:>4} ({(sentiment['negative']/self.stats['total_responses']*100):.1f}%)
"""
        
        if age_analysis is not None and not age_analysis.empty:
            report += f"""
{'='*75}
🎯 SEGMENT ANALYSIS
{'='*75}

PERFORMANCE BY AGE GROUP:
{self.format_segment_table(age_analysis)}
"""
        
        if region_analysis is not None and not region_analysis.empty:
            report += f"""
PERFORMANCE BY REGION:
{self.format_segment_table(region_analysis)}
"""
        
        report += f"""
TOP PERFORMERS:
  Best Region:               {self.stats['best_region']} ({self.stats['best_region_score']:.2f}/5 satisfaction)
  Best Age Group:            {self.stats['top_age_group']} ({self.stats['top_age_score']:.2f}/5 satisfaction)
"""
        
        # Gemini-powered insights
        report += f"""
{'='*75}
🤖 AI-POWERED INSIGHTS (GENERATED BY GEMINI)
{'='*75}

EXECUTIVE SUMMARY:
{self.get_llm_insights("summary")}

TREND ANALYSIS:
{self.get_llm_insights("trends")}

STRATEGIC RECOMMENDATIONS:
{self.get_llm_insights("recommendations")}
"""
        
        report += f"""
{'='*75}
📋 DATA QUALITY ASSESSMENT
{'='*75}
Total Data Points:         {len(self.df) * len(self.df.columns):,}
Missing Values:            {self.df.isnull().sum().sum()}
Duplicate Responses:       {self.df.duplicated().sum()}
Data Completeness:         {self.stats['completion_rate']:.2f}%
Quality Grade:             {'A+' if self.stats['completion_rate'] > 95 else 'A' if self.stats['completion_rate'] > 90 else 'B'}

{'='*75}
📊 STATISTICAL NOTES
{'='*75}
• NPS calculated as: (% Promoters - % Detractors)
• Standard deviation (σ) indicates response variability
• Segment analysis includes mean, std dev, and count
• Time series based on weekly aggregations
• Correlations calculated using Pearson method

╔═══════════════════════════════════════════════════════════════════════╗
║  Report Generated by AI Survey Analyzer v2.0                          ║
║  Powered by Google Gemini Flash 2.5                                   ║
╚═══════════════════════════════════════════════════════════════════════╝
"""
        
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"✅ Report saved to: {save_path}")
        return report
