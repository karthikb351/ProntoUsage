from clint.arguments import Args 
from clint.textui import prompt, puts, colored, indent

import urllib2, cookielib, urllib, os, json

from BeautifulSoup import BeautifulSoup

BASE_URL="http://115.248.50.60"

def loginToPronto(username, password, debug):

	params = urllib.urlencode( { 
		'loginUserId': username,
		'authType': 'Pronto',
		'loginPassword': password,
		'submit': 'Login'
		})

	opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookielib.CookieJar()))
	urllib2.install_opener(opener)

	
	mainReq = urllib2.Request(BASE_URL+'/registration/Main.jsp?wispId=1&nasId=00:15:17:c8:09:b1')
	mainRes = urllib2.urlopen(mainReq)

	loginReq = urllib2.Request(BASE_URL+'/registration/chooseAuth.do',params)
	loginRes = urllib2.urlopen(loginReq)

	historyReq = urllib2.Request(BASE_URL+'/registration/main.do?content_key=%2FCustomerSessionHistory.jsp')
	historyRes = urllib2.urlopen(historyReq)

	soup = BeautifulSoup(historyRes.read())

	table = soup.find('td', attrs={
		"colspan": "3",
		"class": "subTextRight"
		}).parent

	tds=table.findAll('td')
	print "-"*40
	puts(colored.cyan(" "*17+"Usage"))
	print "-"*40
	puts(colored.magenta("Total Time: ")+ tds[1].text)
	puts(colored.magenta("Uploaded: ")+ tds[2].text)
	puts(colored.magenta("Downloaded: ")+ tds[3].text)
	puts(colored.magenta("Total Data: ")+ tds[4].text)
	print "-"*40


if __name__ == '__main__':


	debug= False
	args = Args().grouped
	if '--delete' in args.keys():
		try:
		    os.remove('cred.json')
		except OSError:
		    pass

	if os.path.isfile('cred.json'):
		with open('cred.json', 'r') as f:
			data=json.load(f)
			username=data['username']
			password=data['password']

	else:
		saved= False
		if '--debug' in args.keys():
			debug= True
		if '-u' in args.keys():
			username = args['-u'][0]
		else:
			username = prompt.query("username:")

		if '-p' in args.keys():
			password = args['-p'][0]
		else:
			password = prompt.query("password:")
		with open('cred.json', 'w') as f:
			f.write(json.dumps({
				'username': username,
				'password': password
				}, ensure_ascii=False))
			f.close()

	loginToPronto(username,password,debug)