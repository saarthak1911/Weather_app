import streamlit as st
import requests
from langchain.chat_models import init_chat_model
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# App Title
st.set_page_config(page_title="Weather Explainer: ")
st.title("Weather App")

llm = init_chat_model(
    model = "llama-3.3-70b-versatile",
    model_provider = "openai",
    base_url = "https://api.groq.com/openai/v1",
    api_key = os.getenv("GROQ_API_KEY")
)
conversation = [
    {"role": "system", "content": "You are weather forcast expert with 10 years of experience."}
]


city = st.text_input("Enter city")
if city:
    api_key = os.getenv("OPENWEATHER_API_KEY")

    if not api_key:
        st.error("API key not found. Please set OPENWEATHER_API_KEY.")
      

    url = (
        f"https://api.openweathermap.org/data/2.5/weather"
        f"?q={city}&appid={api_key}&units=metric"
    )

    response = requests.get(url)
    data = response.json()

    if response.status_code != 200:
        st.error(data.get("message", "Failed to fetch weather"))
        

    st.subheader(f"Weather in {city.title()}")
    temp = data["main"]["temp"]
    humidity = data["main"]["humidity"]
    wind_speed = data["wind"]["speed"]
    st.metric("Temperature (°C)",temp)
    st.metric("Humidity (%)",humidity)
    st.metric("Wind Speed (m/s)",wind_speed)

    llm_input = f"""
            
            Question: {temp} {humidity} {wind_speed}
            Instruction:
                Explain the weather conditions based on the given temperature, humidity, and wind speed.
                
                explain the weather in 2-4 sentences without more explaination.
        """
    #print sql query on user input
    result = llm.invoke(llm_input)
    st.write("Weather forecast:")
    st.write(result.content)
        