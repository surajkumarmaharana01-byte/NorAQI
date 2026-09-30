import streamlit as st
import google.generativeai as genai
import requests
import pandas as pd
import base64
from datetime import datetime
from dotenv import load_dotenv
import os

from dotenv import load_dotenv
import streamlit as st
import os

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    st.error("GEMINI_API_KEY not set.")
    st.stop()

AQICN_TOKEN = os.getenv("AQICN_TOKEN", "")
print(GEMINI_API_KEY)
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-3.8-flash")

st.set_page_config(page_title="NorAQI", page_icon="🌫️", layout="wide")

def add_bg(image_file):
    with open(image_file, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()

    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/png;base64,{encoded}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}

        [data-testid="stAppViewContainer"] {{
            background: rgba(0,0,0,0.35);
        }}
        </style>
        """,
        unsafe_allow_html=True
    )
    
add_bg("assets/Hazy River City at Sunset.png")

st.title("🌍 NorAQI")

with st.sidebar:
    st.header("🌫️ NorAQI")
    st.caption("Hyperlocal Air Quality Monitoring")

    st.divider()

    st.markdown("### 📍 Cities")
    st.write("• Kataka")
    st.write("• Bhubaneswar")

    st.divider()

    st.markdown("### ⚙️ Services")
    st.write("✅ Live Weather")
    st.write("✅ Official AQI")
    st.write("✅ AI Advisory")
    st.write("✅ Citizen Reports")

    st.divider()

    st.caption("SIH 2026 Prototype")

st.caption("Hyperlocal air quality reporting & advisory for Bhubaneswar & Kataka")

now = datetime.now()

date = now.strftime("%d %B %Y")
time = now.strftime("%I:%M %p")

left, right = st.columns([1, 1])

with left:
    st.markdown(f"### 📅 {date}")

with right:
    st.markdown(
        f"<h3 style='text-align:right;'>🕒 {time}</h3>",
        unsafe_allow_html=True,
    )

hour = now.hour

greeting = ""
subtitle = ""
message = ""

if 5 <= hour < 8:
    greeting = "🌅 Good Morning"
    subtitle = "सुप्रभात • ଶୁଭ ସକାଳ"
    message = "Start your day with fresh air and positive energy."

elif 8 <= hour < 12:
    greeting = "☀️ Good Day"
    message = "Wishing you a productive and healthy day."

elif 12 <= hour < 17:
    greeting = "🌤️ Good Afternoon"

elif 17 <= hour < 19:
    greeting = "🌇 Good Evening"
    subtitle = "शुभ संध्या • ଶୁଭ ସନ୍ଧ୍ୟା"

elif 19 <= hour < 24:
    greeting = "🌙 Good Night"
    subtitle = "---शुभ रात्रि • ଶୁଭ ରାତ୍ରି---"
    message = "Have you had your dinner?"

else:
    greeting = "🌌 Good Midnight"
    message = "Working late? Remember to take some rest."

st.subheader(greeting)

if subtitle:
    st.caption(subtitle)

city = st.selectbox(
    "📍 Select City",
    ["Kataka", "Bhubaneswar"],
    index=0
)

CITY_QUERY = {
    "Bhubaneswar": "bhubaneswar",
    "Kataka": "cuttack"
}

WEATHER = {
    "Kataka": (20.4625, 85.8830),
    "Bhubaneswar": (20.2961, 85.8245)
}

OSPCB_URL = "https://ospcboard.odisha.gov.in/ambient-air-quality-data/"


@st.cache_data(ttl=21600)
def fetch_live_aqi(city_name):
    try:
        df = pd.read_html(OSPCB_URL)[0]
        df = df[df["City"].str.lower() == city_name.lower()]

        df["Date of Monitoring"] = pd.to_datetime(
            df["Date of Monitoring"],
            dayfirst=True,
            errors="coerce"
        )

        df = df.sort_values(
            "Date of Monitoring",
            ascending=False
        )

        latest = df.iloc[0]

        return {
            "aqi": int(latest["AQI value"]),
            "category": latest["Category"],
            "date": latest["Date of Monitoring"].strftime("%d-%m-%Y")
        }

    except Exception as e:
        pass
        return None


@st.cache_data(ttl=1800)
def fetch_weather(city):
    lat, lon = WEATHER[city]

    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lon}"
        f"&current=temperature_2m,relative_humidity_2m,wind_speed_10m"
    )

    try:
        data = requests.get(url, timeout=5).json()["current"]

        return {
            "temp": data["temperature_2m"],
            "humidity": data["relative_humidity_2m"],
            "wind": data["wind_speed_10m"],
        }

    except Exception as e:
        pass
        return None


DEMO_AQI = {
    "Kataka": 160,
    "Bhubaneswar": 166
}

weather = fetch_weather(city)

if weather:
    c1, c2, c3 = st.columns([1,1,1], gap="medium")

    c1.metric("🌡 Temperature", f"{weather['temp']}°C")
    c2.metric("💧 Humidity", f"{weather['humidity']}%")
    c3.metric("🌬 Wind", f"{weather['wind']} km/h")

AQI_CATEGORIES = [
    (0, 50, "Good", "Air quality is satisfactory, air pollution poses little or no risk.", "None"),
    (51, 100, "Moderate", "Acceptable air quality; may be a moderate concern for unusually sensitive people.", "Active children/adults and people with respiratory disease should limit prolonged outdoor exertion."),
    (101, 150, "Unhealthy for Sensitive Groups", "Sensitive groups may experience health effects; general public less likely affected.", "Active children/adults and people with respiratory disease should limit prolonged outdoor exertion."),
    (151, 200, "Unhealthy", "Everyone may begin to experience health effects; sensitive groups more serious effects.", "Active children/adults and people with respiratory disease should avoid prolonged outdoor exertion; everyone else should limit it."),
    (201, 300, "Very Unhealthy", "Health warnings of emergency conditions; entire population more likely affected.", "Active children/adults and people with respiratory disease should avoid all outdoor exertion; everyone else should limit outdoor exertion."),
    (301, 10000, "Hazardous", "Health alert: everyone may experience more serious health effects.", "Everyone should avoid all outdoor exertion."),
]

def get_aqi_category(aqi):
    for low, high, label, health, caution in AQI_CATEGORIES:
        if low <= aqi <= high:
            return label, health, caution
    return "Unknown", "", ""

if "reports" not in st.session_state:
    st.session_state.reports = []

st.divider()
st.subheader("📝 Report a pollution issue")
report_text = st.text_area(
    "Describe what you're seeing/smelling (mention the area/location)",
    placeholder="e.g. Near Badambadi, Kataka — heavy smoke, smells like burning garbage"
)

if st.button("Submit report", type="primary"):
    if report_text.strip():
        with st.spinner("Analyzing report with Gemini..."):
            prompt = f"""
            Analyze the following citizen pollution report from {city}.

            Report:
            "{report_text}"

            Return ONLY in this exact format:

            📍 Location: <location>

            🔥 Source: <Industrial Emission / Agricultural Burning / Vehicular Emission / Waste Burning / Construction Dust / Unclear>

            ⚠ Severity: <Low / Medium / High>
            """
            
            try:
                response = model.generate_content(prompt)
                analysis_text = getattr(response, "text", None)
                if not analysis_text:
                    analysis_text = "Gemini returned no analysis text (possibly blocked or empty response). Try rephrasing the report."
                st.session_state.reports.append({
                    "city": city,
                    "text": report_text,
                    "analysis": analysis_text
                })
                st.toast("Report submitted and analyzed")
            except Exception as e:
                st.error(f"Gemini API call failed: {e}")
    else:
        st.warning("Please describe what you're seeing first")

st.subheader(f"📋 Recent reports — {city}")
city_reports = [r for r in st.session_state.reports if r["city"] == city]
if city_reports:
    for r in reversed(city_reports):
        with st.container(border=True):
            st.markdown(f"**Report:** {r['text']}")
            st.markdown(r["analysis"])
else:
    st.caption("No reports yet for this city.")

st.subheader(f"🌤️ Today's Air Quality — {city}")

live = fetch_live_aqi(CITY_QUERY[city])

if live:
    st.metric("Official OSPCB AQI", live["aqi"])
    st.caption(f"Latest Available Reading ({live['date']})")
else:
    st.warning("Official OSPCB data unavailable")

st.divider()

aqi_value = DEMO_AQI[city]

category, health_impact, caution = get_aqi_category(aqi_value)

if aqi_value <= 50:
    icon = "🟢"
elif aqi_value <= 100:
    icon = "🟠"
elif aqi_value <= 150:
    icon = "🔴"
elif aqi_value <= 200:
    icon = "🩸"
elif aqi_value <= 300:
    icon = "🟣"
else:
    icon = "⚫"

if aqi_value <= 50:
    color = "#00C853"      # Green

elif aqi_value <= 100:
    color = "#FF9800"      # Orange

elif aqi_value <= 150:
    color = "#F44336"      # Red

elif aqi_value <= 200:
    color = "#8B0000"      # Dark Red / Blood Red

elif aqi_value <= 300:
    color = "#7B1FA2"      # Purple

else:
    color = "#2E004F"      # Very Dark Purple (almost black)

st.markdown(
    f"""
    <div style="
        background: rgba(20,20,20,0.55);
        padding:25px;
        border-radius:20px;
        text-align:center;
        backdrop-filter: blur(8px);
        border:1px solid rgba(255,255,255,0.15);
    ">

    <h2>{icon} Air Quality Index</h2>

    <p style="
        color:#D9D9D9;
        font-size:18px;
        margin-top:-5px;
        margin-bottom:15px;
    ">
    📍 {city}
    </p>

    <h1 style="
        font-size:70px;
        margin:0;
        color:white;
    ">
        {aqi_value}
    </h1>

    <h3 style="color:{color};">
        {category}
    </h3>

    </div>
    """,
    unsafe_allow_html=True,
)



with st.expander("⚠ Health Advisory"):
    st.write(caution)

if st.button("Generate advisory", type="primary"):
    with st.spinner("Generating advisory..."):
        recent_texts = "\n".join([r["text"] for r in city_reports[-3:]]) or "No recent citizen reports."
        advisory_prompt = f"""Current AQI: {aqi_value}
        City: {city}

        Recent Citizen Reports:
        {recent_texts}

        Return ONLY this format:

        🚨 Air Alert:
        (one sentence)

        📍 Hotspot:
        (one location)

        😷 Recommendation:
        • Point 1
        • Point 2"""
        try:
            advisory = model.generate_content(advisory_prompt)
            advisory_text = getattr(advisory, "text", None) or "No advisory text returned."
            with st.container(border=True):
                st.toast("Advisory generated")
                st.markdown(advisory_text)
        except Exception as e:
            st.error(f"Gemini API call failed: {e}")

st.divider()

st.markdown(
    """
    <div style="text-align:center; opacity:0.75; font-size:14px;">
        🌍 <b>NorAQI</b><br>
        Hyperlocal Air Quality Reporting & AI Advisory<br><br>
        Build with AI: Code for Communities - Second Edition
    </div>
    """,
    unsafe_allow_html=True,
)            