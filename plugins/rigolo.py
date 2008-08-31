#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Rigolo
 
Plugin méga-déconnade qui rajoute une pseudo-intelligence artificielle au robot en répondant aux questions de temps en temps, 
à son nom, etc."""
 
import random, re
 
re_smileys = re.compile('(^| ):[pD)(\]]( |$)')
re_lol = re.compile('(^| )(lol|mdr|rofl)( |$)')
 
def responses(bot, event):
	# send a message with a random weight
	def _msg(message, weight = 0):
		if (not hasattr(event, 'answered') or event.answered == False) and (weight == 0 or random.randint(0, weight) == 0):
			if not isinstance(message, str): # if it is a list of messages, take one randomly
				message = random.choice(message)
			bot.msg(event.channel, message)
			event.answered = True
			return True
 
	# quick responses
	responses = {
		'lu':'stucru',
		'hein':'deux',
		('quoi?','quoi ?'):'feur !',
		('a+','++'):('a+','++'),
	}
	for questions, responses in responses.iteritems():
		if isinstance(questions, str): questions = (questions,)
		for question in questions:
			if event.message == question:
				if _msg(responses, 2): return
 
	# position improbable
	if event.message.startswith('où'):
		if _msg('dtc', 2): return
 
	# talkin' to me ?
	if re.compile(bot.nick + r'[^a-zA\Z]').search(event.message):
		if event.message.endswith('?'):
			if _msg(('ouais','euh ouais','vi','sans doute','c\'est possible','j\'en sais rien moi D:','arf, non','non','nan','euh nan','negatif','euhh peut-être'), 3): return
		else:
			if _msg(('3:-0','','oui ?','...','lol','mdr',':\')','arf','shhh',':)','3:)','tg :k','moi aussi je t\'aime', 'oui oui %s' % event.sender), 4): return
 
	# question ?
	if event.message.endswith('?'):
		if _msg(('oui','ouais','ouaip','moi j\'en sais rien','non','nan'), 20): return
 
	# lol inside
	if re_lol.search(event.message):
		if _msg(('lol','mdr',':)'), 20): return
 
	# smile :)
	if re_smileys.search(event.message):
		if _msg((':D',':p',':)'), 20): return
 
	# n'importe quel message
	if _msg(':)', 400): return
 
rules = {responses:('msg','privmsg')}


