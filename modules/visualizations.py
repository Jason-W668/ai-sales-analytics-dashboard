"""
可视化模块
所有 Plotly 图表的创建函数，统一风格和配色
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np


# ======================== 全局配色 ========================

COLORS = {
    "primary": "#4FC3F7",
    "secondary": "#81C784",
    "accent": "#FFB74D",
    "danger": "#E57373",
    "purple": "#BA68C8",
    "teal": "#4DB6AC",
}

COLOR_SEQUENCE = [
    "#4FC3F7", "#81C784", "#FFB74D", "#E57373",
    "#BA68C8", "#4DB6AC", "#F06292", "#AED581",
    "#FFD54F", "#7986CB",
]


def _apply_layout(fig, title="", height=400):
    """统一图表样式"""
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#FAFAFA", size=12),
        margin=dict(l=20, r=20, t=50, b=20),
        title=dict(text=title, font=dict(size=16, color="#FAFAFA")),
        height=height,
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=11)),
    )
    fig.update_xaxes(gridcolor="rgba(128,128,128,0.1)", showgrid=True)
    fig.update_yaxes(gridcolor="rgba(128,128,128,0.1)", showgrid=True)
    return fig


# ======================== KPI 计算 ========================

def calc_kpi_metrics(df):
    """计算关键指标"""
    total_sales = df["Sales"].sum()
    total_profit = df["Profit"].sum()

    return {
        "total_sales": total_sales,
        "total_profit": total_profit,
        "total_orders": df["Order ID"].nunique(),
        "total_customers": df["Customer ID"].nunique(),
        "avg_order_value": df.groupby("Order ID")["Sales"].sum().mean()
            if df["Order ID"].nunique() > 0 else 0,
        "profit_margin": (total_profit / total_sales * 100)
            if total_sales > 0 else 0,
        "avg_discount": df["Discount"].mean() * 100,
        "total_quantity": df["Quantity"].sum(),
    }


# ======================== 图表函数 ========================

def plot_sales_trend(df, freq="M"):
    """月度/季度 销售额与利润趋势"""
    monthly = (
        df.set_index("Order Date")
        .resample(freq)
        .agg({"Sales": "sum", "Profit": "sum"})
        .reset_index()
    )

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=monthly["Order Date"], y=monthly["Sales"],
            name="Sales", mode="lines+markers",
            line=dict(color=COLORS["primary"], width=2.5),
            marker=dict(size=5),
            fill="tozeroy",
            fillcolor="rgba(79, 195, 247, 0.08)",
        )
    )

    fig.add_trace(
        go.Scatter(
            x=monthly["Order Date"], y=monthly["Profit"],
            name="Profit", mode="lines+markers",
            line=dict(color=COLORS["secondary"], width=2.5),
            marker=dict(size=5),
            fill="tozeroy",
            fillcolor="rgba(129, 199, 132, 0.08)",
        )
    )

    _apply_layout(fig, "📈 Sales & Profit Trend", height=420)
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Amount ($)",
        hovermode="x unified",
    )
    return fig


def plot_regional_sales(df):
    """各地区销售额与利润 - 水平柱状图"""
    regional = (
        df.groupby("Region")
        .agg({"Sales": "sum", "Profit": "sum"})
        .reset_index()
        .sort_values("Sales", ascending=True)
    )

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            y=regional["Region"], x=regional["Sales"],
            name="Sales", orientation="h",
            marker_color=COLORS["primary"],
            text=regional["Sales"].apply(lambda x: f"${x:,.0f}"),
            textposition="auto",
        )
    )

    fig.add_trace(
        go.Bar(
            y=regional["Region"], x=regional["Profit"],
            name="Profit", orientation="h",
            marker_color=COLORS["secondary"],
            text=regional["Profit"].apply(lambda x: f"${x:,.0f}"),
            textposition="auto",
        )
    )

    _apply_layout(fig, "🗺️ Sales & Profit by Region", height=350)
    fig.update_layout(barmode="group")
    return fig


def plot_category_bar(df):
    """按产品类别的销售额与利润"""
    cat = (
        df.groupby("Category")
        .agg({"Sales": "sum", "Profit": "sum", "Quantity": "sum"})
        .reset_index()
        .sort_values("Sales", ascending=False)
    )

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=cat["Category"], y=cat["Sales"],
            name="Sales", marker_color=COLORS["primary"],
            text=cat["Sales"].apply(lambda x: f"${x:,.0f}"),
            textposition="auto",
        )
    )

    fig.add_trace(
        go.Bar(
            x=cat["Category"], y=cat["Profit"],
            name="Profit", marker_color=COLORS["secondary"],
            text=cat["Profit"].apply(lambda x: f"${x:,.0f}"),
            textposition="auto",
        )
    )

    _apply_layout(fig, "📦 Sales & Profit by Category", height=380)
    fig.update_layout(barmode="group")
    return fig


def plot_category_sunburst(df):
    """类别与子类别的旭日图"""
    cat_data = (
        df.groupby(["Category", "Sub-Category"])
        .agg({"Sales": "sum"})
        .reset_index()
    )

    fig = px.sunburst(
        cat_data,
        path=["Category", "Sub-Category"],
        values="Sales",
        color="Sales",
        color_continuous_scale="Blues",
    )

    _apply_layout(fig, "🏷️ Category & Sub-Category Breakdown", height=480)
    fig.update_layout(coloraxis_showscale=False)
    return fig


def plot_subcategory_profit(df):
    """子类别利润分析 - 红绿柱状图"""
    sub = df.groupby("Sub-Category")["Profit"].sum().reset_index()
    sub = sub.sort_values("Profit", ascending=True)

    colors = ["#E57373" if p < 0 else "#81C784" for p in sub["Profit"]]

    fig = go.Figure(
        go.Bar(
            y=sub["Sub-Category"], x=sub["Profit"],
            orientation="h", marker_color=colors,
            text=sub["Profit"].apply(lambda x: f"${x:,.0f}"),
            textposition="outside",
        )
    )

    _apply_layout(fig, "💰 Profit by Sub-Category (Red = Loss)", height=520)
    fig.update_layout(xaxis_title="Profit ($)")
    return fig


def plot_segment_donut(df):
    """客户分类占比 - 环形图"""
    seg = df.groupby("Segment")["Sales"].sum().reset_index()

    fig = go.Figure(
        go.Pie(
            labels=seg["Segment"], values=seg["Sales"],
            hole=0.5,
            marker_colors=COLOR_SEQUENCE[:3],
            textinfo="label+percent",
            textposition="outside",
            pull=[0.03] * len(seg),
        )
    )

    _apply_layout(fig, "👥 Sales by Customer Segment", height=380)
    return fig


def plot_top_products(df, n=10):
    """TOP N 产品 - 水平柱状图"""
    top = df.groupby("Product Name")["Sales"].sum().nlargest(n).reset_index()
    top = top.sort_values("Sales", ascending=True)
    top["Short Name"] = top["Product Name"].apply(
        lambda x: x[:45] + "..." if len(x) > 45 else x
    )

    fig = go.Figure(
        go.Bar(
            y=top["Short Name"], x=top["Sales"],
            orientation="h",
            marker=dict(color=top["Sales"], colorscale="Blues"),
            text=top["Sales"].apply(lambda x: f"${x:,.0f}"),
            textposition="outside",
        )
    )

    _apply_layout(fig, f"🏆 Top {n} Products by Sales", height=max(350, n * 40))
    return fig


def plot_top_customers(df, n=10):
    """TOP N 客户 - 水平柱状图"""
    top = (
        df.groupby("Customer Name")
        .agg({"Sales": "sum", "Profit": "sum", "Order ID": "nunique"})
        .reset_index()
        .nlargest(n, "Sales")
        .sort_values("Sales", ascending=True)
    )

    fig = go.Figure(
        go.Bar(
            y=top["Customer Name"], x=top["Sales"],
            orientation="h",
            marker=dict(color=top["Sales"], colorscale="Teal"),
            text=top["Sales"].apply(lambda x: f"${x:,.0f}"),
            textposition="outside",
        )
    )

    _apply_layout(fig, f"👤 Top {n} Customers by Sales", height=max(350, n * 38))
    return fig


def plot_state_map(df):
    """美国各州销售额热力地图"""
    state_abbrev = {
        "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR",
        "California": "CA", "Colorado": "CO", "Connecticut": "CT",
        "Delaware": "DE", "Florida": "FL", "Georgia": "GA", "Hawaii": "HI",
        "Idaho": "ID", "Illinois": "IL", "Indiana": "IN", "Iowa": "IA",
        "Kansas": "KS", "Kentucky": "KY", "Louisiana": "LA", "Maine": "ME",
        "Maryland": "MD", "Massachusetts": "MA", "Michigan": "MI",
        "Minnesota": "MN", "Mississippi": "MS", "Missouri": "MO",
        "Montana": "MT", "Nebraska": "NE", "Nevada": "NV",
        "New Hampshire": "NH", "New Jersey": "NJ", "New Mexico": "NM",
        "New York": "NY", "North Carolina": "NC", "North Dakota": "ND",
        "Ohio": "OH", "Oklahoma": "OK", "Oregon": "OR",
        "Pennsylvania": "PA", "Rhode Island": "RI", "South Carolina": "SC",
        "South Dakota": "SD", "Tennessee": "TN", "Texas": "TX",
        "Utah": "UT", "Vermont": "VT", "Virginia": "VA",
        "Washington": "WA", "West Virginia": "WV", "Wisconsin": "WI",
        "Wyoming": "WY", "District of Columbia": "DC",
    }

    state_data = (
        df.groupby("State")
        .agg({"Sales": "sum", "Profit": "sum"})
        .reset_index()
    )
    state_data["State Code"] = state_data["State"].map(state_abbrev)
    state_data = state_data.dropna(subset=["State Code"])

    fig = go.Figure(
        go.Choropleth(
            locations=state_data["State Code"],
            z=state_data["Sales"],
            locationmode="USA-states",
            colorscale="Blues",
            colorbar_title="Sales ($)",
            text=state_data.apply(
                lambda x: (
                    f"{x['State']}<br>"
                    f"Sales: ${x['Sales']:,.0f}<br>"
                    f"Profit: ${x['Profit']:,.0f}"
                ),
                axis=1,
            ),
            hoverinfo="text",
        )
    )

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#FAFAFA", size=12),
        title=dict(
            text="🗺️ Sales Distribution by State",
            font=dict(size=16, color="#FAFAFA"),
        ),
        height=480,
        margin=dict(l=0, r=0, t=50, b=0),
        geo=dict(
            scope="usa",
            bgcolor="rgba(0,0,0,0)",
            lakecolor="rgba(30,33,48,0.5)",
            landcolor="rgba(30,33,48,1)",
            showlakes=True,
        ),
    )
    return fig


def plot_top_states(df, n=10):
    """TOP N 州 - 柱状图"""
    top = df.groupby("State")["Sales"].sum().nlargest(n).reset_index()
    top = top.sort_values("Sales", ascending=True)

    fig = go.Figure(
        go.Bar(
            y=top["State"], x=top["Sales"],
            orientation="h",
            marker=dict(color=top["Sales"], colorscale="Blues"),
            text=top["Sales"].apply(lambda x: f"${x:,.0f}"),
            textposition="outside",
        )
    )

    _apply_layout(fig, f"🏅 Top {n} States by Sales", height=max(350, n * 38))
    return fig


def plot_top_cities(df, n=10):
    """TOP N 城市 - 柱状图"""
    top = df.groupby("City")["Sales"].sum().nlargest(n).reset_index()
    top = top.sort_values("Sales", ascending=True)

    fig = go.Figure(
        go.Bar(
            y=top["City"], x=top["Sales"],
            orientation="h",
            marker=dict(color=top["Sales"], colorscale="Teal"),
            text=top["Sales"].apply(lambda x: f"${x:,.0f}"),
            textposition="outside",
        )
    )

    _apply_layout(fig, f"🏙️ Top {n} Cities by Sales", height=max(350, n * 38))
    return fig


def plot_discount_vs_profit(df):
    """折扣率 vs 利润 散点图"""
    # 采样避免性能问题
    sample = df.sample(min(2000, len(df)), random_state=42) if len(df) > 2000 else df

    fig = px.scatter(
        sample,
        x="Discount", y="Profit",
        color="Category",
        opacity=0.5,
        color_discrete_sequence=COLOR_SEQUENCE,
        hover_data=["Product Name", "Sales", "Sub-Category"],
    )

    # 添加零利润参考线
    fig.add_hline(y=0, line_dash="dash", line_color="rgba(255,255,255,0.3)")

    _apply_layout(fig, "🏷️ Discount vs Profit (by Category)", height=420)
    fig.update_layout(xaxis_title="Discount Rate", yaxis_title="Profit ($)")
    return fig


def plot_ship_mode(df):
    """配送方式分布"""
    ship = (
        df.groupby("Ship Mode")
        .agg({"Order ID": "nunique", "Shipping Days": "mean"})
        .reset_index()
    )
    ship.columns = ["Ship Mode", "Orders", "Avg Days"]
    ship = ship.sort_values("Orders", ascending=True)

    fig = go.Figure(
        go.Bar(
            y=ship["Ship Mode"], x=ship["Orders"],
            orientation="h",
            marker_color=COLOR_SEQUENCE[:len(ship)],
            text=ship.apply(
                lambda r: f"{r['Orders']:,} orders (avg {r['Avg Days']:.1f} days)",
                axis=1,
            ),
            textposition="auto",
        )
    )

    _apply_layout(fig, "🚚 Orders by Ship Mode", height=300)
    return fig


def plot_yearly_comparison(df):
    """年度同比对比折线图"""
    yearly = (
        df.groupby(["Year", "Month"])
        .agg({"Sales": "sum"})
        .reset_index()
    )

    fig = px.line(
        yearly, x="Month", y="Sales",
        color="Year",
        color_discrete_sequence=COLOR_SEQUENCE,
        markers=True,
    )

    month_labels = [
        "Jan", "Feb", "Mar", "Apr", "May", "Jun",
        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
    ]
    fig.update_xaxes(
        tickmode="array",
        tickvals=list(range(1, 13)),
        ticktext=month_labels,
    )

    _apply_layout(fig, "📅 Year-over-Year Sales Comparison", height=420)
    fig.update_layout(xaxis_title="Month", yaxis_title="Sales ($)")
    return fig


def plot_quarterly_heatmap(df):
    """季度销售额热力图"""
    pivot = df.pivot_table(
        values="Sales", index="Year", columns="Quarter", aggfunc="sum"
    ).round(0)

    fig = go.Figure(
        go.Heatmap(
            z=pivot.values,
            x=[f"Q{q}" for q in pivot.columns],
            y=pivot.index.astype(str),
            colorscale="Blues",
            text=[[f"${v:,.0f}" for v in row] for row in pivot.values],
            texttemplate="%{text}",
            textfont=dict(size=13),
            hoverongaps=False,
        )
    )

    _apply_layout(fig, "📊 Quarterly Sales Heatmap", height=300)
    return fig


def plot_monthly_category_trend(df):
    """各类别月度销售趋势"""
    monthly_cat = (
        df.groupby([pd.Grouper(key="Order Date", freq="M"), "Category"])["Sales"]
        .sum()
        .reset_index()
    )

    fig = px.area(
        monthly_cat,
        x="Order Date", y="Sales",
        color="Category",
        color_discrete_sequence=COLOR_SEQUENCE,
    )

    _apply_layout(fig, "📈 Monthly Sales by Category", height=400)
    fig.update_layout(xaxis_title="Date", yaxis_title="Sales ($)")
    return fig