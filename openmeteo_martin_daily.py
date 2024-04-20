import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry
import matplotlib.pyplot as plt

try:
    # Setup the Open-Meteo API client with cache and retry on error
    cache_session = requests_cache.CachedSession('.cache', expire_after=-1)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    openmeteo = openmeteo_requests.Client(session=retry_session)

    # Stop 53916 - Zilinska univerzita
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": 49.064179,
        "longitude": 18.916146,
        "start_date": "2022-05-01",
        "end_date": "2022-06-30",
        "daily": ["weather_code", "temperature_2m_max", "temperature_2m_min", "temperature_2m_mean",
                  "apparent_temperature_max", "apparent_temperature_min", "apparent_temperature_mean", "sunrise",
                  "sunset", "daylight_duration", "sunshine_duration", "precipitation_sum", "rain_sum",
                  "snowfall_sum", "precipitation_hours", "wind_speed_10m_max", "wind_gusts_10m_max",
                  "wind_direction_10m_dominant", "shortwave_radiation_sum", "et0_fao_evapotranspiration"],
        "timezone": "auto"
    }
    responses = openmeteo.weather_api(url, params=params)

    # Process first location. Add a for-loop for multiple locations or weather models
    response = responses[0]
    print(f"Coordinates {response.Latitude()}°N {response.Longitude()}°E")
    print(f"Elevation {response.Elevation()} m asl")
    print(f"Timezone {response.Timezone()} {response.TimezoneAbbreviation()}")
    print(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s")

    # Process daily data. The order of variables needs to be the same as requested.
    daily = response.Daily()
    daily_weather_code = daily.Variables(0).ValuesAsNumpy()
    daily_temperature_2m_max = daily.Variables(1).ValuesAsNumpy()
    daily_temperature_2m_min = daily.Variables(2).ValuesAsNumpy()
    daily_temperature_2m_mean = daily.Variables(3).ValuesAsNumpy()
    daily_apparent_temperature_max = daily.Variables(4).ValuesAsNumpy()
    daily_apparent_temperature_min = daily.Variables(5).ValuesAsNumpy()
    daily_apparent_temperature_mean = daily.Variables(6).ValuesAsNumpy()
    daily_sunrise = daily.Variables(7).ValuesAsNumpy()
    daily_sunset = daily.Variables(8).ValuesAsNumpy()
    daily_daylight_duration = daily.Variables(9).ValuesAsNumpy()
    daily_sunshine_duration = daily.Variables(10).ValuesAsNumpy()
    daily_precipitation_sum = daily.Variables(11).ValuesAsNumpy()
    daily_rain_sum = daily.Variables(12).ValuesAsNumpy()
    daily_snowfall_sum = daily.Variables(13).ValuesAsNumpy()
    daily_precipitation_hours = daily.Variables(14).ValuesAsNumpy()
    daily_wind_speed_10m_max = daily.Variables(15).ValuesAsNumpy()
    daily_wind_gusts_10m_max = daily.Variables(16).ValuesAsNumpy()
    daily_wind_direction_10m_dominant = daily.Variables(17).ValuesAsNumpy()
    daily_shortwave_radiation_sum = daily.Variables(18).ValuesAsNumpy()
    daily_et0_fao_evapotranspiration = daily.Variables(19).ValuesAsNumpy()

    daily_data = {"date": pd.date_range(
        start=pd.to_datetime(daily.Time(), unit="s", utc=True),
        end=pd.to_datetime(daily.TimeEnd(), unit="s", utc=True),
        freq=pd.Timedelta(seconds=daily.Interval()),
        inclusive="left"
    )}
    # The most severe weather condition on a given day
    # https://www.nodc.noaa.gov/archive/arc0021/0002199/1.1/data/0-data/HTML/WMO-CODE/WMO4677.HTM
    daily_data["weather_code"] = daily_weather_code

    # Maximum and minimum daily air temperature at 2 meters above ground
    daily_data["temperature_2m_max"] = daily_temperature_2m_max
    daily_data["temperature_2m_min"] = daily_temperature_2m_min
    daily_data["temperature_2m_mean"] = daily_temperature_2m_mean

    # Maximum and minimum daily apparent temperature
    daily_data["apparent_temperature_max"] = daily_apparent_temperature_max
    daily_data["apparent_temperature_min"] = daily_apparent_temperature_min
    daily_data["apparent_temperature_mean"] = daily_apparent_temperature_mean

    # Sun rise and set times (iso8601)
    daily_data["sunrise"] = daily_sunrise
    daily_data["sunset"] = daily_sunset

    # Number of seconds of daylight per day
    daily_data["daylight_duration"] = daily_daylight_duration

    # The number of seconds of sunshine per day is determined by calculating direct normalized irradiance exceeding 120 W/m²,
    # following the WMO definition.
    # Sunshine duration will consistently be less than daylight duration due to dawn and dusk.
    daily_data["sunshine_duration"] = daily_sunshine_duration

    # Sum of daily precipitation (including rain, showers and snowfall) (mm)
    daily_data["precipitation_sum"] = daily_precipitation_sum

    # Sum of daily rain (mm)
    daily_data["rain_sum"] = daily_rain_sum

    # Sum of daily snowfall (cm)
    daily_data["snowfall_sum"] = daily_snowfall_sum

    # The number of hours with rain
    daily_data["precipitation_hours"] = daily_precipitation_hours

    # Maximum wind speed and gusts on a day (km/h)
    daily_data["wind_speed_10m_max"] = daily_wind_speed_10m_max
    daily_data["wind_gusts_10m_max"] = daily_wind_gusts_10m_max

    # Dominant wind direction (°)
    daily_data["wind_direction_10m_dominant"] = daily_wind_direction_10m_dominant

    # The sum of solar radiaion on a given day in Megajoules
    daily_data["shortwave_radiation_sum"] = daily_shortwave_radiation_sum

    # Daily sum of ET₀ Reference Evapotranspiration of a well watered grass field (mm)
    daily_data["et0_fao_evapotranspiration"] = daily_et0_fao_evapotranspiration

    daily_dataframe = pd.DataFrame(data=daily_data)

    # Temp plot
    plt.figure(figsize=(10, 6))
    # Mean temperature
    plt.plot(daily_dataframe['date'], daily_dataframe['temperature_2m_mean'], color='violet', marker='o',
             linestyle='-', label='Priemerná teplota (°C)')
    # Max temperature
    plt.plot(daily_dataframe['date'], daily_dataframe['temperature_2m_max'], color='red', linestyle='-',
             label='Najvyššia teplota (°C)')
    # Min temperature
    plt.plot(daily_dataframe['date'], daily_dataframe['temperature_2m_min'], color='blue', linestyle='-',
             label='Najnižšia teplota (°C)')
    plt.title('Denná teplota - 2 metre nad zemou - zastávka Martin, aut.st.')
    plt.xlabel('Dátum')
    plt.ylabel('Teplota (°C)')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.legend()
    plt.grid(True)
    plt.show()

    # Precipitation sum plot
    plt.figure(figsize=(10, 6))
    bar_width = 0.3
    bar_positions_sum = daily_dataframe['date']
    plt.bar(bar_positions_sum, daily_dataframe['precipitation_sum'], color='blue', width=bar_width,
            label='Súčet zrážok (mm)')
    plt.title('Denný súčet zrážok - zastávka Martin, aut.st.')
    plt.xlabel('Dátum')
    plt.xticks(bar_positions_sum, daily_dataframe['date'].dt.strftime('%m-%d'), rotation=90)
    plt.legend()
    plt.tight_layout()
    plt.grid(axis="y")
    plt.show()

    # Wind speed plot
    plt.figure(figsize=(10, 6))
    plt.plot(daily_dataframe['date'], daily_dataframe['wind_speed_10m_max'], color='blue', linestyle='-',
             label='Maximálna rýchlosť vetra (km/h)')
    plt.plot(daily_dataframe['date'], daily_dataframe['wind_gusts_10m_max'], color='red', marker="o", linestyle='-',
             label='Maximálna rýchlosť poryvov vetra (km/h)')
    plt.title('Denná rýchlosť vetra - zastávka Martin, aut.st.')
    plt.xlabel('Dátum')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.legend()
    plt.grid(True)
    plt.show()

except Exception as e:
    print(f"An error occurred: {e}")
