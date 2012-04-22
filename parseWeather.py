#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xml.parsers.expat
import urllib
import time
import copy
import logging
from datetime import datetime, timedelta

class YrCyclingWeather:
    yrForecastURL = ""
    forecastInfo = {}
    hoursOfInterest = []
    emptyForecastObject = {'windSpeed': 0,
                           'windDescription': '',
                           'windDirection': '',
                           'precipitation': 0,
                           'temperature': 0,
                           'description': '',
                           'feelsLike': 0}
    currentFromDatetime = ""
    currentForecastObject = ""
    humanReadableDescription = "{0} {1} - {o[description]} {o[temperature]:.0f}°" \
        "({o[feelsLike]:.0f}°). " \
        "{o[windDescription]} {o[windSpeed]:.0f} {o[windDirection]}." \
        " Rain: {o[precipitation]:.0%}"
    current_day = ""
    current_element = None

    def __init__(self, yrForecastURL):
        self.yrForecastURL = yrForecastURL

    def addHourOfInterest(self, hour):
        self.hoursOfInterest.append(hour)

    def createForecastText(self):
        fh = urllib.urlopen(self.yrForecastURL)
        forecastXML = fh.read()

        p = xml.parsers.expat.ParserCreate()

        p.StartElementHandler = self.start_element
        p.EndElementHandler = self.end_element
        p.CharacterDataHandler = self.char_data
        p.Parse(forecastXML, 1)

        forecastStrings = []
        dateKeys = self.forecastInfo.keys()
        dateKeys.sort()
        for n in range(0, 2):
            try:
                dt = dateKeys[n]
            except IndexError:
                continue

            forecastObject = self.forecastInfo[dt]

            now = datetime.now()
            day = dt.strftime('%d/%m')

            if now.strftime('%d') == dt.strftime('%d'):
                day = 'Today'

            if (now +  timedelta(days=1)).strftime('%d') == dt.strftime('%d'):
                day = 'Tomorrow'

            forecastStrings.append(
                self.humanReadableDescription.format(day,
                                                     dt.strftime('%H:%M'),
                                                     o=forecastObject))

        return "\n".join(forecastStrings)

    def start_element(self, name, attrs):
        self.current_element = name

        if name == "Day":
            self.current_day = attrs['date']

        if name == "TimeStep":
            time = self.current_day + "T" + attrs["time"]
            self.currentFromDatetime = datetime.strptime(time,
                                                         "%Y-%m-%dT%H:%M:%S")
            try:
                if type(self.currentFromDatetime) is datetime \
                 and self.hoursOfInterest.index(self.currentFromDatetime.hour) != -1:
                    self.currentForecastObject = copy.copy(self.emptyForecastObject)
                else:
                    self.currentForecastObject = None
            except ValueError:
                pass

    def char_data(self, data):
        try:
            if type(self.currentFromDatetime) is datetime \
                 and self.hoursOfInterest.index(self.currentFromDatetime.hour) != -1:

                if self.current_element == "FeelsLikeTemperature":
                    self.currentForecastObject['feelsLike'] = float(data)

                if self.current_element == "WindSpeed":
                    self.currentForecastObject['windSpeed'] = float(data) * 3.6

                if self.current_element == "PrecipitationProbability":
                    self.currentForecastObject['precipitation'] = float(data)/100

                if self.current_element == "WindDirection":
                    self.currentForecastObject['windDirection'] = data

                if self.current_element == "Temperature":
                    self.currentForecastObject['temperature'] = float(data)

        except ValueError:
            pass

    def end_element(self, name):
        if name == "TimeStep" and self.currentForecastObject:
            self.forecastInfo[self.currentFromDatetime] = self.currentForecastObject;
            self.currentForecastObject = None
            self.currentFromDatetime = None

if __name__ == "__main__":
    yrForecast = YrCyclingWeather("http://www.metoffice.gov.uk/public/data/PWSCache/BestForecast/Forecast/353127")
    yrForecast.addHourOfInterest(9)
    yrForecast.addHourOfInterest(18)
    print yrForecast.createForecastText()
