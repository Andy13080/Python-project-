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

# Initialize Text-to-Speech
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