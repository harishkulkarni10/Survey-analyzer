"""
Visualization module for Survey Analyzer
Creates comprehensive dashboard with multiple charts
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Optional

from .config import Config
from .statistics import StatisticsCalculator


class VisualizationGenerator:
    """Handles creation of visualization dashboards"""
    
    def __init__(self, df: pd.DataFrame):
        """
        Initialize visualization generator
        
        Args:
            df: DataFrame with survey data
        """
        self.df = df
        self.stats_calc = StatisticsCalculator()
    
    def create_dashboard(self, save_path: Optional[str] = None) -> plt.Figure:
        """
        Create comprehensive visualization dashboard
        
        Args:
            save_path: Optional custom path to save visualization
            
        Returns:
            Matplotlib figure object
        """
        save_path = save_path or Config.get_visualization_path()
        
        # Set style
        sns.set_style("whitegrid")
        plt.rcParams['figure.facecolor'] = 'white'
        
        fig = plt.figure(figsize=Config.FIGURE_SIZE)
        gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
        
        # Main title
        fig.suptitle('Survey Analysis Dashboard', fontsize=20, fontweight='bold', y=0.98)
        
        # 1. Satisfaction Distribution
        ax1 = fig.add_subplot(gs[0, 0])
        if 'satisfaction' in self.df.columns:
            self.df['satisfaction'].hist(bins=5, ax=ax1, color='#4ECDC4', edgecolor='black', alpha=0.7)
            ax1.set_title('Overall Satisfaction Distribution', fontweight='bold', fontsize=11)
            ax1.set_xlabel('Score (1-5)')
            ax1.set_ylabel('Frequency')
            mean_sat = self.df['satisfaction'].mean()
            ax1.axvline(mean_sat, color='red', linestyle='--', label=f'Mean: {mean_sat:.2f}')
            ax1.legend()
        
        # 2. Metrics Comparison
        ax2 = fig.add_subplot(gs[0, 1])
        metrics = ['satisfaction', 'product_quality', 'customer_service', 'value_for_money']
        metric_labels = ['Satisfaction', 'Quality', 'Service', 'Value']
        available_metrics = [(m, ml) for m, ml in zip(metrics, metric_labels) if m in self.df.columns]
        
        if available_metrics:
            metric_cols, metric_labs = zip(*available_metrics)
            avg_scores = [self.df[m].mean() for m in metric_cols]
            colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4'][:len(avg_scores)]
            bars = ax2.barh(metric_labs, avg_scores, color=colors)
            ax2.set_title('Average Scores by Metric', fontweight='bold', fontsize=11)
            ax2.set_xlabel('Average Score')
            ax2.set_xlim(0, 5)
            for i, bar in enumerate(bars):
                width = bar.get_width()
                ax2.text(width, bar.get_y() + bar.get_height()/2, 
                        f'{width:.2f}', ha='left', va='center', fontweight='bold')
        
        # 3. NPS Distribution
        ax3 = fig.add_subplot(gs[0, 2])
        if 'likelihood_to_recommend' in self.df.columns:
            nps_categories = pd.cut(self.df['likelihood_to_recommend'], 
                                   bins=[0, 6, 8, 10], 
                                   labels=['Detractors\n(0-6)', 'Passives\n(7-8)', 'Promoters\n(9-10)'])
            nps_counts = nps_categories.value_counts()
            colors_pie = ['#FF6B6B', '#FFA07A', '#90EE90']
            wedges, texts, autotexts = ax3.pie(nps_counts, labels=nps_counts.index, autopct='%1.1f%%',
                                                colors=colors_pie, startangle=90)
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
            nps_score = self.stats_calc.calculate_nps(self.df)
            ax3.set_title(f'NPS Distribution (Score: {nps_score:.1f})', 
                         fontweight='bold', fontsize=11)
        
        # 4. Regional Analysis
        ax4 = fig.add_subplot(gs[1, 0])
        if 'region' in self.df.columns and 'satisfaction' in self.df.columns:
            regional = self.df.groupby('region')['satisfaction'].mean().sort_values(ascending=True)
            regional.plot(kind='barh', ax=ax4, color='coral')
            ax4.set_title('Satisfaction by Region', fontweight='bold', fontsize=11)
            ax4.set_xlabel('Average Satisfaction')
            for i, v in enumerate(regional):
                ax4.text(v, i, f' {v:.2f}', va='center', fontweight='bold')
        
        # 5. Age Group Analysis
        ax5 = fig.add_subplot(gs[1, 1])
        if 'age_group' in self.df.columns:
            age_cols = ['satisfaction', 'product_quality', 'customer_service']
            available_age_cols = [col for col in age_cols if col in self.df.columns]
            if available_age_cols:
                age_data = self.df.groupby('age_group')[available_age_cols].mean()
                age_data.plot(kind='bar', ax=ax5, width=0.8)
                ax5.set_title('Metrics by Age Group', fontweight='bold', fontsize=11)
                ax5.set_xlabel('Age Group')
                ax5.set_ylabel('Average Score')
                ax5.legend(available_age_cols, loc='lower right')
                ax5.tick_params(axis='x', rotation=45)
                plt.setp(ax5.xaxis.get_majorticklabels(), rotation=45, ha='right')
        
        # 6. Recommendation Score Distribution
        ax6 = fig.add_subplot(gs[1, 2])
        if 'likelihood_to_recommend' in self.df.columns:
            self.df['likelihood_to_recommend'].hist(bins=11, ax=ax6, color='#96CEB4', 
                                                    edgecolor='black', alpha=0.7)
            ax6.set_title('Likelihood to Recommend', fontweight='bold', fontsize=11)
            ax6.set_xlabel('Score (0-10)')
            ax6.set_ylabel('Frequency')
            mean_rec = self.df['likelihood_to_recommend'].mean()
            ax6.axvline(mean_rec, color='red', linestyle='--', label=f'Mean: {mean_rec:.1f}')
            ax6.legend()
        
        # 7. Time Series Analysis
        ax7 = fig.add_subplot(gs[2, :2])
        if 'timestamp' in self.df.columns and 'satisfaction' in self.df.columns:
            time_series = self.df.set_index('timestamp').resample('W')['satisfaction'].mean()
            ax7.plot(time_series.index, time_series.values, marker='o', color='#4ECDC4', linewidth=2)
            ax7.fill_between(time_series.index, time_series.values, alpha=0.3, color='#4ECDC4')
            ax7.set_title('Satisfaction Trend Over Time (Weekly Average)', fontweight='bold', fontsize=11)
            ax7.set_xlabel('Date')
            ax7.set_ylabel('Average Satisfaction')
            ax7.grid(True, alpha=0.3)
            ax7.tick_params(axis='x', rotation=45)
            plt.setp(ax7.xaxis.get_majorticklabels(), rotation=45, ha='right')
        
        # 8. Correlation Heatmap
        ax8 = fig.add_subplot(gs[2, 2])
        corr_cols = ['satisfaction', 'product_quality', 'customer_service', 'value_for_money']
        available_corr_cols = [col for col in corr_cols if col in self.df.columns]
        if len(available_corr_cols) > 1:
            correlation = self.df[available_corr_cols].corr()
            sns.heatmap(correlation, annot=True, fmt='.2f', cmap='coolwarm', center=0,
                       square=True, ax=ax8, cbar_kws={"shrink": 0.8})
            ax8.set_title('Metric Correlations', fontweight='bold', fontsize=11)
        
        plt.tight_layout()
        
        # Save
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=Config.DPI, bbox_inches='tight')
        print(f"✅ Visualizations saved to: {save_path}")
        
        return fig
