#!/usr/bin/env python

import xml.parsers.expat
import urllib
import time
from datetime import datetime

class YrCyclingWeather:
	yrForecastURL = ""
	forecastInfo = {}
	hoursOfInterest = []
	forecastObject = {'windSpeed': 0, 'windDescription': '', 'windDirection': '', 'precipitation': 0, 'temperature': 0, 'description': ''}
	currentFromDatetime = ""
	humanReadableDescription = "{0}: {o[description]}. Wind: {o[windDescription]} {o[windSpeed]} {o[windDirection]}, Precipitation: {o[precipitation]}, Temp: {o[temperature]}"
	
	def __init__(self, yrForecastURL):
		self.yrForecastURL = yrForecastURL

	def addHourOfInterest(self, datetimeString):
		self.hoursOfInterest.append(datetimeString)

	def createForecastText(self):
		fh = urllib.urlopen(self.yrForecastURL)
		forecastXML = fh.read()
		
		p = xml.parsers.expat.ParserCreate()

		p.StartElementHandler = self.start_element
 		p.EndElementHandler = self.end_element
# 		p.CharacterDataHandler = self.char_data
		p.Parse(forecastXML, 1)
				
		forecastStrings = []
		for datetimeString, forecastObject in self.forecastInfo.iteritems():
			dt = datetime.strptime(datetimeString, "%Y-%m-%dT%H:%M:%S")
			forecastStrings.append(self.humanReadableDescription.format(dt.strftime('%H:%M'), o=forecastObject))
		
		return "\n".join(forecastStrings)
				
	def start_element(self, name, attrs):
		if name == "time":	
			self.currentFromDatetime = attrs['from']
			
			try:
				if self.hoursOfInterest.index(self.currentFromDatetime) != -1:
					self.forecastInfo[self.currentFromDatetime] = self.forecastObject
			except ValueError:
				pass

			return
			
		try:
			if  self.hoursOfInterest.index(self.currentFromDatetime) != -1:
				if name == "symbol":
					self.forecastInfo[self.currentFromDatetime]['description'] = attrs['name']
				if name == "windDirection":
					self.forecastInfo[self.currentFromDatetime]['windDirection'] = attrs['code']
				if name == "windSpeed":
					self.forecastInfo[self.currentFromDatetime]['windSpeed'] = 3.6 * float(attrs['mps'])
					self.forecastInfo[self.currentFromDatetime]['windDescription'] = attrs['name']
				if name == "temperature":
					self.forecastInfo[self.currentFromDatetime]['temperature'] = attrs['value']
		except ValueError:
			pass

	def end_element(self, name):
		if name == "time":
			self.currentFromDatetime = ""
		
		
yrForecast = YrCyclingWeather("http://www.yr.no/place/United_Kingdom/England/Pudsey~2639866/forecast_hour_by_hour.xml")
yrForecast.addHourOfInterest(time.strftime('%Y-%m-%dT08:00:00'))
yrForecast.addHourOfInterest(time.strftime('%Y-%m-%dT17:00:00'))

print yrForecast.createForecastText()
