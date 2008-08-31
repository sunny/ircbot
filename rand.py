import random
 
def rand(bot, event):
	if event.message.startswith('!rand'):
		args = event.message.split(' ')
		if len(args) == 1: limit = 10
		else: limit = args[1]
 
		try: limit = int(limit)
		except ValueError: pass
		else: bot.msg(event.channel, random.randint(0, limit))
 
rules = {rand: 'msg'}

