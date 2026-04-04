"""
📊 AI-Powered Sales Analytics Dashboard
标准化 i18n - JSON 语言包
"""

import streamlit as st
import pandas as pd

from modules.data_loader import load_data, get_filtered_data, get_data_summary
from modules.visualizations import (
    calc_kpi_metrics, plot_sales_trend, plot_regional_sales, plot_category_bar,
    plot_category_sunburst, plot_subcategory_profit, plot_segment_donut,
    plot_top_products, plot_top_customers, plot_state_map, plot_top_states,
    plot_top_cities, plot_discount_vs_profit, plot_ship_mode,
    plot_yearly_comparison, plot_quarterly_heatmap, plot_monthly_category_trend,
)
from modules.ai_insights import generate_insights, answer_question
from modules.forecasting import prepare_time_series, forecast_sales, plot_forecast
from modules.config_manager import render_ai_sidebar, get_active_config
from modules.i18n import t, render_language_selector

# ================================================================
st.set_page_config(page_title="AI Sales Analytics", page_icon="📊", layout="wide", initial_sidebar_state="expanded")

# ================================================================
st.markdown("""
<style>
    .kpi-card{background:linear-gradient(135deg,#1a1f36 0%,#252b48 100%);border-radius:14px;padding:22px 16px;text-align:center;border:1px solid rgba(79,195,247,0.15);box-shadow:0 4px 20px rgba(0,0,0,0.4);transition:transform .2s,box-shadow .2s}
    .kpi-card:hover{transform:translateY(-2px);box-shadow:0 6px 25px rgba(79,195,247,0.15)}
    .kpi-value{font-size:26px;font-weight:700;color:#4FC3F7;margin:6px 0 2px 0;line-height:1.2}
    .kpi-value.green{color:#81C784}.kpi-value.orange{color:#FFB74D}.kpi-value.purple{color:#BA68C8}
    .kpi-label{font-size:11px;color:#9e9e9e;text-transform:uppercase;letter-spacing:1.2px;font-weight:500}
    .main-header{font-size:38px;font-weight:800;background:linear-gradient(120deg,#4FC3F7 0%,#81C784 50%,#FFB74D 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent;text-align:center;margin-bottom:0;padding-top:10px}
    .sub-header{font-size:15px;color:#888;text-align:center;margin-bottom:25px}
    .section-divider{border:none;border-top:1px solid rgba(79,195,247,0.12);margin:25px 0}
    .info-bar{background:rgba(79,195,247,0.08);border-left:3px solid #4FC3F7;padding:10px 16px;border-radius:0 8px 8px 0;margin-bottom:20px;font-size:13px;color:#ccc}
    .stTabs [data-baseweb="tab-list"]{gap:4px}.stTabs [data-baseweb="tab"]{border-radius:8px 8px 0 0;padding:10px 20px;font-size:14px}
    section[data-testid="stSidebar"]>div{padding-top:1rem}
</style>""", unsafe_allow_html=True)

# ================================================================
df = load_data()

# ================================================================
with st.sidebar:
    st.markdown(f"# {t('sidebar.control_panel')}")
    st.markdown("---")
    render_language_selector()
    st.markdown("---")

    st.markdown(f"### {t('sidebar.date_range')}")
    min_date, max_date = df["Order Date"].min().date(), df["Order Date"].max().date()
    date_range = st.date_input("Date", value=(min_date, max_date), min_value=min_date, max_value=max_date, label_visibility="collapsed")

    st.markdown(f"### {t('sidebar.region')}")
    regions = st.multiselect("Region", sorted(df["Region"].unique()), default=[], label_visibility="collapsed")

    st.markdown(f"### {t('sidebar.category')}")
    categories = st.multiselect("Category", sorted(df["Category"].unique()), default=[], label_visibility="collapsed")

    st.markdown(f"### {t('sidebar.segment')}")
    segments = st.multiselect("Segment", sorted(df["Segment"].unique()), default=[], label_visibility="collapsed")

    st.markdown("---")
    ai_config = render_ai_sidebar()
    st.markdown("---")
    st.markdown(f"""<div style='text-align:center;color:#555;font-size:11px;line-height:1.6;'>
        📊 AI Sales Analytics<br>OpenAI 🤖 & SiliconFlow 🌊<br>
        <span style='color:#4FC3F7;'>{t('app.version')}</span></div>""", unsafe_allow_html=True)

# ================================================================
filtered_df = get_filtered_data(
    df,
    date_range=date_range if isinstance(date_range, tuple) and len(date_range) == 2 else None,
    regions=regions or None, categories=categories or None, segments=segments or None,
)
if len(filtered_df) == 0:
    st.warning(t("errors.no_data_warning"))
    st.stop()

# ================================================================
st.markdown(f'<div class="main-header">{t("app.title")}</div>', unsafe_allow_html=True)
st.markdown(f'<div class="sub-header">{t("app.subtitle")}</div>', unsafe_allow_html=True)
st.markdown(f"""<div class="info-bar">
    📋 <strong>{len(filtered_df):,}</strong> {t('info_bar.records')} &nbsp;|&nbsp;
    🛒 <strong>{filtered_df['Order ID'].nunique():,}</strong> {t('info_bar.orders')} &nbsp;|&nbsp;
    👤 <strong>{filtered_df['Customer ID'].nunique():,}</strong> {t('info_bar.customers')} &nbsp;|&nbsp;
    📅 {filtered_df['Order Date'].min().strftime('%Y-%m-%d')} — {filtered_df['Order Date'].max().strftime('%Y-%m-%d')}
    </div>""", unsafe_allow_html=True)

# ================================================================
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    t("tabs.overview"), t("tabs.deep_dive"), t("tabs.regional"),
    t("tabs.products"), t("tabs.ai_insights"), t("tabs.forecast"),
])

# ======================== TAB 1 ========================
with tab1:
    kpis = calc_kpi_metrics(filtered_df)
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown(f'<div class="kpi-card"><div class="kpi-label">{t("kpi.total_revenue")}</div><div class="kpi-value">${kpis["total_sales"]:,.0f}</div></div>', unsafe_allow_html=True)
    with c2: st.markdown(f'<div class="kpi-card"><div class="kpi-label">{t("kpi.total_profit")}</div><div class="kpi-value green">${kpis["total_profit"]:,.0f}</div></div>', unsafe_allow_html=True)
    with c3: st.markdown(f'<div class="kpi-card"><div class="kpi-label">{t("kpi.total_orders")}</div><div class="kpi-value orange">{kpis["total_orders"]:,}</div></div>', unsafe_allow_html=True)
    with c4: st.markdown(f'<div class="kpi-card"><div class="kpi-label">{t("kpi.profit_margin")}</div><div class="kpi-value purple">{kpis["profit_margin"]:.1f}%</div></div>', unsafe_allow_html=True)
    st.markdown("")
    c5, c6, c7, c8 = st.columns(4)
    with c5: st.markdown(f'<div class="kpi-card"><div class="kpi-label">{t("kpi.avg_order_value")}</div><div class="kpi-value">${kpis["avg_order_value"]:,.0f}</div></div>', unsafe_allow_html=True)
    with c6: st.markdown(f'<div class="kpi-card"><div class="kpi-label">{t("kpi.customers")}</div><div class="kpi-value green">{kpis["total_customers"]:,}</div></div>', unsafe_allow_html=True)
    with c7: st.markdown(f'<div class="kpi-card"><div class="kpi-label">{t("kpi.avg_discount")}</div><div class="kpi-value orange">{kpis["avg_discount"]:.1f}%</div></div>', unsafe_allow_html=True)
    with c8: st.markdown(f'<div class="kpi-card"><div class="kpi-label">{t("kpi.items_sold")}</div><div class="kpi-value purple">{kpis["total_quantity"]:,}</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    st.plotly_chart(plot_sales_trend(filtered_df), use_container_width=True)
    col_a, col_b = st.columns(2)
    with col_a: st.plotly_chart(plot_category_bar(filtered_df), use_container_width=True)
    with col_b: st.plotly_chart(plot_regional_sales(filtered_df), use_container_width=True)
    col_c, col_d = st.columns(2)
    with col_c: st.plotly_chart(plot_segment_donut(filtered_df), use_container_width=True)
    with col_d: st.plotly_chart(plot_ship_mode(filtered_df), use_container_width=True)

# ======================== TAB 2 ========================
with tab2:
    st.markdown(t("deep_dive.yoy_comparison"))
    st.plotly_chart(plot_yearly_comparison(filtered_df), use_container_width=True)
    col_e, col_f = st.columns(2)
    with col_e: st.plotly_chart(plot_quarterly_heatmap(filtered_df), use_container_width=True)
    with col_f: st.plotly_chart(plot_monthly_category_trend(filtered_df), use_container_width=True)
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    st.markdown(t("deep_dive.discount_impact"))
    st.plotly_chart(plot_discount_vs_profit(filtered_df), use_container_width=True)
    dc1, dc2, dc3 = st.columns(3)
    disc = filtered_df[filtered_df["Discount"] > 0]
    nodisc = filtered_df[filtered_df["Discount"] == 0]
    with dc1: st.metric(t("deep_dive.discounted_orders"), f"{len(disc):,}", f"{len(disc)/len(filtered_df)*100:.1f}% {t('deep_dive.of_total')}")
    with dc2: st.metric(t("deep_dive.profit_discounted"), f"${disc['Profit'].sum():,.0f}")
    with dc3: st.metric(t("deep_dive.profit_full_price"), f"${nodisc['Profit'].sum():,.0f}")
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    st.markdown(t("deep_dive.subcategory_profitability"))
    st.plotly_chart(plot_subcategory_profit(filtered_df), use_container_width=True)

# ======================== TAB 3 ========================
with tab3:
    st.markdown(t("regional.geo_distribution"))
    st.plotly_chart(plot_state_map(filtered_df), use_container_width=True)
    col_g, col_h = st.columns(2)
    with col_g: st.plotly_chart(plot_top_states(filtered_df, n=10), use_container_width=True)
    with col_h: st.plotly_chart(plot_top_cities(filtered_df, n=10), use_container_width=True)
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    st.markdown(t("regional.summary_title"))
    rs = filtered_df.groupby("Region").agg({"Sales": "sum", "Profit": "sum", "Order ID": "nunique", "Customer ID": "nunique", "Quantity": "sum", "Discount": "mean"}).round(2)
    rs.columns = [t("regional.columns.total_sales"), t("regional.columns.total_profit"), t("regional.columns.orders"), t("regional.columns.customers"), t("regional.columns.qty"), t("regional.columns.avg_discount")]
    pm_col = t("regional.columns.profit_margin")
    rs[pm_col] = (rs[t("regional.columns.total_profit")] / rs[t("regional.columns.total_sales")] * 100).round(1)
    rs[t("regional.columns.avg_discount")] = (rs[t("regional.columns.avg_discount")] * 100).round(1)
    rs = rs.sort_values(t("regional.columns.total_sales"), ascending=False)
    st.dataframe(rs.style.format({
        t("regional.columns.total_sales"): "${:,.0f}", t("regional.columns.total_profit"): "${:,.0f}",
        t("regional.columns.orders"): "{:,}", t("regional.columns.customers"): "{:,}",
        t("regional.columns.qty"): "{:,}", t("regional.columns.avg_discount"): "{:.1f}%", pm_col: "{:.1f}%",
    }), use_container_width=True, height=220)

# ======================== TAB 4 ========================
with tab4:
    col_i, col_j = st.columns(2)
    with col_i:
        np_ = st.slider(t("products.top_products_slider"), 5, 20, 10, key="n_prod")
        st.plotly_chart(plot_top_products(filtered_df, n=np_), use_container_width=True)
    with col_j:
        nc_ = st.slider(t("products.top_customers_slider"), 5, 20, 10, key="n_cust")
        st.plotly_chart(plot_top_customers(filtered_df, n=nc_), use_container_width=True)
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    st.plotly_chart(plot_category_sunburst(filtered_df), use_container_width=True)
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    with st.expander(t("products.view_raw_data"), expanded=False):
        dcols = ["Order Date", "Customer Name", "Segment", "Region", "State", "City", "Category", "Sub-Category", "Product Name", "Sales", "Quantity", "Discount", "Profit"]
        acols = [c for c in dcols if c in filtered_df.columns]
        st.dataframe(filtered_df[acols].sort_values("Order Date", ascending=False), use_container_width=True, height=400)
        st.caption(t("products.showing_records", n=f"{len(filtered_df):,}"))

# ======================== TAB 5 ========================
with tab5:
    st.markdown(t("ai_insights.title"))
    if ai_config and ai_config.is_configured:
        st.markdown(f"""<div style="background:rgba(79,195,247,0.06);border-radius:8px;padding:12px 16px;margin-bottom:16px;border:1px solid rgba(79,195,247,0.15);">
            <span style="color:#aaa;font-size:13px;">🔗 Provider: <strong style="color:#4FC3F7">{ai_config.display_name}</strong>
            &nbsp;|&nbsp; 🧠 {t('sidebar.ai.model')}: <strong style="color:#81C784">{ai_config.model}</strong></span></div>""", unsafe_allow_html=True)
        st.markdown(t("ai_insights.description"))
        if st.button(t("ai_insights.generate_btn"), type="primary", use_container_width=True):
            with st.spinner(t("ai_insights.analyzing")):
                insights = generate_insights(get_data_summary(filtered_df), ai_config.api_key, ai_config.base_url, ai_config.model)
            st.markdown("---")
            st.markdown(insights)
            st.session_state["last_insights"] = insights
        elif "last_insights" in st.session_state:
            st.markdown("---")
            st.markdown(t("ai_insights.previous"))
            st.markdown(st.session_state["last_insights"])
    else:
        st.warning(t("ai_insights.configure_warning"))
        st.markdown(t("ai_insights.how_to_configure"))

# ======================== TAB 6 ========================
with tab6:
    ftab, atab = st.tabs([t("tabs.forecast_sub"), t("tabs.ask_ai_sub")])

    with ftab:
        st.markdown(t("forecast.title"))
        st.markdown(t("forecast.description"))
        fc1, fc2 = st.columns([1, 3])
        with fc1:
            fp = st.selectbox(t("forecast.period"), [3, 6, 9, 12], index=1, format_func=lambda x: t("forecast.months", n=x))
        ts_data = prepare_time_series(filtered_df)
        if len(ts_data) < 6:
            st.warning(t("forecast.not_enough_data"))
        else:
            with st.spinner(t("forecast.fitting_model")):
                fdf, fidf, mn, met = forecast_sales(ts_data, periods=fp)
            m1, m2, m3, m4 = st.columns(4)
            m1.metric(t("forecast.metric_model"), mn.split("(")[0].strip())
            m2.metric("MAPE", f"{met['mape']:.1f}%")
            m3.metric(t("forecast.forecast_total", n=fp), f"${met['forecast_total']:,.0f}")
            m4.metric(t("forecast.avg_monthly"), f"${met['forecast_avg_monthly']:,.0f}")
            st.plotly_chart(plot_forecast(ts_data, fdf, fidf, mn), use_container_width=True)
            with st.expander(t("forecast.table_title")):
                dfc = fdf.copy()
                dfc["Date"] = dfc["Date"].dt.strftime("%Y-%m")
                dfc = dfc.rename(columns={"Forecast": t("forecast.columns.predicted"), "Lower": t("forecast.columns.lower"), "Upper": t("forecast.columns.upper")})
                st.dataframe(dfc.style.format({t("forecast.columns.predicted"): "${:,.0f}", t("forecast.columns.lower"): "${:,.0f}", t("forecast.columns.upper"): "${:,.0f}"}), use_container_width=True)

    with atab:
        st.markdown(t("ask_ai.title"))
        st.markdown(t("ask_ai.description"))
        if not ai_config or not ai_config.is_configured:
            st.warning(t("ask_ai.no_key"))
            st.info(t("ask_ai.supports"))
        else:
            st.caption(f"🔗 {ai_config.display_name} · 🧠 {ai_config.model}")
            st.markdown(t("ask_ai.sample_title"))
            ecols = st.columns(3)
            for i in range(1, 7):
                with ecols[(i - 1) % 3]:
                    q = t(f"ask_ai.samples.q{i}")
                    if st.button(f"📌 {q}", key=f"sample_{i}", use_container_width=True):
                        st.session_state["ai_question"] = q
            st.markdown("---")
            uq = st.text_input(t("ask_ai.your_question"), value=st.session_state.get("ai_question", ""), placeholder=t("ask_ai.placeholder"))
            if uq:
                with st.spinner(t("ask_ai.thinking")):
                    ans = answer_question(uq, get_data_summary(filtered_df), ai_config.api_key, ai_config.base_url, ai_config.model)
                st.markdown("---")
                st.markdown(t("ask_ai.answer"))
                st.markdown(ans)
                if "ai_question" in st.session_state:
                    del st.session_state["ai_question"]

# ================================================================
st.markdown("---")
st.markdown(f"""<div style='text-align:center;color:#555;font-size:12px;padding:10px 0 30px 0;'>
    📊 <strong>AI Sales Analytics Dashboard</strong> &nbsp;|&nbsp; {t('app.footer')}</div>""", unsafe_allow_html=True)