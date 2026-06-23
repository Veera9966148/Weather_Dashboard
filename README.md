# 🌦️ Weather Dashboard Pro

A production-ready weather dashboard built using Flask and OpenWeather API.

## Features
- Real-Time Weather Search
- 5 Forecast Updates
- Search History
- Dark Mode
- Responsive UI
- Error Handling
- OpenWeather API Integration

## Tech Stack
- Python
- Flask
- REST API
- SQLite
- HTML5
- CSS3
- JavaScript
- OpenWeather API

## Installation

git clone https://github.com/your-username/weather-dashboard-pro.git

cd weather-dashboard-pro

pip install -r requirements.txt

python app.py

## Environment Variables

Create .env file:

API_KEY=your_openweather_api_key

## Deployment

Deploy on Render using:

Build Command:
pip install -r requirements.txt

Start Command:
gunicorn app:app
