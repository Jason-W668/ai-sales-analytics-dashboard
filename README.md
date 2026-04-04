
# AI Sales Analytics Dashboard

English | [简体中文](README.zh.md)

An AI-powered sales analytics dashboard built with Streamlit, featuring data visualization, trend analysis, and sales forecasting.

## Features

- 📊 Interactive sales data visualization
- 🤖 AI-generated business insights
- 📈 Sales forecasting with time-series analysis
- 📁 CSV data import support (Kaggle dataset)

## Tech Stack

- Python 3.x
- Streamlit
- Pandas / Plotly
- OpenAI API (or your AI provider)

## Data Setup

Download the dataset from [Kaggle](https://www.kaggle.com/datasets/vivek468/superstore-dataset-final) and place it in the `data/` directory.

## Getting Started

### Prerequisites

```bash
pip install -r requirements.txt
```

### Run

```bash
streamlit run app.py
```

The browser will automatically open http://localhost:8501

## Project Structure

```
ai-sales-analytics/
├── app.py                 # Main Streamlit application
├── data/
│   └── sales_data.csv     # Kaggle sales dataset
├── modules/
│   ├── __init__.py
│   ├── data_loader.py     # Data loading and preprocessing
│   ├── visualizations.py  # Chart and graph components
│   ├── ai_insights.py     # AI-powered analysis
│   └── forecasting.py     # Sales forecasting models
├── .streamlit/
│   └── config.toml        # Streamlit configuration
├── requirements.txt
└── README.md
```

## License

MIT
