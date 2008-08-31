#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Parrot
 
Repeats what at least two others have already just said on a chan."""
 
import random
 
lastlines = {} # dictionnary with last message event for each channel
 
def parrot(bot, event):
	"""Repeats if someone else just said the same thing"""
	if event.channel not in lastlines:
		lastlines[event.channel] = False
 
	if (not hasattr(event, 'answered') or event.answered == False) \
	  and lastlines[event.channel] and lastlines[event.channel].message == event.message \
	  and lastlines[event.channel].sender != event.sender and random.randint(0, 4):
		if event.type == 'action':
			bot.action(event.channel, event.message + ' aussi')
		else:
			bot.msg(event.channel, event.message)
		event.answered = True
		lastlines[event.channel] = False
	else:
		lastlines[event.channel] = event
 
rules = {parrot: ('msg','action')}

