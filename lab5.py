import streamlit as st
import requests
from openai import OpenAI

# --- Load secrets ---
try:
    openai_key = st.secrets["OPENAI_API_KEY"]
    weather_key = st.secrets["OPENWEATHER_API_KEY"]
except Exception:
    st.error("⚠️ Missing API keys in .streamlit/secrets.toml")
    st.stop()

client = OpenAI(api_key=openai_key)

# --- Weather Function (Lab 5a) ---
def get_current_weather(location: str, API_key: str):
    """
    Calls OpenWeatherMap API and returns weather info in Celsius.
    """
    if "," in location:
        location = location.split(",")[0].strip()

    urlbase = "https://api.openweathermap.org/data/2.5/"
    urlweather = f"weather?q={location}&appid={API_key}"
    url = urlbase + urlweather

    response = requests.get(url)
    data = response.json()

    if "main" not in data:
        return {"error": f"Could not find weather for {location}"}

    # Convert Kelvin → Celsius
    temp = data['main']['temp'] - 273.15
    feels_like = data['main']['feels_like'] - 273.15
    temp_min = data['main']['temp_min'] - 273.15
    temp_max = data['main']['temp_max'] - 273.15
    humidity = data['main']['humidity']

    return {
        "location": location,
        "temperature": round(temp, 2),
        "feels_like": round(feels_like, 2),
        "temp_min": round(temp_min, 2),
        "temp_max": round(temp_max, 2),
        "humidity": round(humidity, 2),
        "description": data["weather"][0]["description"].capitalize(),
    }

# --- Streamlit UI ---
st.title("🌤️ Lab 5: The What-to-Wear Bot")
st.write("Enter a city to get weather, clothing suggestions, and picnic advice.")

city = st.text_input("Enter city:", placeholder="e.g., Syracuse, NY")

if st.button("Check Weather & Get Suggestions"):
    if not city.strip():
        city = "Syracuse, NY"  # default fallback

    # Get weather info
    weather = get_current_weather(city, weather_key)

    if "error" in weather:
        st.error(weather["error"])
    else:
        st.write(f"### 🌍 Weather in {weather['location']}")
        st.json(weather)

        # Prepare prompt for LLM
        prompt = f"""
        The current weather for {weather['location']} is:
        - Temperature: {weather['temperature']} °C
        - Feels Like: {weather['feels_like']} °C
        - Min: {weather['temp_min']} °C
        - Max: {weather['temp_max']} °C
        - Humidity: {weather['humidity']} %
        - Conditions: {weather['description']}

        Based on this weather:
        1. Suggest what clothes someone should wear today.
        2. Say if it’s a good day for a picnic (yes/no with reasoning).
        Please keep your answer simple enough for a 10-year-old to understand.
        """

        # Call OpenAI for suggestions
        with st.spinner("Thinking..."):
            response = client.chat.completions.create(
                model="gpt-5-chat-latest",   # ✅ updated model
                messages=[{"role": "user", "content": prompt}],
            )
            suggestion = response.choices[0].message["content"]

        st.subheader("👕 Clothing & Picnic Advice")
        st.write(suggestion)
