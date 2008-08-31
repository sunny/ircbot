#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Admin : fonctions utiles à l'administration du bot
et accessibles seulement au patron.
 
Commandes :
 !reload          recharge tous les plugins
 !quit [message]  fais quitter le bot
 !nick nick        change de pseudonyme"""
 
def _isadmin(user):
	"""Returns wether or not the bot can trust this person to be the admin"""
	return user.host.endswith('YOURHOST')
 
def identify(bot, event):
	"""Identify bot on join"""
	bot.msg('nickserv', 'identify PASSWORD')
 
def reloadplugins(bot, event):
	"""Reload all plugins using !reload"""
	if _isadmin(event.sender) and event.firstword() == '!reload':
		bot.loadplugins()
		identify(bot, event)
		bot.msg(event.sender.nick, "Plugins reloaded.")
 
def quit(bot, event):
	"""Quit bot using !quit [message]"""
	if _isadmin(event.sender) and event.firstword() == '!quit':
		bot.quit(event.arguments())
 
def nick(bot, event):
	"""Change nick using !nick nickname"""
	if _isadmin(event.sender) and event.firstword() == '!nick':
		bot.changenick(event.arguments())
 
def say(bot, event):
	"""Say something nick"""
	if _isadmin(event.sender) and event.firstword() == '!say':
		arguments = event.message.split(' ')
		bot.msg(arguments[1], ' '.join(arguments[2:]))
 
rules = {
	reloadplugins: 'privmsg', 
	quit: 'privmsg', 
	say: 'privmsg',
	identify: ('motd-end','nickchange','reload'), # TODO identify on nickchange
	 nick: 'privmsg',
}
 
