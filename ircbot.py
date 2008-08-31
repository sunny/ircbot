#!/usr/bin/python
# -*- coding: utf-8 -*-
"""IRCBot

IRC Bot supporting plugins
"""
 
import os, socket, sys, re
 
__module__ = "IRCBot"
__author__ = "Sunny Ripert <negatif@gmail.com>"
__copyright__ = "Copyright (c) 2003 Sunny Ripert"
__license__ = "GPL"
__version__ = "1.0"
 
RE_USER = re.compile('(.+?)!n?=?(.+?)@(.+)')
 
class Bot(object):
	"""IRC Bot"""
	def __init__(self, host, port, nick, ident, realname, channels = []):
		"""Creates a new bot, initialising the socket, loading plugins, connecting"""
		self.host = host
		self.port = port
		self.nick = nick
		self.ident = ident
		self.realname = realname
		self.channels = channels
		self.socket = socket.socket()
		self.socketbuffer = ""
		self.hooks = {}
		self.online = False
		self.loadplugins()
		self.connect()
 
	# Plugins and hooks handling
 
	def addhook(self, eventtype, function):
		"""Adds a hook to the bot"""
		if not eventtype in self.hooks: # if hook key doesn't exist, make it
			self.hooks[eventtype] = []
		self.hooks[eventtype].append(function) # add hook to list
 
	def loadplugin(self, name):
		"""Loads a plugin from plugins/[name].py"""
		try: module = getattr(__import__('plugins.' + name), name)
		except Exception, e:
			print "### Error loading %s: %s" % (name, e)
			return
 
		if hasattr(module, 'imported'):
			try: reload(module) # reload plugin
			except Exception, e:
				print "### Error reloading %s: %s" % (name, e)
				return
		else: module.imported = True
 
		for function, events in module.rules.iteritems():
			if isinstance(events, str): events = (events,)
			for eventtype in events:
				self.addhook(eventtype, function)
 
	def loadplugins(self):
		"""Loads all plugins in the directory, reinitializing hooks"""
		self.hooks = {}
		pluginsdir = os.path.join(os.getcwd(), 'plugins')
		for filename in sorted(os.listdir(pluginsdir)):
			if filename.endswith('.py') and not filename.startswith('_'):
				name, ext = os.path.splitext(os.path.basename(filename))
				self.loadplugin(name)
 
	def trigger_event(self, type, message = None, sender = None, channel = None, where = None) :
		"""Launches a newly created event"""
		self.trigger(Event(type, message, sender, channel, where))
 
	def trigger(self, event):
		"""Launches all hooks for that event"""
		if event == None: return
		print "=== %s" % event # for debug
		if event.type in self.hooks:
			for function in self.hooks[event.type]:
				try: function(self, event) # launch the hook with arguments the bot and the triggering event
				except Exception, e:
					print "### Error in hook %s from %s: %s" % (function.__name__, function.__module__, e)
 
	# Socket handling
 
	def connect(self):
		"""Connects to the socket and sets default socket options"""
		self.socket.connect((self.host, self.port))
		self.socket.settimeout(2.0)
		self.send("NICK %s" % self.nick)
		self.send("USER %s %s %s :%s" % (self.ident, '+iw', self.nick, self.realname))
		self.online = True
		self.trigger_event('connect')
 
	def quit(self, message = ""):
		"""Kindly quits the IRC server with a message"""
		self.trigger_event('disconnect')
		self.send("QUIT :" + message)
		self.online = False
 
	def run(self):
		"""Gets the last lines from the buffer, waiting for the timeout and sends triggers"""
		try: self.socketbuffer += self.socket.recv(1024)
		except socket.timeout:
			pass
		bufferlines = self.socketbuffer.split("\n")
		self.socketbuffer = bufferlines.pop()
		for line in bufferlines:
			line = line.rstrip()
			print "<-- %s" % line
			self.parseraw(line)
 
	def send(self, command):
		"""Send line to socket"""
		print "--> %s" % command
		self.socket.send(command + "\r\n")
 
	# IRC RFC handling
 
	def parseraw(self, line):
		"""React to given IRC raw input"""
		words = line.split() # wouldn't it be sexyer with regexps ?
		if words[0] == 'PING':
			self.trigger_event('ping', words[1])
		elif words[1] == 'PRIVMSG':
			sender = User.fromraw(words[0][1:])
			message = ' '.join([words[3][1:]] + words[4:]).strip() # strips ":" and whitespace
			if words[2].startswith('#'):
				if message.startswith('ACTION'): # /me on a chan
					self.trigger_event('action', message[7:-1], sender, channel=words[2])
				else: # message on a chan
					self.trigger_event('msg', message, sender, channel=words[2])
			else:
				if message.startswith('ACTION'): # private /me
					self.trigger_event('privaction', message[7:-1], sender)
				else:
					self.trigger_event('privmsg', message, sender) # private message
 
		elif line.startswith('ERROR :Closing Link:'): # error on connection
			self.trigger_event('closing', ' '.join(words[0:3]))
 
		elif words[1] == '376': # end of MOTD
			for channel in self.channels: # join chans
				self.join(channel)
			self.trigger_event('motd-end')
 
		elif words[1] == '433': # Nickname already in use
			self.changenick(self.nick + '_')
 
 
 
 
	def msg(self, who, message):
		"""Send a private message to a user or a public message on a channel"""
		self.send("PRIVMSG %s :%s" % (who, message))
		self.trigger_event('sendmsg', message, channel=who)
 
	def action(self, who, message):
		"""Send a /me message to a user or a public /me on a channel"""
		self.send("PRIVMSG %s :ACTION %s" % (who, message))
		self.trigger_event('sendaction', message, channel=who)
 
	def join(self, channel):
		"""Joins given channel"""
		self.send("JOIN " + channel)
		self.trigger_event('join', channel=channel)
 
	def changenick(self, nick):
		"""Change nickname and save new name"""
		self.nick = nick
		self.send("NICK %s" % nick)
		self.trigger_event('nickchange', message=nick)
 
class Event(object):
	"""IRC event of any kind provided by raw rfc"""
	def __init__(self, type, message = None, sender = None, channel = None, where = None):
		"""Creates a new event"""
		self.type, self.message, self.sender, self.channel, self.where = type, message, sender, channel, where
 
	def __str__(self):
		"""Returns string eg 'type (attr:value, ...)'"""
		options = ["%s:%s" % (k, v) for k, v in self.__dict__.iteritems() if v and k != 'type']
		if len(options) == 0: return '%s' % self.type
		return '%s (%s)' % (self.type, ', '.join(options))
 
	def firstword(self):
		"""Returns first word of the event's message"""
		return self.message.split(' ')[0]
 
	def arguments(self):
		"""Returns second and following words of the event's message or empty string"""
		return ' '.join(self.message.split(' ')[1:])
 
class User(object):
	"""User on IRC"""
	@staticmethod
	def fromraw(rawname):
		"""Creates a new user from a given raw string nick!ident@host"""
		nick, ident, host = RE_USER.findall(rawname)[0]
		return User(nick, ident, host)
 
	def __init__(self, nick, ident, host):
		"""Creates a new user"""
		self.nick, self.ident, self.host = nick, ident, host
 
	def __str__(self):
		"""Returns nickname"""
		return self.nick
 
	def raw(self):
		"""Returns raw representation nick!ident@host"""
		return "%s!%s@%s" % (self.nick, self.ident, self.host)
 
 
if __name__ == '__main__':
	bot = Bot("irc.freenode.org", 6667, "Steak", "ircbot", "Hachier", ['#escalope'])
	while bot.online:
		try: bot.run()
		except KeyboardInterrupt: bot.quit()
 
