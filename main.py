import openmeteo_requests
import pandas as pd
import requests_cache
from retry_requests import retry
import time
import pyttsx3

#speech settings
engine = pyttsx3.init()
rate = engine.getProperty('rate')
engine.setProperty('rate', rate-25)

# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)
# Make sure all required weather variables are listed here
# The order of variables in hourly or daily is important to assign them correctly below
url = "https://api.open-meteo.com/v1/forecast"
params = {
	"latitude": 51.5085,
	"longitude": -0.1257,
	"daily": ["temperature_2m_max", "temperature_2m_min"],
	"hourly": ["temperature_2m", "rain"],
	"models": "ukmo_seamless",
	"current": ["temperature_2m", "apparent_temperature", "rain"],
	"timezone": "GMT",
	"forecast_days": 1,
	"wind_speed_unit": "mph"
}
responses = openmeteo.weather_api(url, params=params)
# Process first location. Add a for-loop for multiple locations or weather models
response = responses[0]
#print(f"Coordinates {response.Latitude()}°N {response.Longitude()}°E")
#print(f"Elevation {response.Elevation()} m asl")
#print(f"Timezone {response.Timezone()}{response.TimezoneAbbreviation()}")
#print(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s")

# Current values. The order of variables needs to be the same as requested.
current = response.Current()
current_temperature_2m = current.Variables(0).Value()
current_apparent_temperature = current.Variables(1).Value()
current_rain = current.Variables(2).Value()

#print(f"Current time {current.Time()}")
#print(f"Current temperature_2m {current_temperature_2m}")
#print(f"Current apparent_temperature {current_apparent_temperature}")
#print(f"Current rain {current_rain}")

# Process hourly data. The order of variables needs to be the same as requested.
hourly = response.Hourly()
hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
hourly_rain = hourly.Variables(1).ValuesAsNumpy()

hourly_data = {"date": pd.date_range(
	start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
	end = pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
	freq = pd.Timedelta(seconds = hourly.Interval()),
	inclusive = "left"
)}

hourly_data["temperature_2m"] = hourly_temperature_2m
hourly_data["rain"] = hourly_rain

hourly_dataframe = pd.DataFrame(data = hourly_data)
#print(hourly_dataframe)

# Process daily data. The order of variables needs to be the same as requested.
daily = response.Daily()
daily_temperature_2m_max = daily.Variables(0).ValuesAsNumpy()
daily_temperature_2m_min = daily.Variables(1).ValuesAsNumpy()

daily_data = {"date": pd.date_range(
	start = pd.to_datetime(daily.Time(), unit = "s", utc = True),
	end = pd.to_datetime(daily.TimeEnd(), unit = "s", utc = True),
	freq = pd.Timedelta(seconds = daily.Interval()),
	inclusive = "left"
)}

daily_data["temperature_2m_max"] = daily_temperature_2m_max
daily_data["temperature_2m_min"] = daily_temperature_2m_min

daily_dataframe = pd.DataFrame(data = daily_data)
#print(f"Current temperature_2m {current_temperature_2m}")

#temp and time variables
current_time = int(time.strftime("%H%M"))
current_temp = round(current_temperature_2m, 2)
#speech variables and sayings
time_now = f"the time is {time.strftime("%H:%M")}"
current_temp_final = f"current apparent temperature in London is {current_temp} degrees		"
rain = f"current rain is {current_rain}		"
bless_up = "bless up yourself and have a good day"
reload = "reload this one my selector"

#while True:
if current_time > 800:
		engine.say(f"Good morning Nick, {time_now}, {current_temp_final}, {rain}, {bless_up}")
		engine.runAndWait()

elif current_time > 1200:
		engine.say(f"Good afternoon Nick, {time_now}, {current_temp_final}, {rain}, {reload}")
		engine.runAndWait()

elif current_time > 1800:
		engine.say(f"Good evening Nick, {time_now}, {current_temp_final}, {rain}")
		engine.runAndWait()

elif current_time > 2000:
	engine.say()
	engine.runAndWait()
