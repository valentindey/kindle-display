#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
import base64
import sys
import xml.etree.cElementTree as ET
from datetime import datetime

import pytz

from mvg import get_departures
from weather import get_forecast

ID_MVG_FF_RING = 750
ID_MVG_MOOSACHER_STR = 331

ID_WEATHER_MILBERTSHOFEN = 2871160

UTC = pytz.timezone('UTC')
CET = pytz.timezone('CET')

DAYS_DE = {
    'Mon': 'Monatg',
    'Tue': 'Dienstag',
    'Wed': 'Mittwoch',
    'Thu': 'Donnerstag',
    'Fri': 'Freitag',
    'Sat': 'Samstag',
    'Sun': 'Sonntag'
}

MONTHS_DE = {
    'Jan': 'Januar',
    'Feb': 'Februar',
    'Mar': 'März',
    'Apr': 'April',
    'May': 'Mai',
    'Jun': 'Juni',
    'Jul': 'Juli',
    'Aug': 'August',
    'Sep': 'September',
    'Oct': 'Oktober',
    'Nov': 'November',
    'Dec': 'Dezember'
}


def get_date_strings(dt):
    """translates a datetime into a German date string
    setting the right locale would be easier in code (only datetime.strftime)
    but a bigger hassle to install on the kindle
    also this is not a very flexible way to handle the different time zones
    but good enough for this
    """
    localized_utc = UTC.localize(dt)
    localized_cet = localized_utc.astimezone(CET)
    day_str = DAYS_DE[localized_cet.strftime('%a')]
    month = MONTHS_DE[localized_cet.strftime('%b')]
    day = localized_cet.day
    hour = '{:02d}'.format(localized_cet.hour)
    minute = '{:02d}'.format(localized_cet.minute)
    return '{day_str}, {day}. {month}'.format(day_str=day_str, day=day, month=month), \
           '{hour}:{minute}'.format(hour=hour, minute=minute)


def generate_svg(filename):
    now = datetime.now()

    date_str, time_str = get_date_strings(now)

    departures_ms = get_departures(ID_MVG_MOOSACHER_STR)
    departure_texts_ms = [dep.get_text(now) for dep in departures_ms[:6]]
    departures_ffr = get_departures(ID_MVG_FF_RING, filter_only='UBAHN')
    departure_texts_ffr = [dep.get_text(now) for dep in departures_ffr[:6]]

    weather_forecast = get_forecast(ID_WEATHER_MILBERTSHOFEN)
    # gets the current weather, and those in 24 and 48 hours
    # for me that's good enough for a forecast for tomorrow and the day after
    weather_infos_3day = [weather_forecast.weather_infos[0],
                          weather_forecast.weather_infos[8],
                          weather_forecast.weather_infos[16]]

    gen_svg(date_str=date_str, time_str=time_str,
            departure_texts_ms=departure_texts_ms,
            departure_texts_ffr=departure_texts_ffr,
            weather_infos=weather_infos_3day,
            filename=filename)


def gen_svg(date_str, time_str, departure_texts_ms, departure_texts_ffr, weather_infos, filename):
    assert len(departure_texts_ms) <= 6, 'Can display max 6 departures for Moosacher Straße!'
    assert len(departure_texts_ffr) <= 6, 'Can display max 6 departures for Frankfurter Ring!'
    assert len(weather_infos) == 3, 'Need 3 weather infos: today, tomorrow and day after tomorrow!'

    svg_root = ET.Element('svg', xmlns='http://www.w3.org/2000/svg', width='600', height='800',
                          **{'xmlns:xlink': 'http://www.w3.org/1999/xlink'})

    ET.SubElement(svg_root, 'rect', width='600', height='800', style='fill:white;stroke-width:5;stroke:rgb(0,0,0)')

    def add_text(text, x, y, font_size):
        attrs = {
            'x': str(x),
            'y': str(y),
            'transform': 'rotate(90 {} {})'.format(x, y),
            'font-size': str(font_size)
        }
        ET.SubElement(svg_root, 'text', **attrs).text = text

    def add_image(image_path, x, y, w, h):
        # creating self-contained svgs by adding the base64 encoded image data directly
        # this way we don't need to care about correctly linking
        with open(image_path, 'rb') as f:
            b64data = base64.encodestring(f.read())
        attrs = {
            'x': str(x),
            'y': str(y),
            'width': str(w),
            'height': str(h),
            'transform': 'rotate(90 {} {})'.format(x + (w / 2), y + (h / 2)),
            'xlink:href': 'data:image/png;base64,{b64data}'.format(b64data=b64data)
        }
        ET.SubElement(svg_root, 'image', **attrs)

    add_text(date_str, x=550, y=20, font_size=32)
    add_text(time_str, x=480, y=20, font_size=70)

    add_text(u'Moosacher Straße', x=400, y=20, font_size=27)
    ET.SubElement(svg_root, 'line', x1='395', y1='20', x2='395', y2='400', style='stroke:black;stroke-width:2')
    for i, dep_ms in enumerate(departure_texts_ms):
        add_text(dep_ms, x=365 - (25 * i), y=20, font_size=20)

    add_text('Frankfurter Ring', x=200, y=20, font_size=27)
    ET.SubElement(svg_root, 'line', x1='195', y1='20', x2='195', y2='400', style='stroke:black;stroke-width:2')
    for i, dep_ffr in enumerate(departure_texts_ffr):
        add_text(dep_ffr, x=165 - (25 * i), y=20, font_size=20)

    add_text('Heute', x=550, y=500, font_size=32)
    add_image(weather_infos[0].icon_path, x=400, y=500, w=140, h=140)
    add_text(weather_infos[0].temp_range, x=470, y=650, font_size=26)
    add_text(weather_infos[0].description, x=370, y=500, font_size=26)

    add_text('Morgen', x=330, y=500, font_size=28)
    add_image(weather_infos[1].icon_path, x=220, y=500, w=100, h=100)
    add_text(weather_infos[1].temp_range, x=260, y=610, font_size=22)
    add_text(weather_infos[1].description, x=190, y=500, font_size=22)

    add_text(u'Übermorgen', x=150, y=500, font_size=28)
    add_image(weather_infos[2].icon_path, x=40, y=500, w=100, h=100)
    add_text(weather_infos[2].temp_range, x=80, y=610, font_size=22)
    add_text(weather_infos[2].description, x=10, y=500, font_size=22)

    tree = ET.ElementTree(svg_root)

    tree.write(filename)


if __name__ == '__main__':
    if len(sys.argv) == 2:
        filename = sys.argv[1]
    else:
        print('No argument given (or too many!), writing file to display.svg')
        filename = 'display.svg'
    generate_svg(filename)
