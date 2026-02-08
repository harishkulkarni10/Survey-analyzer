"""
Main entry point for Survey Analyzer
Production-grade survey analysis tool with Gemini-powered insights
"""

import sys
import os

# Fix Windows console encoding for emojis
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

from survey_analyzer import SurveyAnalyzer
from survey_analyzer.config import Config


def check_packages():
    """Check if required packages are installed"""
    print("🔍 Checking required packages...")
    all_ok = True
    
    try:
        import pandas as pd
        print(f"   ✅ pandas: {pd.__version__}")
    except ImportError:
        print("   ❌ pandas: NOT INSTALLED")
        all_ok = False
    
    try:
        import numpy as np
        print(f"   ✅ numpy: {np.__version__}")
    except ImportError:
        print("   ❌ numpy: NOT INSTALLED")
        all_ok = False
    
    try:
        import matplotlib
        print(f"   ✅ matplotlib: {matplotlib.__version__}")
    except ImportError:
        print("   ❌ matplotlib: NOT INSTALLED")
        all_ok = False
    
    try:
        import seaborn as sns
        print(f"   ✅ seaborn: {sns.__version__}")
    except ImportError:
        print("   ❌ seaborn: NOT INSTALLED")
        all_ok = False
    
    # Gemini check
    print()
    print("🔍 Checking Gemini...")
    gemini_ok = False
    try:
        import google.generativeai
        print(f"   ✅ google-generativeai: installed")
        gemini_ok = True
    except ImportError:
        print("   ❌ google-generativeai: NOT INSTALLED")
        print("      Run: pip install google-generativeai")
    
    # API key check
    api_key = Config.get_gemini_api_key()
    if api_key:
        print(f"   ✅ Gemini API key: set in api_key.py")
    else:
        print(f"   ❌ Gemini API key: not set")
        print(f"      Open api_key.py and paste your key")
    
    print()
    return all_ok, gemini_ok and (api_key is not None)


def main():
    """Main execution function"""
    
    print("="*75)
    print("  SURVEY ANALYSIS TOOL - GEMINI AI-POWERED INSIGHTS")
    print("="*75)
    print()
    
    # Check packages
    core_ok, gemini_ok = check_packages()
    if not core_ok:
        print("❌ Missing required packages. Run: pip install -r requirements.txt")
        sys.exit(1)
    
    if not gemini_ok:
        print("❌ Gemini is not ready. Make sure:")
        print("   1. pip install google-generativeai")
        print("   2. Add your API key in api_key.py")
        sys.exit(1)
    
    # Check if a file path was passed as argument
    data_source = None
    if len(sys.argv) > 1:
        data_source = sys.argv[1]
        if not os.path.exists(data_source):
            print(f"❌ File not found: {data_source}")
            sys.exit(1)
        print(f"📂 Data source: {data_source}")
    else:
        print("📂 Data source: Sample data (pass a file path to use your own)")
        print("   Usage: python main.py your_data.csv")
        print("   Supported: .csv, .xlsx, .xls, .pdf")
    
    # Initialize analyzer
    print()
    print("🚀 Starting Analysis...")
    print()
    
    analyzer = SurveyAnalyzer(data=data_source)
    
    # Run analysis steps
    print("📊 Step 1/5: Calculating statistics...", end=" ")
    try:
        analyzer.calculate_statistics()
        print("✅ DONE")
    except Exception as e:
        print(f"❌ FAILED: {e}")
        raise
    
    print("🎨 Step 2/5: Creating visualizations...", end=" ")
    try:
        viz_path = analyzer.create_visualizations()
        print(f"✅ DONE → {os.path.basename(viz_path)}")
    except Exception as e:
        print(f"❌ FAILED: {e}")
        raise
    
    print("📝 Step 3/5: Generating AI report (Gemini)...", end=" ")
    try:
        report = analyzer.generate_report()
        report_path = os.path.join(analyzer.output_dir, "survey_report.txt")
        print(f"✅ DONE → {os.path.basename(report_path)}")
    except Exception as e:
        print(f"❌ FAILED: {e}")
        raise
    
    print("💾 Step 4/5: Exporting data files...", end=" ")
    try:
        exported_files = analyzer.export_data()
        print(f"✅ DONE → {len(exported_files)} files exported")
    except Exception as e:
        print(f"❌ FAILED: {e}")
        raise
    
    print("🤖 Step 5/5: Generating output explanation (Gemini)...", end=" ")
    try:
        explanation_file = analyzer.generate_output_explanation(exported_files)
        print(f"✅ DONE → {os.path.basename(explanation_file)}")
    except Exception as e:
        print(f"❌ FAILED: {e}")
        raise
    
    # Final summary
    print("\n" + "="*75)
    print("✅ ANALYSIS COMPLETE!")
    print("="*75)
    
    output_dir = analyzer.output_dir
    abs_output_dir = os.path.abspath(output_dir)
    folder_name = os.path.basename(output_dir)
    
    print(f"\n📁 OUTPUT FOLDER: {folder_name}")
    print(f"📁 FULL PATH: {abs_output_dir}")
    print()
    print(f"🤖 LLM: {analyzer.llm_provider.name}")
    print("   All insights and explanations are generated by Gemini AI")
    print()
    print("📄 Generated Files:")
    print(f"   • survey_report.txt          - Full analysis report")
    print("                                └─ 🤖 AI insights by Gemini")
    print(f"   • output_explanation.txt     - AI explanation of all outputs")
    print("                                └─ 🤖 Fully written by Gemini")
    print(f"   • survey_visualizations.png  - Visual dashboard (8 charts)")
    print(f"   • age_group_analysis.csv     - Age demographics")
    print(f"   • regional_analysis.csv      - Regional breakdown")
    print(f"   • survey_raw_data.csv        - Complete dataset")
    print(f"   • statistics.json            - Calculated metrics")
    print()
    print("💡 Each run creates a NEW timestamped folder.")
    print(f"💡 Open: {abs_output_dir}")
    print()
    
    return analyzer


if __name__ == "__main__":
    try:
        analyzer = main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Analysis interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
