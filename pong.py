#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Pong
 
Responds to raw pings with a pong."""
 
def pong(bot, event):
	bot.send("PONG " + event.message)
 
rules = {pong: 'ping'}

