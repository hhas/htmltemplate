#!/usr/bin/env python3

""" htmlcalendar - Functions and classes for generating one-month and twelve-month calendars in HTML format.

Copyright (C) 2007-2016 HAS

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""

import calendar, getopt, os, os.path, sys, time, webbrowser, urllib.parse

from htmltemplate import Template


gHelp = """htmlcalendar -- generate 12 month HTML calendar

Usage:

	python3 /path/to/htmlcalendar.py [-b] [-h] [-o PATH] [-s] [-y YEAR]
	
	-b -- if -o option is also given, open the generated file in user's web browser
	
	-h -- print this help and exit
	
	-o -- path to write HTML file; if omitted, HTML is written to STDOUT
	
	-s -- start each calendar week on Sunday; if omitted, start on Monday
	
	-y -- the year; if omitted, generates calendar for current year

Example:

	python3 /path/to/htmlcalendar.py -b -y 2014 -o 2014.html -s
"""


#################################################
# SUPPORT
#################################################

gTemplatesDir = os.path.join(os.path.dirname(__file__), 'templates')

def readfile(dirpath, name):
	with open(os.path.join(dirpath, name), encoding='utf8') as f:
		return f.read()


#################################################
# Month Calendar
#################################################


class CalendarRenderer:
	""" Renders a one-month calendar. """

	gTemplate = Template(readfile(gTemplatesDir, 'month_template.html'))
	
	_months = ["January", "February", "March", "April", "May", "June", 
			"July", "August", "September", "October", "November", "December"]

	_sundaytosaturday = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
	
	year = property(lambda self: self._year)

	def __init__(self, year=None, sundayfirst=True, dayrenderer=None):
		"""
			year : int | None -- e.g. 2014; default is current year
			sundayfirst : bool -- if True, week begins on Sunday, else Monday
			dayrenderer : function | None -- if given, a function that takes year, month, day and returns the HTML for a single calendar cell (e.g. this can be used to add links, reminders, etc. to cells); if None, the day number is inserted
		"""
		self._template = self.gTemplate.copy()
		self._year = time.gmtime()[0] if year is None else int(year)
		self._dayrenderer = dayrenderer or self._defaultdayrenderer
		if sundayfirst:
			self._firstweekday = 6
			columnlabels = self._sundaytosaturday
		else: 
			self._firstweekday = 0
			columnlabels = self._sundaytosaturday[1:] + [self._sundaytosaturday[0]]
		self._weekendtracker = [sundayfirst, False, False, False, False, not sundayfirst, True]
		self._template.labels.repeat(self._renderlabels, columnlabels) # pre-render column labels for efficiency
	
	def _renderlabels(self, node, weekday):
		node.atts['title'] = weekday
		node.text = weekday[0]
	
	def _defaultdayrenderer(self, year, month, day):
		return int(day)
	
	def _renderday(self, node, day, month, weekendtracker):
		isweekend = next(weekendtracker)
		if isweekend:
			node.atts['class'] = 'wkend'
		if day == 0:
			node.html = '&nbsp;'
		else:
			node.html = self._dayrenderer(self._year, month, day)
	
	def _renderweek(self, node, weekdays, month):
		node.day.repeat(self._renderday, weekdays, month, iter(self._weekendtracker))
	
	def _rendertemplate(self, node, month):
		fd = calendar.firstweekday()
		calendar.setfirstweekday(self._firstweekday)
		weeks = calendar.monthcalendar(self._year, month) # a list of seven-item lists
		calendar.setfirstweekday(fd)
		if len(weeks) == 5:
			weeks.append([0, 0, 0, 0, 0, 0, 0])
		node.caption.text = self._months[month - 1] # set table caption
		node.week.repeat(self._renderweek, weeks, month) # render weekly rows
	
	def render(self, month=None):
		""" Render a one-month calendar.
		
				month : int -- 1-12
				Result : str -- HTML table
		"""
		month = time.gmtime()[1] if month is None else int(month)
		return self._template.render(self._rendertemplate, month)



#################################################
# Table grid renderer
#################################################

gGridTemplate = Template(readfile(gTemplatesDir, 'grid_template.html'))

def grid_cell(node, cellvalue, cellrenderer):
	node.content.html = cellrenderer(cellvalue)

def grid_row(node, cellvalues, cellrenderer):
	node.cell.repeat(grid_cell, cellvalues, cellrenderer)

def render_grid(node, cellrenderer):
	""" Render a 4x3 table; each cell's content is generated by cellrenderer
	
			node : Template -- the grid template to render
			cellrenderer : function -- a function that takes an integer from 1 to 12 and returns an HTML string
	"""
	node.row.repeat(grid_row, [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]], cellrenderer) 


#################################################
# Page renderer
#################################################

gPageTemplate = Template(readfile(gTemplatesDir, 'page_template.html'))

gPageTemplate.content = gGridTemplate # graft grid template onto placeholder


def renderyearcalendar(year=None, sundayfirst=True, dayrenderer=None):
	""" Render a twelve-month calendar as a complete HTML page.
	
			year : int | None -- e.g. 2014; default is current year
			sundayfirst : bool -- if True, week begins on Sunday, else Monday
			dayrenderer : function | None -- if given, a function that takes year, month, day and returns the HTML for a single calendar cell (e.g. this can be used to add links, reminders, etc. to cells); if None, the day number is inserted
			Result : str -- HTML document
	"""
	monthrenderer = CalendarRenderer(year, sundayfirst, dayrenderer)
	node = gPageTemplate.copy()
	node.title.text = node.title.text.format(year=monthrenderer.year)
	node.heading.text = node.heading.text.format(year=monthrenderer.year)
	render_grid(node.content, monthrenderer.render)
	return node.render()


#################################################
# CLI
#################################################

if __name__ == '__main__':
	opts = dict(getopt.getopt(sys.argv[1:], 'bho:sy:')[0])
	if '-h' in opts:
		print(gHelp)
		sys.exit()
	html = renderyearcalendar(opts.get('-y'), '-s' in opts)
	if '-o' in opts:
		path = os.path.abspath(os.path.expanduser(opts['-o']))
		with open(path, 'w') as f:
			f.write(html)
		if '-b' in opts:
			webbrowser.open_new(urllib.parse.urlunparse(('file', 'localhost', path, '', '', '')))
	else:
		print(html)

