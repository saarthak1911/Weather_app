import streamlit as st
import requests
from langchain_community.chat_models import init_chat_model


# ---------------------------
# PAGE CONFIG & CUSTOM STYLE
# ---------------------------
st.set_page_config(page_title="🌦️ AI Weather Assistant", layout="wide")

st.markdown("""
    <style>
        body {
            background-color: #f3f6ff;
        }
        .title {
            font-size: 40px;
            font-weight: 700;
            text-align: center;
            color: #2d4dff;
        }
        .subtitle {
            text-align: center;
            font-size: 18px;
            color: #444;
        }
       
        .metric-title {
            font-size: 20px;
            color: #ff5722;
        }
        .metric-value {
            font-size: 30px;
            font-weight: bold;
            color: #2d4dff;
        }
    </style>
""", unsafe_allow_html=True)

# ---------------------------
# HEADER
# ---------------------------
st.markdown("<div class='title'>🌤️ AI Weather Assistant</div>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Get real-time weather + AI-generated explanations</p>", unsafe_allow_html=True)

# ---------------------------
# LOAD API KEYS
# ---------------------------
groq_api_key = st.secrets.get("GROQ_API_KEY")
openweather_api_key = st.secrets.get("OPENWEATHER_API_KEY")

if not groq_api_key:
    st.error("❌ Missing GROQ_API_KEY in secrets.toml")
if not openweather_api_key:
    st.error("❌ Missing OPENWEATHER_API_KEY in secrets.toml")

# ---------------------------
# LLM MODEL
# ---------------------------
llm = init_chat_model(
    model="llama-3.3-70b-versatile",
    model_provider="openai",
    base_url="https://api.groq.com/openai/v1",
    api_key=groq_api_key
)

# ---------------------------
# INPUT SECTION
# ---------------------------
st.write("### 🔍 Enter a city to check the weather")
city = st.text_input("City Name", placeholder="e.g., Mumbai")

# ---------------------------
# FETCH WEATHER
# ---------------------------
if city:
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={openweather_api_key}&units=metric"
    response = requests.get(url)
    data = response.json()

    if response.status_code != 200:
        st.error("❌ " + data.get("message", "Failed to fetch weather"))
    else:
        temp = data["main"]["temp"]
        humidity = data["main"]["humidity"]
        wind_speed = data["wind"]["speed"]
        weather_type = data["weather"][0]["main"]

        # ---------------------------
        # WEATHER ICON MAP
        # ---------------------------
        icons = {
            "Clear": "☀️",
            "Clouds": "☁️",
            "Rain": "🌧️",
            "Thunderstorm": "⛈️",
            "Snow": "❄️",
            "Mist": "🌫️"
        }
        icon = icons.get(weather_type, "🌍")

        st.markdown(f"## {icon} Weather in **{city.title()}**")

        # ---------------------------
        # METRIC CARDS (3 columns)
        # ---------------------------
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("<div class='metric-title'>Temperature</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='metric-value'>{temp}°C</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with col2:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("<div class='metric-title'>Humidity</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='metric-value'>{humidity}%</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with col3:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("<div class='metric-title'>Wind Speed</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='metric-value'>{wind_speed} m/s</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        # ---------------------------
        # LLM EXPLANATION
        # ---------------------------
        with st.spinner("🤖 AI analyzing weather conditions..."):
            llm_input = f"""
            Weather details:
            - Temperature: {temp}°C
            - Humidity: {humidity}%
            - Wind Speed: {wind_speed} m/s

            Write a friendly weather explanation in 2–4 sentences.
            """

            result = llm.invoke(llm_input)

        st.write("## 🤖 AI Weather Summary")
        st.success(result.content)

        # ---------------------------
        # EXTRA: MOTIVATION / TIPS BASED ON WEATHER
        # ---------------------------
        st.write("---")
        st.write("### 🌈 Tips for Today's Weather:")

        if temp > 30:
            st.info("🔥 It's quite hot! Stay hydrated and avoid the sun during peak hours.")
        elif temp < 15:
            st.info("🧥 It's cold! Wear warm clothes if you're going out.")
        else:
            st.info("😊 The temperature is pleasant, enjoy your day!")

        if humidity > 80:
            st.warning("💧 High humidity can make it feel warmer than it is.")
        if wind_speed > 10:
            st.warning("🌬️ Strong winds — secure loose items outdoors.")

