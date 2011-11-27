#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xml.parsers.expat
import urllib
import time
import copy
from datetime import datetime, timedelta

class YrCyclingWeather:
	yrForecastURL = ""
	forecastInfo = {}
	hoursOfInterest = []
	emptyForecastObject = {'windSpeed': 0, 'windDescription': '', 'windDirection': '', 'precipitation': 0, 'temperature': 0, 'description': ''}
	currentFromDatetime = ""
	currentForecastObject = ""
	humanReadableDescription = u"{0} {1} - {o[description]} {o[temperature]}°. Wind: {o[windDescription]} {o[windSpeed]} {o[windDirection]}. Rain: {o[precipitation]}"
	
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
# 		p.CharacterDataHandler = self.char_data
		p.Parse(forecastXML, 1)
				
		forecastStrings = []
		for n in range(0, 2):
			(datetimeString, forecastObject) = self.forecastInfo.popitem()
			dt = datetime.strptime(datetimeString, "%Y-%m-%dT%H:%M:%S")
			
			now = datetime.now()
			day = dt.strftime('%d/%m')
			
			if now.strftime('%d') == dt.strftime('%d'):
				day = 'Today'
			
			if (now +  timedelta(days=1)).strftime('%d') == dt.strftime('%d'):
				day = 'Tomorrow'
			
			forecastStrings.append(self.humanReadableDescription.format(day, dt.strftime('%H:%M'), o=forecastObject))
		
		return "\n".join(forecastStrings)
				
	def start_element(self, name, attrs):
		if name == "time":	
			self.currentFromDatetime = attrs['from']
			try:
				if self.hoursOfInterest.index(datetime.strptime(self.currentFromDatetime, "%Y-%m-%dT%H:%M:%S").hour) != -1:
					self.currentForecastObject = copy.copy(self.emptyForecastObject)
				else:
					self.currentForecastObject = ""
			except ValueError:
				pass

			return
			
		try:
			if self.hoursOfInterest.index(datetime.strptime(self.currentFromDatetime, "%Y-%m-%dT%H:%M:%S").hour) != -1:
				if name == "symbol":
					self.currentForecastObject['description'] = attrs['name']
				if name == "windDirection":
					self.currentForecastObject['windDirection'] = attrs['code']
				if name == "windSpeed":
					self.currentForecastObject['windSpeed'] = 3.6 * float(attrs['mps'])
					self.currentForecastObject['windDescription'] = attrs['name']
				if name == "temperature":
					self.currentForecastObject['temperature'] = attrs['value']
		except ValueError:
			pass

	def end_element(self, name):
		if name == "time" and self.currentForecastObject != "":
			self.forecastInfo[self.currentFromDatetime] = self.currentForecastObject;
			self.currentForecastObject = ""
			self.currentFromDatetime = ""
		
		
yrForecast = YrCyclingWeather("http://www.yr.no/place/United_Kingdom/England/Pudsey~2639866/forecast_hour_by_hour.xml")
yrForecast.addHourOfInterest(8)
yrForecast.addHourOfInterest(17)

print yrForecast.createForecastText()
