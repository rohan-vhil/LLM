# import openmeteo_requests
# from openmeteo_sdk.Variable import Variable

# om = openmeteo_requests.Client()
# url = "https://api.open-meteo.com/v1/forecast"
# params = {
#     "latitude": 18.73,
#     "longitude": 73.67,
#     "hourly": ["shortwave_radiation", "diffuse_radiation", "direct_normal_irradiance", "global_tilted_irradiance"],
#     "current": "temperature_2m"
# }

# responses = om.weather_api(url, params=params)
# response = responses[0]
# # print(response)
# # print(f"Coordinates {response.Latitude()}°N {response.Longitude()}°E")
# # print(f"Elevation {response.Elevation()} m asl")
# # print(f"Timezone {response.Timezone()} {response.TimezoneAbbreviation()}")
# # print(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s")

# # Current values
# current = response.Current()
# current_temperature_2m = current.Variables(0).Value()

# hourly = response.Hourly()
# hourly_shortwave_radiation = hourly.Variables(0).ValuesAsNumpy()
# hourly_diffuse_radiation = hourly.Variables(1).ValuesAsNumpy()
# hourly_direct_normal_irradiance = hourly.Variables(2).ValuesAsNumpy()
# hourly_global_tilted_irradiance = hourly.Variables(3).ValuesAsNumpy()

# print(hourly_shortwave_radiation, hourly_direct_normal_irradiance, hourly_direct_normal_irradiance, hourly_global_tilted_irradiance)
# print(current_temperature_2m)
# # current_variables = list(map(lambda i: current.Variables(i), range(0, current.VariablesLength())))
# # current_temperature_2m = next(filter(lambda x: x.Variable() == Variable.temperature and x.Altitude() == 2, current_variables))
# # current_relative_humidity_2m = next(filter(lambda x: x.Variable() == Variable.relative_humidity and x.Altitude() == 2, current_variables))

# # print(f"Current time {current.Time()}")
# # print(f"Current temperature_2m {current_temperature_2m.Value()}")
# # print(f"Current relative_humidity_2m {current_relative_humidity_2m.Value()}")






import openmeteo_requests

import pandas as pd
import requests_cache
from retry_requests import retry

# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)

# Make sure all required weather variables are listed here
# The order of variables in hourly or daily is important to assign them correctly below
url = "https://api.open-meteo.com/v1/forecast"
params = {
	"latitude": 18.71,
	"longitude": 73.67,
	"hourly": ["shortwave_radiation", "diffuse_radiation", "direct_normal_irradiance", "global_tilted_irradiance"],
	"current": "temperature_2m"
}
responses = openmeteo.weather_api(url, params=params)

# Process first location. Add a for-loop for multiple locations or weather models
response = responses[0]
print(f"Coordinates {response.Latitude()}°N {response.Longitude()}°E")
print(f"Elevation {response.Elevation()} m asl")
print(f"Timezone {response.Timezone()}{response.TimezoneAbbreviation()}")
print(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s")

# Current values. The order of variables needs to be the same as requested.
current = response.Current()
current_temperature_2m = current.Variables(0).Value()

print(f"Current time {current.Time()}")
print(f"Current temperature_2m {current_temperature_2m}")

# Process hourly data. The order of variables needs to be the same as requested.
hourly = response.Hourly()
hourly_shortwave_radiation = hourly.Variables(0).ValuesAsNumpy()
hourly_diffuse_radiation = hourly.Variables(1).ValuesAsNumpy()
hourly_direct_normal_irradiance = hourly.Variables(2).ValuesAsNumpy()
hourly_global_tilted_irradiance = hourly.Variables(3).ValuesAsNumpy()

hourly_data = {"date": pd.date_range(
	start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
	end = pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
	freq = pd.Timedelta(seconds = hourly.Interval()),
	inclusive = "left"
)}

hourly_data["shortwave_radiation"] = hourly_shortwave_radiation
hourly_data["diffuse_radiation"] = hourly_diffuse_radiation
hourly_data["direct_normal_irradiance"] = hourly_direct_normal_irradiance
hourly_data["global_tilted_irradiance"] = hourly_global_tilted_irradiance

hourly_dataframe = pd.DataFrame(data = hourly_data)
print(hourly_dataframe)
