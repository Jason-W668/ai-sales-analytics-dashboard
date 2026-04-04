"""
数据加载与预处理模块
处理 Superstore Sales Dataset 的读取、清洗、派生列计算
"""

import pandas as pd
import numpy as np
import streamlit as st


@st.cache_data
def load_data(filepath="data/sales_data.csv"):
    """
    加载并预处理 Superstore 销售数据
    自动处理编码、日期解析、派生列计算
    """

    # 尝试多种编码格式读取
    df = None
    for encoding in ["utf-8", "latin-1", "cp1252", "iso-8859-1"]:
        try:
            df = pd.read_csv(filepath, encoding=encoding)
            break
        except (UnicodeDecodeError, FileNotFoundError):
            continue

    if df is None:
        st.error("❌ 无法读取数据文件，请检查 data/sales_data.csv 是否存在")
        st.stop()

    # ---------- 列名标准化 ----------
    # 处理可能的列名差异（如空格、大小写）
    df.columns = df.columns.str.strip()

    # 处理 "Sub-Category" vs "Sub Category" 差异
    col_mapping = {}
    for col in df.columns:
        if col.lower().replace("-", "").replace(" ", "") == "subcategory":
            col_mapping[col] = "Sub-Category"
    if col_mapping:
        df = df.rename(columns=col_mapping)

    # ---------- 日期解析 ----------
    df["Order Date"] = pd.to_datetime(df["Order Date"], format="mixed", dayfirst=False)
    df["Ship Date"] = pd.to_datetime(df["Ship Date"], format="mixed", dayfirst=False)

    # ---------- 派生列 ----------
    df["Year"] = df["Order Date"].dt.year
    df["Month"] = df["Order Date"].dt.month
    df["Month Name"] = df["Order Date"].dt.strftime("%b")
    df["Quarter"] = df["Order Date"].dt.quarter
    df["Year-Quarter"] = df["Year"].astype(str) + "-Q" + df["Quarter"].astype(str)
    df["Year-Month"] = df["Order Date"].dt.strftime("%Y-%m")
    df["Day of Week"] = df["Order Date"].dt.day_name()

    # 利润率（处理除零）
    df["Profit Margin (%)"] = np.where(
        df["Sales"] > 0, (df["Profit"] / df["Sales"] * 100).round(2), 0
    )

    # 运输天数
    df["Shipping Days"] = (df["Ship Date"] - df["Order Date"]).dt.days

    # 单件收入
    df["Revenue per Unit"] = np.where(
        df["Quantity"] > 0, (df["Sales"] / df["Quantity"]).round(2), 0
    )

    # 处理缺失值
    if "Postal Code" in df.columns:
        df["Postal Code"] = df["Postal Code"].fillna(0).astype(int)

    return df


def get_filtered_data(df, date_range=None, regions=None, categories=None,
                      segments=None, states=None):
    """
    根据用户筛选条件过滤数据
    """
    filtered = df.copy()

    if date_range and len(date_range) == 2:
        filtered = filtered[
            (filtered["Order Date"].dt.date >= date_range[0])
            & (filtered["Order Date"].dt.date <= date_range[1])
        ]

    if regions and len(regions) > 0:
        filtered = filtered[filtered["Region"].isin(regions)]

    if categories and len(categories) > 0:
        filtered = filtered[filtered["Category"].isin(categories)]

    if segments and len(segments) > 0:
        filtered = filtered[filtered["Segment"].isin(segments)]

    if states and len(states) > 0:
        filtered = filtered[filtered["State"].isin(states)]

    return filtered


def get_data_summary(df):
    """
    生成全面的数据摘要文本，供 AI 分析使用
    """
    total_sales = df["Sales"].sum()
    total_profit = df["Profit"].sum()
    profit_margin = (total_profit / total_sales * 100) if total_sales > 0 else 0

    summary = f"""
=== SUPERSTORE SALES DATA SUMMARY ===

📋 OVERVIEW:
- Total Records: {len(df):,}
- Date Range: {df['Order Date'].min().strftime('%Y-%m-%d')} to {df['Order Date'].max().strftime('%Y-%m-%d')}
- Total Sales Revenue: ${total_sales:,.2f}
- Total Profit: ${total_profit:,.2f}
- Overall Profit Margin: {profit_margin:.2f}%
- Unique Orders: {df['Order ID'].nunique():,}
- Unique Customers: {df['Customer ID'].nunique():,}
- Average Order Value: ${df.groupby('Order ID')['Sales'].sum().mean():,.2f}
- Average Discount: {df['Discount'].mean() * 100:.1f}%

📦 SALES BY CATEGORY:
{df.groupby('Category').agg({'Sales': 'sum', 'Profit': 'sum', 'Quantity': 'sum'}).round(2).to_string()}

📦 SALES BY SUB-CATEGORY:
{df.groupby('Sub-Category').agg({'Sales': 'sum', 'Profit': 'sum', 'Quantity': 'sum'}).sort_values('Sales', ascending=False).round(2).to_string()}

🗺️ SALES BY REGION:
{df.groupby('Region').agg({'Sales': 'sum', 'Profit': 'sum', 'Order ID': 'nunique'}).round(2).to_string()}

👥 SALES BY SEGMENT:
{df.groupby('Segment').agg({'Sales': 'sum', 'Profit': 'sum', 'Order ID': 'nunique'}).round(2).to_string()}

🚚 SHIPPING MODE:
{df.groupby('Ship Mode').agg({'Sales': 'sum', 'Shipping Days': 'mean', 'Order ID': 'nunique'}).round(2).to_string()}

📈 MONTHLY TREND (Last 12 Months):
{df.groupby('Year-Month').agg({'Sales': 'sum', 'Profit': 'sum'}).tail(12).round(2).to_string()}

🏆 TOP 10 STATES BY SALES:
{df.groupby('State')['Sales'].sum().nlargest(10).round(2).to_string()}

📉 BOTTOM 5 SUB-CATEGORIES BY PROFIT:
{df.groupby('Sub-Category')['Profit'].sum().nsmallest(5).round(2).to_string()}

🏷️ DISCOUNT ANALYSIS:
- Orders with Discount > 0: {len(df[df['Discount'] > 0]):,} ({len(df[df['Discount'] > 0]) / len(df) * 100:.1f}%)
- Average Discount on discounted items: {df[df['Discount'] > 0]['Discount'].mean() * 100:.1f}%
- Profit on discounted items: ${df[df['Discount'] > 0]['Profit'].sum():,.2f}
- Profit on non-discounted items: ${df[df['Discount'] == 0]['Profit'].sum():,.2f}
"""
    return summary