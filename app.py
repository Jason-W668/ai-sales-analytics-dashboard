"""
📊 AI-Powered Sales Analytics Dashboard
主应用入口 - 整合所有模块
"""

import streamlit as st
import pandas as pd

from modules.data_loader import load_data, get_filtered_data, get_data_summary
from modules.visualizations import (
    calc_kpi_metrics,
    plot_sales_trend,
    plot_regional_sales,
    plot_category_bar,
    plot_category_sunburst,
    plot_subcategory_profit,
    plot_segment_donut,
    plot_top_products,
    plot_top_customers,
    plot_state_map,
    plot_top_states,
    plot_top_cities,
    plot_discount_vs_profit,
    plot_ship_mode,
    plot_yearly_comparison,
    plot_quarterly_heatmap,
    plot_monthly_category_trend,
)
from modules.ai_insights import generate_insights, answer_question
from modules.forecasting import (
    prepare_time_series,
    forecast_sales,
    plot_forecast,
)


# ================================================================
#                         页面配置
# ================================================================

st.set_page_config(
    page_title="AI Sales Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ================================================================
#                       自定义 CSS
# ================================================================

st.markdown(
    """
<style>
    /* ---------- KPI 卡片 ---------- */
    .kpi-card {
        background: linear-gradient(135deg, #1a1f36 0%, #252b48 100%);
        border-radius: 14px;
        padding: 22px 16px;
        text-align: center;
        border: 1px solid rgba(79, 195, 247, 0.15);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .kpi-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 25px rgba(79, 195, 247, 0.15);
    }
    .kpi-value {
        font-size: 26px;
        font-weight: 700;
        color: #4FC3F7;
        margin: 6px 0 2px 0;
        line-height: 1.2;
    }
    .kpi-value.green { color: #81C784; }
    .kpi-value.orange { color: #FFB74D; }
    .kpi-value.purple { color: #BA68C8; }
    .kpi-label {
        font-size: 11px;
        color: #9e9e9e;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        font-weight: 500;
    }

    /* ---------- 标题 ---------- */
    .main-header {
        font-size: 38px;
        font-weight: 800;
        background: linear-gradient(120deg, #4FC3F7 0%, #81C784 50%, #FFB74D 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0;
        padding-top: 10px;
    }
    .sub-header {
        font-size: 15px;
        color: #888;
        text-align: center;
        margin-bottom: 25px;
    }

    /* ---------- 分隔线 ---------- */
    .section-divider {
        border: none;
        border-top: 1px solid rgba(79, 195, 247, 0.12);
        margin: 25px 0;
    }

    /* ---------- 信息条 ---------- */
    .info-bar {
        background: rgba(79, 195, 247, 0.08);
        border-left: 3px solid #4FC3F7;
        padding: 10px 16px;
        border-radius: 0 8px 8px 0;
        margin-bottom: 20px;
        font-size: 13px;
        color: #ccc;
    }

    /* ---------- Tab 样式优化 ---------- */
    .stTabs [data-baseweb="tab-list"] { gap: 4px; }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0;
        padding: 10px 20px;
        font-size: 14px;
    }

    /* ---------- 侧边栏 ---------- */
    section[data-testid="stSidebar"] > div { padding-top: 1rem; }
</style>
""",
    unsafe_allow_html=True,
)


# ================================================================
#                         加载数据
# ================================================================

df = load_data()


# ================================================================
#                         侧边栏
# ================================================================

with st.sidebar:
    st.markdown("# 🎛️ Control Panel")
    st.markdown("---")

    # ---- 日期筛选 ----
    st.markdown("### 📅 Date Range")
    min_date = df["Order Date"].min().date()
    max_date = df["Order Date"].max().date()
    date_range = st.date_input(
        "Select Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
        label_visibility="collapsed",
    )

    st.markdown("### 🗺️ Region")
    all_regions = sorted(df["Region"].unique())
    regions = st.multiselect("Region", options=all_regions, default=[],
                             label_visibility="collapsed")

    st.markdown("### 📦 Category")
    all_categories = sorted(df["Category"].unique())
    categories = st.multiselect("Category", options=all_categories, default=[],
                                label_visibility="collapsed")

    st.markdown("### 👥 Segment")
    all_segments = sorted(df["Segment"].unique())
    segments = st.multiselect("Segment", options=all_segments, default=[],
                              label_visibility="collapsed")

    st.markdown("---")
    st.markdown("### 🤖 AI Configuration")
    api_key = st.text_input(
        "OpenAI API Key",
        type="password",
        help="Required for AI Insights and Ask AI features. Get yours at platform.openai.com",
    )

    st.markdown("---")
    st.markdown(
        """
    <div style='text-align:center; color:#555; font-size:11px; line-height:1.6;'>
        📊 AI Sales Analytics<br>
        Built with Streamlit · Plotly · OpenAI<br>
        <span style='color:#4FC3F7;'>v1.0</span>
    </div>
    """,
        unsafe_allow_html=True,
    )


# ================================================================
#                    应用筛选条件
# ================================================================

filtered_df = get_filtered_data(
    df,
    date_range=date_range if isinstance(date_range, tuple) and len(date_range) == 2 else None,
    regions=regions or None,
    categories=categories or None,
    segments=segments or None,
)

# 空数据检测
if len(filtered_df) == 0:
    st.warning("⚠️ No data matches your filters. Please adjust the filters in the sidebar.")
    st.stop()


# ================================================================
#                         页头
# ================================================================

st.markdown(
    '<div class="main-header">📊 AI-Powered Sales Analytics</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="sub-header">Interactive Dashboard with Predictive Insights & Natural Language Query</div>',
    unsafe_allow_html=True,
)

# 信息栏
st.markdown(
    f"""<div class="info-bar">
    📋 <strong>{len(filtered_df):,}</strong> records &nbsp;|&nbsp;
    🛒 <strong>{filtered_df['Order ID'].nunique():,}</strong> orders &nbsp;|&nbsp;
    👤 <strong>{filtered_df['Customer ID'].nunique():,}</strong> customers &nbsp;|&nbsp;
    📅 {filtered_df['Order Date'].min().strftime('%b %d, %Y')} — {filtered_df['Order Date'].max().strftime('%b %d, %Y')}
    </div>""",
    unsafe_allow_html=True,
)


# ================================================================
#                         TAB 布局
# ================================================================

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
    [
        "📊 Overview",
        "📈 Sales Deep Dive",
        "🗺️ Regional Analysis",
        "🏷️ Products & Customers",
        "🤖 AI Insights",
        "🔮 Forecast & Ask AI",
    ]
)


# ======================== TAB 1: OVERVIEW ========================
with tab1:

    kpis = calc_kpi_metrics(filtered_df)

    # ----- 第一行 KPI -----
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown(
            f"""<div class="kpi-card">
            <div class="kpi-label">Total Revenue</div>
            <div class="kpi-value">${kpis['total_sales']:,.0f}</div>
            </div>""",
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            f"""<div class="kpi-card">
            <div class="kpi-label">Total Profit</div>
            <div class="kpi-value green">${kpis['total_profit']:,.0f}</div>
            </div>""",
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            f"""<div class="kpi-card">
            <div class="kpi-label">Total Orders</div>
            <div class="kpi-value orange">{kpis['total_orders']:,}</div>
            </div>""",
            unsafe_allow_html=True,
        )
    with c4:
        st.markdown(
            f"""<div class="kpi-card">
            <div class="kpi-label">Profit Margin</div>
            <div class="kpi-value purple">{kpis['profit_margin']:.1f}%</div>
            </div>""",
            unsafe_allow_html=True,
        )

    st.markdown("")

    # ----- 第二行 KPI -----
    c5, c6, c7, c8 = st.columns(4)

    with c5:
        st.markdown(
            f"""<div class="kpi-card">
            <div class="kpi-label">Avg Order Value</div>
            <div class="kpi-value">${kpis['avg_order_value']:,.0f}</div>
            </div>""",
            unsafe_allow_html=True,
        )
    with c6:
        st.markdown(
            f"""<div class="kpi-card">
            <div class="kpi-label">Customers</div>
            <div class="kpi-value green">{kpis['total_customers']:,}</div>
            </div>""",
            unsafe_allow_html=True,
        )
    with c7:
        st.markdown(
            f"""<div class="kpi-card">
            <div class="kpi-label">Avg Discount</div>
            <div class="kpi-value orange">{kpis['avg_discount']:.1f}%</div>
            </div>""",
            unsafe_allow_html=True,
        )
    with c8:
        st.markdown(
            f"""<div class="kpi-card">
            <div class="kpi-label">Items Sold</div>
            <div class="kpi-value purple">{kpis['total_quantity']:,}</div>
            </div>""",
            unsafe_allow_html=True,
        )

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    # ----- 销售趋势 -----
    st.plotly_chart(plot_sales_trend(filtered_df), use_container_width=True)

    # ----- 类别 + 地区 -----
    col_a, col_b = st.columns(2)
    with col_a:
        st.plotly_chart(plot_category_bar(filtered_df), use_container_width=True)
    with col_b:
        st.plotly_chart(plot_regional_sales(filtered_df), use_container_width=True)

    # ----- 客户分类 + 配送 -----
    col_c, col_d = st.columns(2)
    with col_c:
        st.plotly_chart(plot_segment_donut(filtered_df), use_container_width=True)
    with col_d:
        st.plotly_chart(plot_ship_mode(filtered_df), use_container_width=True)


# ======================== TAB 2: SALES DEEP DIVE ========================
with tab2:

    st.markdown("### 📈 Year-over-Year Comparison")
    st.plotly_chart(plot_yearly_comparison(filtered_df), use_container_width=True)

    col_e, col_f = st.columns(2)
    with col_e:
        st.plotly_chart(plot_quarterly_heatmap(filtered_df), use_container_width=True)
    with col_f:
        st.plotly_chart(plot_monthly_category_trend(filtered_df), use_container_width=True)

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    st.markdown("### 🏷️ Discount Impact Analysis")
    st.plotly_chart(plot_discount_vs_profit(filtered_df), use_container_width=True)

    # 折扣影响统计
    disc_col1, disc_col2, disc_col3 = st.columns(3)
    discounted = filtered_df[filtered_df["Discount"] > 0]
    non_discounted = filtered_df[filtered_df["Discount"] == 0]

    with disc_col1:
        st.metric(
            "Discounted Orders",
            f"{len(discounted):,}",
            f"{len(discounted)/len(filtered_df)*100:.1f}% of total",
        )
    with disc_col2:
        st.metric(
            "Profit (Discounted)",
            f"${discounted['Profit'].sum():,.0f}",
            delta=None,
        )
    with disc_col3:
        st.metric(
            "Profit (Full Price)",
            f"${non_discounted['Profit'].sum():,.0f}",
            delta=None,
        )

    # ----- 子类别利润分析 -----
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    st.markdown("### 💰 Sub-Category Profitability")
    st.plotly_chart(
        plot_subcategory_profit(filtered_df), use_container_width=True
    )


# ======================== TAB 3: REGIONAL ANALYSIS ========================
with tab3:

    st.markdown("### 🗺️ Geographic Sales Distribution")
    st.plotly_chart(plot_state_map(filtered_df), use_container_width=True)

    col_g, col_h = st.columns(2)
    with col_g:
        st.plotly_chart(plot_top_states(filtered_df, n=10), use_container_width=True)
    with col_h:
        st.plotly_chart(plot_top_cities(filtered_df, n=10), use_container_width=True)

    # 地区详细表格
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    st.markdown("### 📋 Regional Performance Summary")

    region_summary = (
        filtered_df.groupby("Region")
        .agg(
            {
                "Sales": "sum",
                "Profit": "sum",
                "Order ID": "nunique",
                "Customer ID": "nunique",
                "Quantity": "sum",
                "Discount": "mean",
            }
        )
        .round(2)
    )
    region_summary.columns = [
        "Total Sales ($)", "Total Profit ($)", "Orders",
        "Customers", "Qty Sold", "Avg Discount",
    ]
    region_summary["Profit Margin (%)"] = (
        region_summary["Total Profit ($)"]
        / region_summary["Total Sales ($)"]
        * 100
    ).round(1)
    region_summary["Avg Discount"] = (region_summary["Avg Discount"] * 100).round(1)
    region_summary = region_summary.sort_values("Total Sales ($)", ascending=False)

    st.dataframe(
        region_summary.style.format(
            {
                "Total Sales ($)": "${:,.0f}",
                "Total Profit ($)": "${:,.0f}",
                "Orders": "{:,}",
                "Customers": "{:,}",
                "Qty Sold": "{:,}",
                "Avg Discount": "{:.1f}%",
                "Profit Margin (%)": "{:.1f}%",
            }
        ),
        use_container_width=True,
        height=220,
    )


# ======================== TAB 4: PRODUCTS & CUSTOMERS ========================
with tab4:

    col_i, col_j = st.columns(2)
    with col_i:
        n_products = st.slider("Number of top products", 5, 20, 10, key="n_prod")
        st.plotly_chart(
            plot_top_products(filtered_df, n=n_products),
            use_container_width=True,
        )
    with col_j:
        n_customers = st.slider("Number of top customers", 5, 20, 10, key="n_cust")
        st.plotly_chart(
            plot_top_customers(filtered_df, n=n_customers),
            use_container_width=True,
        )

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    st.plotly_chart(
        plot_category_sunburst(filtered_df), use_container_width=True
    )

    # 数据浏览
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    with st.expander("📋 View Raw Data", expanded=False):
        display_cols = [
            "Order Date", "Customer Name", "Segment", "Region",
            "State", "City", "Category", "Sub-Category",
            "Product Name", "Sales", "Quantity", "Discount", "Profit",
        ]
        available_cols = [c for c in display_cols if c in filtered_df.columns]
        st.dataframe(
            filtered_df[available_cols].sort_values("Order Date", ascending=False),
            use_container_width=True,
            height=400,
        )
        st.caption(f"Showing {len(filtered_df):,} records")


# ======================== TAB 5: AI INSIGHTS ========================
with tab5:

    st.markdown("### 🤖 AI-Powered Business Insights")
    st.markdown(
        "Click the button below to generate a comprehensive AI analysis "
        "of your sales data using GPT-4o."
    )

    if not api_key:
        st.warning(
            "⚠️ Please enter your OpenAI API Key in the sidebar to use AI features."
        )
        st.info(
            "💡 Get your API key at [platform.openai.com](https://platform.openai.com/api-keys)"
        )
    else:
        if st.button("🚀 Generate AI Insights", type="primary", use_container_width=True):
            with st.spinner("🧠 AI is analyzing your data... This may take 15-30 seconds."):
                data_summary = get_data_summary(filtered_df)
                insights = generate_insights(data_summary, api_key)

            st.markdown("---")
            st.markdown(insights)

            # 保存到 session state
            st.session_state["last_insights"] = insights

        # 如果之前有生成过，显示上一次的结果
        elif "last_insights" in st.session_state:
            st.markdown("---")
            st.markdown("*📝 Previously generated insights:*")
            st.markdown(st.session_state["last_insights"])


# ======================== TAB 6: FORECAST & ASK AI ========================
with tab6:

    forecast_tab, ask_tab = st.tabs(["🔮 Sales Forecast", "💬 Ask AI"])

    # ---------- 预测子标签 ----------
    with forecast_tab:
        st.markdown("### 🔮 Sales Forecasting")
        st.markdown("Predict future sales using time series analysis.")

        fcol1, fcol2 = st.columns([1, 3])
        with fcol1:
            forecast_periods = st.selectbox(
                "Forecast Period",
                options=[3, 6, 9, 12],
                index=1,
                format_func=lambda x: f"{x} months",
            )

        # 准备时间序列并预测
        ts_data = prepare_time_series(filtered_df)

        if len(ts_data) < 6:
            st.warning("⚠️ Not enough data points for forecasting. Need at least 6 months of data.")
        else:
            with st.spinner("🔄 Fitting forecast model..."):
                forecast_df, fitted_df, model_name, metrics = forecast_sales(
                    ts_data, periods=forecast_periods
                )

            # 预测指标
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Model", model_name.split("(")[0].strip())
            m2.metric("MAPE", f"{metrics['mape']:.1f}%",
                      help="Mean Absolute Percentage Error — lower is better")
            m3.metric(
                f"Forecast Total ({forecast_periods}mo)",
                f"${metrics['forecast_total']:,.0f}",
            )
            m4.metric("Avg Monthly Forecast", f"${metrics['forecast_avg_monthly']:,.0f}")

            # 预测图
            st.plotly_chart(
                plot_forecast(ts_data, forecast_df, fitted_df, model_name),
                use_container_width=True,
            )

            # 预测数据表
            with st.expander("📋 Forecast Data Table"):
                display_fc = forecast_df.copy()
                display_fc["Date"] = display_fc["Date"].dt.strftime("%Y-%m")
                display_fc = display_fc.rename(
                    columns={
                        "Forecast": "Predicted Sales ($)",
                        "Lower": "Lower Bound ($)",
                        "Upper": "Upper Bound ($)",
                    }
                )
                st.dataframe(
                    display_fc.style.format(
                        {
                            "Predicted Sales ($)": "${:,.0f}",
                            "Lower Bound ($)": "${:,.0f}",
                            "Upper Bound ($)": "${:,.0f}",
                        }
                    ),
                    use_container_width=True,
                )

    # ---------- Ask AI 子标签 ----------
    with ask_tab:
        st.markdown("### 💬 Ask AI About Your Data")
        st.markdown("Ask any question about the sales data in natural language.")

        if not api_key:
            st.warning(
                "⚠️ Please enter your OpenAI API Key in the sidebar to use this feature."
            )
        else:
            # 示例问题
            st.markdown("**💡 Try these sample questions:**")
            example_cols = st.columns(3)
            sample_questions = [
                "Which region has the highest profit margin?",
                "What are the top 3 most profitable sub-categories?",
                "How does discount affect profitability?",
                "Which customer segment should we focus on?",
                "What products should we consider discontinuing?",
                "Compare Q4 vs Q1 performance",
            ]
            for i, q in enumerate(sample_questions):
                with example_cols[i % 3]:
                    if st.button(f"📌 {q}", key=f"sample_{i}", use_container_width=True):
                        st.session_state["ai_question"] = q

            st.markdown("---")

            # 问题输入
            user_question = st.text_input(
                "🔍 Your question:",
                value=st.session_state.get("ai_question", ""),
                placeholder="e.g., Which state has the worst profit margin?",
            )

            if user_question:
                with st.spinner("🧠 AI is thinking..."):
                    data_summary = get_data_summary(filtered_df)
                    answer = answer_question(user_question, data_summary, api_key)

                st.markdown("---")
                st.markdown("#### 🤖 AI Answer:")
                st.markdown(answer)

                # 清除预设问题
                if "ai_question" in st.session_state:
                    del st.session_state["ai_question"]


# ================================================================
#                         页脚
# ================================================================

st.markdown("---")
st.markdown(
    """
<div style='text-align:center; color:#555; font-size:12px; padding:10px 0 30px 0;'>
    📊 <strong>AI-Powered Sales Analytics Dashboard</strong> &nbsp;|&nbsp;
    Built with Python · Streamlit · Plotly · OpenAI &nbsp;|&nbsp;
    Data: Superstore Sales Dataset
</div>
""",
    unsafe_allow_html=True,
)