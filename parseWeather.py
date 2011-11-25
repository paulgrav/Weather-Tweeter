#!/usr/bin/env python

import xml.parsers.expat
import urllib
import time

fh = urllib.urlopen("http://www.yr.no/place/United_Kingdom/England/Pudsey~2639866/forecast_hour_by_hour.xml")
forecastXML = fh.read()
toWorkDateTime = time.strftime('%Y-%m-%sT08:00:00')
toHomeDateTime = time.strftime('%Y-%m-%sT17:00:00')

forecastInfo[toWorkForecastInfo] = forecastInfo[toWorkDateTime] = {'windSpeed': 0, 'windDescription': '', 'windDirection': '', 'precipitation': 0, 'temperature': 0, 'description': ''}


toWorkObject = { }
# 3 handler functions
def start_element(name, attrs):
	if name == "time":	
	    currentFromDatetime = attrs['from']
	    return

	if currentFromDatetime == toWorkDateTime:
		if name == "symbol":
			toWorkForecastInfo['description'] = attrs['name']
	
def end_element(name):
    print 'End element:', name
def char_data(data):
    print 'Character data:', repr(data)

p = xml.parsers.expat.ParserCreate()

p.StartElementHandler = start_element
p.EndElementHandler = end_element
p.CharacterDataHandler = char_data

p.Parse(forecastXML, 1)

print toWorkForecastInfo
print toHomeForecastInfo
