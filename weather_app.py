import sys
import requests
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel,
                             QLineEdit, QPushButton, QListWidget, QHBoxLayout, QMessageBox)
from PyQt5.QtGui import QFont
import pyttsx3
import speech_recognition as sr
from collections import defaultdict
import datetime

API_KEY = '3538c7353ea6924c8139a1e8b5aa90a2'

engine = pyttsx3.init()

def speak(text):
    engine.say(text)
    engine.runAndWait()

def get_city_options(city_name):
    url = f"http://api.openweathermap.org/geo/1.0/direct?q={city_name}&limit=5&appid={API_KEY}"
    response = requests.get(url)
    return response.json()

def get_weather(lat, lon):
    url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&units=metric&appid={API_KEY}"
    response = requests.get(url)
    return response.json()

def group_forecast_by_day(forecast_data):
    daily_forecast = defaultdict(list)
    for entry in forecast_data['list']:
        date = entry['dt_txt'].split()[0]
        daily_forecast[date].append(entry)

    forecast_summary = []
    for i, (date, entries) in enumerate(daily_forecast.items()):
        if i >= 5:
            break
        temp = sum([e['main']['temp'] for e in entries]) / len(entries)
        condition = entries[0]['weather'][0]['description']
        forecast_summary.append((date, round(temp), condition))
    return forecast_summary

class WeatherApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Weather App")
        self.setGeometry(100, 100, 350, 500)
        layout = QVBoxLayout()

        title = QLabel("Weather")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setStyleSheet("color: white; background-color: red; padding: 6px; border-radius: 5px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        self.city_input = QLineEdit()
        self.city_input.setPlaceholderText("Enter city name")
        layout.addWidget(self.city_input)

        button_layout = QHBoxLayout()
        self.search_btn = QPushButton("Search")
        self.search_btn.clicked.connect(self.search_city)
        button_layout.addWidget(self.search_btn)

        self.voice_btn = QPushButton("🎤 Activate Voice")
        self.voice_btn.clicked.connect(self.enable_voice_mode)
        button_layout.addWidget(self.voice_btn)

        layout.addLayout(button_layout)

        self.city_list = QListWidget()
        self.city_list.itemClicked.connect(self.city_selected)
        layout.addWidget(self.city_list)

        self.result_label = QLabel("Weather Info Will Appear Here")
        self.result_label.setWordWrap(True)
        layout.addWidget(self.result_label)

        self.setLayout(layout)
        self.voice_mode = False

    def enable_voice_mode(self):
        self.voice_mode = True
        self.listen_for_command()

    def listen_for_command(self):
        if not self.voice_mode:
            return
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            self.result_label.setText("Listening for command like 'weather in Lusaka'...")
            audio = recognizer.listen(source)
        try:
            command = recognizer.recognize_google(audio)
            if "weather in" in command.lower():
                city_name = command.lower().split("weather in")[-1].strip()
                self.city_input.setText(city_name)
                self.search_city()
            else:
                self.result_label.setText("Please say 'weather in <city>'")
        except:
            self.result_label.setText("Voice not recognized")

    def search_city(self):
        city_name = self.city_input.text()
        if not city_name:
            QMessageBox.warning(self, "Input Error", "Please enter a city name.")
            return
        options = get_city_options(city_name)
        if not options:
            QMessageBox.critical(self, "City Not Found", "No city found with that name.")
            return
        self.city_list.clear()
        self.city_data = options
        for city in options:
            display = f"{city['name']}, {city.get('state', '')}, {city['country']}"
            self.city_list.addItem(display)

    def city_selected(self, item):
        index = self.city_list.currentRow()
        city = self.city_data[index]
        lat = city['lat']
        lon = city['lon']
        weather_data = get_weather(lat, lon)
        forecast = group_forecast_by_day(weather_data)

        output = f"Weather for {city['name']}, {city['country']}\n"
        for day in forecast:
            output += f"{day[0]}: {day[1]}°C, {day[2]}\n"
        self.result_label.setText(output)
        speak(output)

if __name__ == '__main__':
    from PyQt5.QtCore import Qt
    app = QApplication(sys.argv)
    window = WeatherApp()
    window.show()
    sys.exit(app.exec_())
