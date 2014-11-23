from clint.arguments import Args 
from clint.textui import prompt, puts, colored, indent
from datetime import datetime

import dateutil.relativedelta
import urllib2, cookielib, urllib, os, json

from BeautifulSoup import BeautifulSoup

BASE_URL="http://115.248.50.60"

def getCycleStartDate(planstart):
	today = datetime.now()
	month_ago = today - dateutil.relativedelta.relativedelta(months=1)
	if(planstart.day>today.day):
		return {
			"dd":planstart.day,
			"mm":month_ago.month-1,
			"yy":month_ago.year
		}
	else:
		return {
			"dd":planstart.day,
			"mm":today.month-1,
			"yy":today.year
		}



def loginToPronto(username, password, debug):

	params = urllib.urlencode( { 
		'loginUserId': username,
		'authType': 'Pronto',
		'loginPassword': password,
		'submit': 'Login'
		})

	opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookielib.CookieJar()))
	urllib2.install_opener(opener)
	puts(colored.white("Contacting ProntoNetworks..."))

	if debug:
		if not os.path.exists('debug/'):
			os.makedirs('debug/')

	with indent(5, quote=">"):
		puts(colored.yellow("Fetching site"))
	mainReq = urllib2.Request(BASE_URL+'/registration/Main.jsp?wispId=1&nasId=00:15:17:c8:09:b1')
	mainRes = urllib2.urlopen(mainReq)

	if debug:
		with open('debug/main.txt', 'wb') as f:
			f.write(mainRes.read())
			f.close()
			with indent(5, quote=colored.white("DEBUG:")):
				puts(colored.red("logged /registration/Main.jsp response"))

	with indent(5, quote=">"):
		puts(colored.yellow("Sending credentials"))
	loginReq = urllib2.Request(BASE_URL+'/registration/chooseAuth.do',params)
	loginRes = urllib2.urlopen(loginReq)

	if debug:
		with open('debug/login.txt', 'wb') as f:
			f.write(loginRes.read())
			f.close()
			with indent(5, quote=colored.white("DEBUG:")):
				puts(colored.red("logged /registration/chooseAuth.do response"))


	with indent(5, quote=">"):
		puts(colored.yellow("Checking plan"))
	planReq = urllib2.Request(BASE_URL+'/registration/main.do?content_key=%2FSelectedPlan.jsp')
	planRes = urllib2.urlopen(planReq)

	planSoup = BeautifulSoup(planRes.read())
	data=planSoup.findAll('td', attrs={
		'class': 'formFieldRight',
		'colspan': '2'
		})
	planDetails=[]
	for i in range(0,len(data)-1):
		kids = data[i].parent.findAll('td')
		planDetails.append(str(kids[1].text))

	if debug:
		with open('debug/plan.txt', 'wb') as f:
			f.write(loginRes.read())
			f.close()
			with indent(5, quote=colored.white("DEBUG:")):
				puts(colored.red("logged /registration/main.do?content_key=%2FSelectedPlan.jsp response"))

	startDate=datetime.strptime(planDetails[2], "%m/%d/%Y %H:%M:%S")
	endDate=datetime.strptime(planDetails[3], "%m/%d/%Y %H:%M:%S")

	cycleStart=getCycleStartDate(startDate)

	historyParams=urllib.urlencode({
		"location":"allLocations",
		"parameter":"custom",
		"customStartMonth":cycleStart['mm'],
		"customStartDay":cycleStart['dd'],
		"customStartYear":cycleStart['yy'],
		"customEndMonth":04,
		"customEndDay":01,
		"customEndYear":2016,# Lazy, so hardcoding end year.
		"button":"View"
	})

	with indent(5, quote=">"):
		puts(colored.yellow("Accessing history"))
	historyReq = urllib2.Request(BASE_URL+'/registration/customerSessionHistory.do', historyParams)
	historyRes = urllib2.urlopen(historyReq)

	html= historyRes.read()
	if debug:
		with open('debug/history.txt', 'wb') as f:
			f.write(html)
			f.close()
			with indent(5, quote=colored.white("DEBUG:")):
				puts(colored.red("logged /registration/customerSessionHistory.do response"))


	with indent(5, quote=">"):
		puts(colored.yellow("Parsing data"))
	historySoup = BeautifulSoup(html)
	table = historySoup.find('td', attrs={
		"colspan": "3",
		"class": "subTextRight"
		}).parent
	tds=table.findAll('td')


	

	print "-"*40
	puts(colored.cyan(" "*14+"Plan Details"))
	print "-"*40
	puts(colored.magenta("Data Limit: ")+ planDetails[0])
	puts(colored.magenta("Start Date: ")+ planDetails[2])
	puts(colored.magenta("End Date: ")+ planDetails[3])
	print "-"*40

	print "-"*40
	puts(colored.cyan(" "*17+"Usage"))
	print "-"*40
	puts(colored.magenta("Total Time: ")+ tds[1].text)
	puts(colored.magenta("Uploaded: ")+ tds[2].text)
	puts(colored.magenta("Downloaded: ")+ tds[3].text)
	puts(colored.magenta("Total Data: ")+ tds[4].text)
	print "-"*40


if __name__ == '__main__':
	print "-"*40
	puts(colored.white(" "*15+"ProntoUsage"))
	print "-"*40
	debug= False
	args = Args().grouped
	if '--debug' in args.keys():
		debug=True
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