import streamlit as st
import requests
from openai import OpenAI

# Load secrets
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
OPENWEATHER_API_KEY = st.secrets["OPENWEATHER_API_KEY"]

client = OpenAI(api_key=OPENAI_API_KEY)

st.title("🌦️ Lab 5: Weather & Picnic Bot")
st.write("Get weather updates and picnic suggestions powered by GPT and OpenWeather API!")

# --- Input from user ---
location = st.text_input("Enter a city", value="Syracuse")

if st.button("Check Weather"):
    # Normalize user input (replace commas/spaces for API compatibility)
    query_location = location.strip().replace(", ", ",").replace(" ", "+")

    # Call OpenWeather API
    url = f"https://api.openweathermap.org/data/2.5/weather?q={query_location}&appid={OPENWEATHER_API_KEY}&units=metric"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()

        weather_info = {
            "location": location,
            "temperature": data["main"]["temp"],
            "feels_like": data["main"]["feels_like"],
            "temp_min": data["main"]["temp_min"],
            "temp_max": data["main"]["temp_max"],
            "humidity": data["main"]["humidity"],
            "description": data["weather"][0]["description"].capitalize(),
        }

        st.write("### Weather Data")
        st.json(weather_info)

        # --- Ask GPT for picnic suggestion ---
        prompt = f"""
        The weather in {weather_info['location']} is:
        - Temperature: {weather_info['temperature']} °C
        - Feels like: {weather_info['feels_like']} °C
        - Min/Max: {weather_info['temp_min']}–{weather_info['temp_max']} °C
        - Humidity: {weather_info['humidity']}%
        - Condition: {weather_info['description']}

        Please suggest if it's a good day for a picnic.
        Explain in simple words a 10-year-old can understand.
        """

        ai_response = client.chat.completions.create(
            model="gpt-5-chat-latest",  # ✅ Using GPT-5 latest
            messages=[{"role": "user", "content": prompt}],
        )

        suggestion = ai_response.choices[0].message.content  # ✅ fixed access
        st.subheader("🤖 Picnic Suggestion")
        st.write(suggestion)

    else:
        st.error("❌ Could not fetch weather data. Please check the city name or try adding a country code (e.g., 'Paris,FR').")
