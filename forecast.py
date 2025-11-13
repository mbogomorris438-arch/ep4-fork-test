# forecast.py
import pandas as pd
from statsmodels.tsa.holtwinters import ExponentialSmoothing
import warnings
warnings.filterwarnings('ignore')

# Load data
df = pd.read_excel("cleaned_sales_medicines_swapped.xlsx")
df['datum'] = pd.to_datetime(df['datum'])
df['Medicine'] = df['Medicine'].str.lower()

# Get all medicines
medicines = df['Medicine'].unique()

# Prepare forecast DataFrame
future_dates = pd.date_range(start=df['datum'].max() + pd.Timedelta(days=1), periods=30, freq='D')
forecast_df = pd.DataFrame({'Date': future_dates})

# Forecast each medicine
for med in medicines:
    data = df[df['Medicine'] == med][['datum', 'Value']].set_index('datum')
    if len(data) < 10:
        forecast_df[med.title()] = 0
        continue
    data_daily = data.resample('D').sum()
    try:
        model = ExponentialSmoothing(data_daily['Value'], trend='add', seasonal='add', seasonal_periods=7)
        fit = model.fit()
        forecast = fit.forecast(30)
        forecast_df[med.title()] = forecast.values
    except:
        forecast_df[med.title()] = 0

# Save
forecast_df.to_csv("30_day_demand_forecast.csv", index=False)
print("Forecast saved: 30_day_demand_forecast.csv")
print("\nSlow-Moving Drugs (avg < 1/day):")
for col in forecast_df.columns:
    if col != 'Date':
        avg = forecast_df[col].mean()
        if avg < 1.0:
            print(f"  • {col}: {avg:.2f} units/day → REDUCE STOCK!")