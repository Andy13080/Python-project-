from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import requests

API_KEY = '3538c7353ea6924c8139a1e8b5aa90a2'
BOT_TOKEN = '7974786854:AAHHjnzJX0J-JWU8Pt4r5H2_3TQFEXGnLlA'

def get_weather(city):
    geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={API_KEY}"
    geo_response = requests.get(geo_url).json()
    if not geo_response:
        return "City not found."

    lat, lon = geo_response[0]["lat"], geo_response[0]["lon"]
    weather_url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&units=metric&appid={API_KEY}"
    weather_response = requests.get(weather_url).json()

    message = f"Weather for {city}:\n"
    shown = set()
    for entry in weather_response["list"]:
        date = entry["dt_txt"].split(" ")[0]
        if date not in shown:
            temp = entry["main"]["temp"]
            desc = entry["weather"][0]["description"]
            message += f"{date}: {round(temp)}°C, {desc}\n"
            shown.add(date)
            if len(shown) == 5:
                break
    return message

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    city = update.message.text.strip()
    result = get_weather(city)
    await update.message.reply_text(result)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome! Send me a city name to get the 5-day forecast.")

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

app.run_polling()
