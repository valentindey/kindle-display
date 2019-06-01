# -*- coding: utf-8 -*-

import json
import os
import time

import requests

BASE_URL = 'http://api.openweathermap.org/data/2.5'
API_KEY = 'YOUR_KEY_HERE'


class WeatherInfo:

    def __init__(self, description, icon_path, temp_min, temp_max):
        self.description = description
        self.icon_path = icon_path
        self.temp_min = temp_min
        self.temp_max = temp_max
        self.temp_range = self.get_temp_range_text()

    def get_temp_range_text(self):
        t_min = int(round(self.temp_min))
        t_max = int(round(self.temp_max))
        if t_min == t_max:
            return u'{t_min}°C'.format(t_min=t_min)
        return u'{t_min}-{t_max}°C'.format(t_min=t_min, t_max=t_max)

    @classmethod
    def from_dict(cls, dct):
        dct.pop('temp_range')
        return cls(**dct)


class Forecast(object):

    def __init__(self, weather_infos, timestamp):
        self.weather_infos = weather_infos
        self.timestamp = timestamp

    def older_than(self, hours):
        now = time.time()
        if now - self.timestamp > (3600 * hours):
            return True
        return False

    def save(self, path):
        data = {
            'weather_infos': [wi.__dict__ for wi in self.weather_infos],
            'timestamp': self.timestamp
        }
        with open(path, 'w') as fp:
            json.dump(data, fp, indent=4)

    @classmethod
    def load(cls, path):
        with open(path, 'r') as fp:
            data = json.load(fp)
        return cls(weather_infos=[WeatherInfo.from_dict(dct) for dct in data['weather_infos']],
                   timestamp=data['timestamp'])


def get_forecast(location_id):
    path = os.path.join(os.path.dirname(__file__), 'weather_3_days_{location_id}'.format(location_id=location_id))
    try:
        loaded_forecast = Forecast.load(path)
        if not loaded_forecast.older_than(hours=3):
            return loaded_forecast
    except IOError:
        print('unable to retrieve or error reading persisted weather info from "{path}";'
              ' getting new forecast'.format(path=path))
    forecast = get_forecast_from_web(location_id)
    forecast.save(path)
    return forecast


def get_forecast_from_web(location_id):
    response = requests.get("{BASE_URL}/forecast?id={location_id}&APPID={API_KEY}&lang=de".format(BASE_URL=BASE_URL,
                                                                                                  location_id=location_id,
                                                                                                  API_KEY=API_KEY))
    response.raise_for_status()
    resp_json = response.json()

    forecast_list = resp_json['list']

    return Forecast(weather_infos=[get_weather_info(info) for info in forecast_list], timestamp=time.time())


def get_weather_info(weather_json):
    description = weather_json['weather'][0]['description']
    icon_path = get_icon_path(weather_json['weather'][0]['icon'])
    temp_min = kelvin_to_celsius(weather_json['main']['temp_min'])
    temp_max = kelvin_to_celsius(weather_json['main']['temp_max'])
    return WeatherInfo(description=description, icon_path=icon_path, temp_min=temp_min, temp_max=temp_max)


def get_icon_path(icon_id):
    return os.path.abspath(os.path.join(os.path.dirname(__file__), 'weather_icons',
                                        '{icon_id}.png'.format(icon_id=icon_id)))


def kelvin_to_celsius(k):
    return k - 273.15
