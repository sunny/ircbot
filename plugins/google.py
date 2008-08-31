import _google as google
google.setLicense('YOUR_GOOGLE_LICENCE')
 
def googlesearch(bot, event):
	"""Return first google search queries"""
	if not event.message.startswith('!google'): return
 
	msg = event.message.split(' ')[1:]
 
	if len(msg) == 0:
		bot.msg(event.channel, "http://google.com")
		return
 
	txt = ' '.join(msg)
	data = google.doGoogleSearch(q=txt, maxResults=3, language='fr')
	for result in data.results:
		try: result.title = result.title.decode('utf-8', 'replace')
		except UnicodeEncodeError, e:
			print e
			continue
		result.title = result.title.replace('<b>', '\x02').replace('</b>', '\x02')
		bot.msg(event.channel, result.title)
		bot.msg(event.channel, '    ' + result.URL)
 
rules = {googlesearch: 'msg'}
 
