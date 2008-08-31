#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Delicious
 
Link logger which submits links to del.icio.us."""
 
import pydelicious, re
api = pydelicious.apiNew('NICKNAME', 'PASSWORD')
link_re = re.compile('^(.*\s)?(http://.+?)(\s.*)?$')
 
def addlink(bot, event):
	matches = link_re.findall(event.message)
	if (matches):
		matches = matches[0]
 
		url = matches[1]
		title = (matches[0] + matches[2]).trim() or url
		description = "<%s> %s" % (event.sender, event.message)
		tags = (event.sender, event.channel)
 
		api.posts_add(url=url, description=title, extended=description, tags=" ".join(tags))
		print "___ Posted '%s' to http://del.icio.us/%s" % (url, api.user)
 
rules = {addlink: 'msg'}

