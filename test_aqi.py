import pandas as pd

URL = "https://ospcboard.odisha.gov.in/ambient-air-quality-data/"

def get_aqi(city):
    df = pd.read_html(URL)[0]

    df = df[df["City"].str.lower() == city.lower()]

    df["Date of Monitoring"] = pd.to_datetime(
        df["Date of Monitoring"],
        dayfirst=True,
        errors="coerce"
    )

    df = df.sort_values("Date of Monitoring", ascending=False)

    latest = df.iloc[0]

    return {
        "aqi": latest["AQI value"],
        "category": latest["Category"],
        "date": latest["Date of Monitoring"].strftime("%d-%m-%Y")
    }