
# AI 销售分析仪表板

[English](README.md) | 简体中文

基于 Streamlit 构建的 AI 销售分析仪表板，提供数据可视化、趋势分析及销售预测功能。

## 功能特性

- 📊 交互式销售数据可视化  
- 🤖 AI 生成的业务洞察  
- 📈 基于时间序列的销售预测  
- 📁 支持 CSV 数据导入（可使用 Kaggle 数据集）

## 技术栈

- Python 3.x  
- Streamlit  
- Pandas / Plotly  
- OpenAI API（或其他 AI 服务）

## 数据准备

从 [Kaggle](https://www.kaggle.com/datasets/vivek468/superstore-dataset-final) 下载数据集，并将其放置在 `data/` 目录下。

## 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 运行应用

```bash
streamlit run app.py
```

浏览器会自动打开 http://localhost:8501

## 项目结构

```
ai-sales-analytics/
├── app.py                 # Streamlit 主应用
├── data/
│   └── sales_data.csv     # Kaggle 销售数据集
├── modules/
│   ├── __init__.py
│   ├── data_loader.py     # 数据加载与预处理
│   ├── visualizations.py  # 图表与可视化组件
│   ├── ai_insights.py     # AI 分析模块
│   └── forecasting.py     # 销售预测模型
├── .streamlit/
│   └── config.toml        # Streamlit 配置
├── requirements.txt
└── README.md
```

## 许可证

MIT

