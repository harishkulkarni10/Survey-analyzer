# Survey Analyzer — Gemini AI-Powered Insights

## Setup

### 1. Add your Gemini API key

Open `api_key.py` and paste your key:

```python
GEMINI_API_KEY = "your_gemini_api_key_here"
```

### 2. Install dependencies

```powershell
cd Analysis
pip install -r requirements.txt
```

## Run

**With sample data (dummy):**

```powershell
python main.py
```

**With your own data:**

```powershell
python main.py your_file.csv
python main.py your_file.xlsx
python main.py your_file.pdf
```

Place your data files in the `Analysis` folder, or pass a full path.

## Outputs

Each run creates a **new timestamped folder** inside `outputs/`, e.g.:

```
outputs/
  analysis_20260208_190000/
    survey_report.txt          ← Full report with AI insights (Gemini)
    output_explanation.txt     ← AI explanation of all outputs (Gemini)
    survey_visualizations.png  ← Dashboard with 8 charts
    age_group_analysis.csv     ← Demographics breakdown
    regional_analysis.csv      ← Regional breakdown
    survey_raw_data.csv        ← Complete dataset
    statistics.json            ← All calculated metrics
```

The output folder path is printed in the terminal after each run.

## Project Structure

```
Analysis/
  api_key.py                   ← Your Gemini API key goes here
  main.py                      ← Entry point — run this
  requirements.txt             ← Dependencies
  survey_analyzer/
    config.py                  ← Settings
    llm_providers.py           ← Gemini API integration
    data_loader.py             ← CSV/Excel/PDF loading
    statistics.py              ← Statistical calculations
    visualizations.py          ← Chart generation
    report_generator.py        ← Report with AI insights
    analyzer.py                ← Orchestrator
```
