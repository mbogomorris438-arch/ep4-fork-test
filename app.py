# app.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os

# Page setup
st.set_page_config(page_title="AfyaPlus Dashboard", page_icon="pill", layout="wide")
st.title("AfyaPlus Pharmacy – Demand Forecasting")
st.markdown("**Kericho, Kenya** | Prevent expiry with data")

# Load data
@st.cache_data
def load_sales():
    df = pd.read_excel("cleaned_sales_medicines_swapped.xlsx")
    df['datum'] = pd.to_datetime(df['datum'])
    df['Medicine'] = df['Medicine'].str.lower()
    return df

@st.cache_data
def load_forecast():
    if os.path.exists("30_day_demand_forecast.csv"):
        df = pd.read_csv("30_day_demand_forecast.csv")
        df['Date'] = pd.to_datetime(df['Date'])
        return df
    return None

df = load_sales()
forecast_df = load_forecast()

# Sidebar
st.sidebar.header("Filters")
all_meds = ['All'] + sorted(df['Medicine'].unique().tolist())
selected_med = st.sidebar.selectbox("Select Medicine", all_meds)

min_date = df['datum'].min().date()
max_date = df['datum'].max().date()
date_range = st.sidebar.date_input("Date Range", [min_date, max_date], min_value=min_date, max_value=max_date)
start_date, end_date = date_range

# Filter data
mask = (df['datum'].dt.date >= start_date) & (df['datum'].dt.date <= end_date)
filtered = df[mask].copy()
if selected_med != 'All':
    filtered = filtered[filtered['Medicine'] == selected_med]

# Metrics
col1, col2, col3 = st.columns(3)
total = filtered['Value'].sum()
days = (end_date - start_date).days + 1
avg_daily = total / days if days > 0 else 0

col1.metric("Total Sales", f"{total:,.0f}")
col2.metric("Avg Daily Sales", f"{avg_daily:.1f}")
col3.metric("Days Selected", days)

# Chart
st.subheader("Sales Trend & 30-Day Forecast")
fig, ax = plt.subplots(figsize=(12, 5))
hist = filtered.groupby('datum')['Value'].sum()
ax.plot(hist.index, hist.values, label='Historical', color='steelblue', marker='o')

if forecast_df is not None and selected_med != 'All':
    col = selected_med.title()
    if col in forecast_df.columns:
        f_dates = forecast_df['Date']
        f_vals = forecast_df[col]
        ax.plot(f_dates, f_vals, label='Forecast (30 days)', color='red', linestyle='--')
        ax.axvline(hist.index[-1], color='gray', linestyle=':', label='Today')
ax.set_xlabel("Date")
ax.set_ylabel("Sales")
ax.legend()
ax.grid(True, alpha=0.3)
plt.xticks(rotation=45)
st.pyplot(fig)

# Top 5
st.subheader("Top 5 Best Sellers")
top5 = filtered.groupby('Medicine')['Value'].sum().nlargest(5)
fig2, ax2 = plt.subplots()
top5.plot(kind='barh', ax=ax2, color='lightgreen')
ax2.set_xlabel("Total Sales")
st.pyplot(fig2)

# Slow Movers
st.subheader("Expiry Risk Alert")
if forecast_df is not None:
    slow = [(c, forecast_df[c].mean()) for c in forecast_df.columns if c != 'Date' and forecast_df[c].mean() < 1.0]
    if slow:
        st.error("**Reduce Stock Immediately:**")
        for name, avg in slow:
            st.write(f"• **{name}**: {avg:.2f} units/day → Risk of expiry!")
    else:
        st.success("No slow-moving drugs!")
else:
    st.info("Forecast not available.")

# Download
if forecast_df is not None:
    csv = forecast_df.to_csv(index=False).encode()
    st.download_button(
        "Download 30-Day Forecast",
        csv,
        "afyaplus_30day_forecast.csv",
        "text/csv"
    )

st.markdown("---")
st.caption("Built with Python • Streamlit | © 2025")