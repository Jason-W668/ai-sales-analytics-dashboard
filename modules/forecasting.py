"""
销售预测模块 - 标准化 i18n
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
from modules.i18n import t

_COLORS = {"primary": "#4FC3F7", "secondary": "#81C784", "accent": "#FFB74D", "danger": "#E57373"}


def prepare_time_series(df, freq="M"):
    ts = df.set_index("Order Date").resample(freq)["Sales"].sum().reset_index()
    ts.columns = ["Date", "Sales"]
    return ts


def forecast_sales(ts_data, periods=6):
    n = len(ts_data)
    try:
        from statsmodels.tsa.holtwinters import ExponentialSmoothing
        if n >= 24:
            model = ExponentialSmoothing(ts_data["Sales"].values, trend="add", seasonal="add", seasonal_periods=12).fit(optimized=True)
            model_name = "Holt-Winters (Additive Trend + Seasonal)"
        elif n >= 6:
            model = ExponentialSmoothing(ts_data["Sales"].values, trend="add", seasonal=None).fit(optimized=True)
            model_name = "Holt-Winters (Additive Trend)"
        else:
            raise ValueError("Not enough data")
        forecast_values = model.forecast(periods)
        fitted_values = model.fittedvalues
        residuals = ts_data["Sales"].values - fitted_values
        std_resid = np.std(residuals)
        mape = np.mean(np.abs(residuals / ts_data["Sales"].values) * 100)
        rmse = np.sqrt(np.mean(residuals ** 2))
    except Exception:
        x = np.arange(n)
        coeffs = np.polyfit(x, ts_data["Sales"].values, deg=2)
        poly = np.poly1d(coeffs)
        fitted_values = poly(x)
        forecast_x = np.arange(n, n + periods)
        forecast_values = poly(forecast_x)
        if n >= 12:
            seasonal = ts_data["Sales"].values[-12:]
            seasonal_factor = seasonal - np.mean(seasonal)
            forecast_values = forecast_values + np.tile(seasonal_factor, (periods // 12) + 1)[:periods]
        residuals = ts_data["Sales"].values - fitted_values
        std_resid = np.std(residuals)
        mape = np.mean(np.abs(residuals / ts_data["Sales"].values) * 100)
        rmse = np.sqrt(np.mean(residuals ** 2))
        model_name = "Polynomial Trend + Seasonal (Fallback)"

    forecast_dates = pd.date_range(start=ts_data["Date"].iloc[-1] + pd.DateOffset(months=1), periods=periods, freq="MS")
    forecast_df = pd.DataFrame({"Date": forecast_dates, "Forecast": forecast_values,
                                "Lower": forecast_values - 1.96 * std_resid, "Upper": forecast_values + 1.96 * std_resid})
    forecast_df["Lower"] = forecast_df["Lower"].clip(lower=0)
    fitted_df = pd.DataFrame({"Date": ts_data["Date"], "Fitted": fitted_values})
    metrics = {"mape": round(mape, 2), "rmse": round(rmse, 2),
               "forecast_total": round(forecast_df["Forecast"].sum(), 2),
               "forecast_avg_monthly": round(forecast_df["Forecast"].mean(), 2)}
    return forecast_df, fitted_df, model_name, metrics


def plot_forecast(ts_data, forecast_df, fitted_df, model_name):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=ts_data["Date"], y=ts_data["Sales"], name=t("charts.legend.historical"),
                             mode="lines+markers", line=dict(color=_COLORS["primary"], width=2), marker=dict(size=4)))
    fig.add_trace(go.Scatter(x=fitted_df["Date"], y=fitted_df["Fitted"], name=t("charts.legend.fitted"),
                             mode="lines", line=dict(color=_COLORS["accent"], width=1.5, dash="dot"), opacity=0.7))
    fig.add_trace(go.Scatter(x=forecast_df["Date"], y=forecast_df["Forecast"], name=t("charts.legend.forecast"),
                             mode="lines+markers", line=dict(color=_COLORS["secondary"], width=2.5), marker=dict(size=8, symbol="diamond")))
    fig.add_trace(go.Scatter(
        x=pd.concat([forecast_df["Date"], forecast_df["Date"][::-1]]),
        y=pd.concat([forecast_df["Upper"], forecast_df["Lower"][::-1]]),
        fill="toself", fillcolor="rgba(129,199,132,0.15)", line=dict(color="rgba(0,0,0,0)"),
        name=t("charts.legend.confidence"), showlegend=True))

    boundary_x = ts_data["Date"].iloc[-1].isoformat()
    fig.add_shape(type="line", x0=boundary_x, x1=boundary_x, y0=0, y1=1, yref="paper",
                  line=dict(color="rgba(255,255,255,0.3)", width=1.5, dash="dash"))
    fig.add_annotation(x=boundary_x, y=1.06, yref="paper", text=t("charts.legend.forecast_start"),
                       showarrow=False, font=dict(color="#FAFAFA", size=12))

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#FAFAFA", size=12), margin=dict(l=20, r=20, t=60, b=20),
        title=dict(text=t("charts.forecast", model=model_name), font=dict(size=15, color="#FAFAFA")),
        height=480, xaxis_title=t("charts.axis.date"), yaxis_title=t("charts.axis.sales"),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=11)), hovermode="x unified")
    fig.update_xaxes(gridcolor="rgba(128,128,128,0.1)")
    fig.update_yaxes(gridcolor="rgba(128,128,128,0.1)")
    return fig