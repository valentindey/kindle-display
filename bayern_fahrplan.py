# -*- coding: utf-8 -*-
import re
from datetime import datetime
from xml.dom.minidom import parseString

import requests

BASE_URL = 'https://txt.bayern-fahrplan.de/textversion/bcl_abfahrtstafel'
HEADERS = {
    'Accept': 'text/html',
    'Content-Type': 'application/x-www-form-urlencoded'
}


class Departure:

    def __init__(self, line, destination, departure_time):
        self.line = line
        self.destination = destination
        self.departure_time = departure_time

    def get_text(self, now):
        if now > self.departure_time:
            mins_until = 0  # not necessarily true, bot an ok workaround for this use case
        else:
            mins_until = (self.departure_time - now).seconds / 60
        return u'In {mins_until} Min: {line} Richtung {destination}'.format(mins_until=mins_until,
                                                                            line=self.line,
                                                                            destination=self.destination)


def get_departures(station_id, ubahn_express_bus_only=False):
    form_data = get_form_data(station_id)
    response = requests.post(BASE_URL, headers=HEADERS, data=form_data, verify=False)
    doc = parseString(response.content)
    # getElementById('') won't work, as the id is not known as such
    # see https://www.w3.org/TR/DOM-Level-2-Core/core.html#ID-getElBId
    table_elem = doc.getElementsByTagName('table')[1]
    table_body = table_elem.getElementsByTagName('tbody')[0]
    departures = []
    for table_row in table_body.childNodes[1:]:  # skipping the header
        date_elem, time_elem, line_elem, dest_elem, platform_elem = table_row.childNodes
        line = elem_to_text(line_elem)
        if ubahn_express_bus_only and not (line.startswith('U') or line.startswith('X')):
            continue
        destination = elem_to_text(dest_elem)
        departure_time = get_datetime(date_elem=date_elem, time_elem=time_elem)
        departures.append(Departure(line=line, destination=destination, departure_time=departure_time))

    return departures


def get_form_data(station, date=None, limit=20):
    if date is None:
        date = datetime.now()
    return {
        'limit': limit,
        'useRealtime': 1,
        'itdLPxx_bcl': 'true',
        'type_dm': 'any',
        'deleteAssignedStops': '1',
        'mode': 'direct',
        'itdTimeHour': date.hour,
        'itdTimeMinute': date.minute,
        'itdDate': '{}{:02d}{:02d}'.format(date.year, date.month, date.day),
        'name_dm': station
    }


def elem_to_text(elem):
    return elem.firstChild.nodeValue


date_re = re.compile(r'(\d\d?)\.(\d\d?)\.(\d\d\d\d)')
time_re = re.compile(r'(\d\d?):(\d\d).*')


def get_datetime(date_elem, time_elem):
    date_match = date_re.match(elem_to_text(date_elem))
    day = int(date_match.group(1))
    month = int(date_match.group(2))
    year = int(date_match.group(3))
    time_match = time_re.match(elem_to_text(time_elem))
    hour = int(time_match.group(1))
    minute = int(time_match.group(2))
    return datetime(year=year, month=month, day=day, hour=hour, minute=minute)
