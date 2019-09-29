# -*- coding: utf-8 -*-

from datetime import datetime

import requests

BASE_URL = 'https://www.mvg.de/fahrinfo/api'
HEADERS = {
    'Accept': 'application/json',
    'X-MVG-Authorization-Key': 'YOUR_KEY_HERE'
}


class Departure:

    def __init__(self, product, line, destination, departure_time):
        self.product = product
        self.line = line
        self.destination = destination
        self.departure_time = departure_time

    def get_text(self, now):
        mins_until = int(((self.departure_time - now).seconds / 60.) + 1)
        return u'In {mins_until} Min: {line} Richtung {destination}'.format(mins_until=mins_until,
                                                                            line=self.line,
                                                                            destination=self.destination)


def get_departures(station_id, filter_only=None):
    response = requests.get("{BASE_URL}/departure/{station_id}".format(BASE_URL=BASE_URL, station_id=station_id),
                            headers=HEADERS)
    if response.status_code != 200:
        print('unable to get departures from mvg: http error {STATUS_CODE}'.format(STATUS_CODE=response.status_code))
        return []
    j = response.json()
    departures = []
    for dep in j['departures']:
        if not filter_only or dep['product'] == filter_only:
            departure_time = datetime.fromtimestamp(dep['departureTime'] / 1000)
            departures.append(Departure(product=dep['product'],
                                        line=dep['label'],
                                        destination=dep['destination'],
                                        departure_time=departure_time))
    return departures


def station_ids(query):
    response = requests.get("{BASE_URL}/location/query".format(BASE_URL=BASE_URL), params={'q': query}, headers=HEADERS)
    return [station['id'] for station in response.json()['locations'] if station['type'] == 'station']
