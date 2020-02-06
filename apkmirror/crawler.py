from threading import Thread
import requests
from math import ceil
from bs4 import BeautifulSoup as bs
import urllib3
import cfscrape
import queue
import cfscrape
from fake_useragent import UserAgent
import os
import csv
import datetime
import json
import pandas as pd
import random
import sys

base_URL = "https://www.apkmirror.com/"
search_URL = "?post_type=app_release&searchtype=apk&s="

def fetch_proxies():
	proxies = []
	PROXY_URLS = ["https://free-proxy-list.net/"]
	for url in PROXY_URLS:
		success = False
		while not success:
			try:
				page = requests.get(url)
				soup = bs(page.content, "html.parser")
				for row in soup.findAll('table')[0].tbody.findAll('tr'):
					columns = row.findAll('td')
					ip = columns[0].contents[0]
					#print (ip)
					port = columns[1].contents[0]
					#print (port)
					protocol = columns[5].contents[0].lower()
					protocol1 = columns[6].contents[0].lower()

					#print (protocol)
					proxies.append((ip, port, protocol,protocol1))
				success = True
				if(os.path.exists('../record.csv') == False):
					with open('../record.csv','w') as csv_file:
						csv_writer = csv.writer(csv_file,delimiter=',')
						csv_writer.writerow(["Source","Time"])
				with open('../record.csv','a') as csv_file:
					csv_writer = csv.writer(csv_file,delimiter=',')
					csv_writer.writerow(["BR",str(datetime.datetime.now())])

			except Exception as ex:
				print(ex)
				print('Cannot get proxy')
				success = False
				exit()
	filtered_proxies = [p for p in proxies if (p[2] in "yes") or (p[3] in "yes") ]
	return filtered_proxies




def give_apkURL(apk_name, proxylist):
	random.shuffle(proxylist)
	proxy = proxylist[0]

	proxies = None
	if ( proxy[3] in "yes"):
		proxies = {"http": "{0}://{1}:{2}".format("http", proxy[0], proxy[1])}

	elif(proxy[2] in "yes"):
		proxies = {"https": "{0}://{1}:{2}".format("https", proxy[0], proxy[1])}

	# print(proxies)

	# scraper = cfscrape.create_scraper()
	# print(base_URL+search_URL+apk_name, 'https://www.apkmirror.com/?post_type=app_release&searchtype=apk&s=com.ftt.gbworld.aos')
	r = requests.get(base_URL+search_URL+apk_name, proxies= proxies, timeout = 60)
	soup = bs(r.text, 'html.parser')
	for data in soup.find_all('div', id='content', class_='col-md-8 content-area search-area', role = 'main'):
		for div in data.find_all('div', class_='appRow'):
			for div2 in div.find_all('div', class_='table-cell'):	
				for a in div2.find_all('a'):
				    return (a.get('href'))


def give_VersionsPageLinks(apk_url, proxylist):
	random.shuffle(proxylist)
	proxy = proxylist[0]

	proxies = None
	if ( proxy[3] in "yes"):
		proxies = {"http": "{0}://{1}:{2}".format("http", proxy[0], proxy[1])}

	elif(proxy[2] in "yes"):
		proxies = {"https": "{0}://{1}:{2}".format("https", proxy[0], proxy[1])}

	
	# scraper = cfscrape.create_scraper()
	r = requests.get(base_URL+apk_url[1:], proxies= proxies ,timeout=60)
	soup = bs(r.text, 'html.parser')

	see_moreLink = ''
	flag = False
	for data in soup.find_all('div', id='content', class_="col-md-8 content-area", role="main"):
		for div in data.find_all('div', class_='listWidget'):
			for div2 in div.find_all('div', class_='table-cell center'):	
				for a in div2.find_all('a'):
				    see_moreLink = a.get('href')
				    flag = True
				    break
				if(flag):
					break   
			if(flag):
				break
		if(flag):
			break	


	return see_moreLink	

def give_maxPage(see_more, proxylist):
	random.shuffle(proxylist)
	proxy = proxylist[0]

	proxies = None
	if ( proxy[3] in "yes"):
		proxies = {"http": "{0}://{1}:{2}".format("http", proxy[0], proxy[1])}

	elif(proxy[2] in "yes"):
		proxies = {"https": "{0}://{1}:{2}".format("https", proxy[0], proxy[1])}

	# scraper = cfscrape.create_scraper()
	r = requests.get(base_URL+see_more[1:], proxies=proxies, timeout=60)
	soup = bs(r.content, 'html.parser')
	flag = False

	tot_page = ''
	for data in soup.find_all('div', id='primary', class_='col-md-8 content-area', role="main"):
		for div in data.find_all('div', class_='listWidget'):
			for div2 in div.find_all('div', class_='pagination desktop'):	
				for a in div2.find_all('a', class_="last"):
				    tot_page = a.get('href')
				    flag = True
				    break
				if(flag):
					break   
			if(flag):
				break
		if(flag):
			break	
	
	return tot_page
	

def get_version_apk_link(post_url, proxylist):
	links = []

	count = 1
	while True:
		random.shuffle(proxylist)
		proxy = proxylist[0]

		proxies = None
		if ( proxy[3] in "yes"):
			proxies = {"http": "{0}://{1}:{2}".format("http", proxy[0], proxy[1])}

		elif(proxy[2] in "yes"):
			proxies = {"https": "{0}://{1}:{2}".format("https", proxy[0], proxy[1])}

		count = count + 1
		url = base_URL + post_url[1:]
		#scraper = cfscrape.create_scraper()
		req = requests.get(url, proxies=proxies, timeout=60)
		
		soup = bs(req.content, 'html.parser')

		data = soup.find('div', id='primary', class_='col-md-8 content-area', role = 'main')
		for div in  data.find_all('div', class_='appRow'):
			for div2 in div.find_all('div', class_='downloadIconPositioning'):	
				a = div2.find('a')

				appTitle = div.find('h5', class_="appRowTitle wrapText marginZero block-on-mobile").text.lower()
				alphaBetaCheck = 'alpha' in appTitle  or 'beta' in appTitle 


				if not alphaBetaCheck:
					links.append(base_URL + a.get('href')[1:])

			
		next_div = data.find('div', class_='wp-pagenavi', role='navigation')
		if next_div == None:
			return links
		next_div = next_div.find('a', class_='nextpostslink', rel='next')
		if next_div == None:
			return links
			
		post_url = next_div.get('href')
		
	return links


def get_download_page_links(url, proxylist):
	random.shuffle(proxylist)
	proxy = proxylist[0]

	proxies = None
	if ( proxy[3] in "yes"):
		proxies = {"http": "{0}://{1}:{2}".format("http", proxy[0], proxy[1])}

	elif(proxy[2] in "yes"):
		proxies = {"https": "{0}://{1}:{2}".format("https", proxy[0], proxy[1])}

#	scraper = cfscrape.create_scraper()
	req = requests.get(url, proxies=proxies, timeout=60)
	soup = bs(req.content, 'html.parser')
	data = soup.find('div', id = 'content', class_= 'col-md-8 content-area', role='main')

	try:
		apkTableLinks = data.find('div', class_='table topmargin variants-table').find_all('a')
		downloadlinks = [base_URL + link.get('href')[1:] for link in apkTableLinks]
	
		appversion = soup.find('h1', class_="marginZero wrapText app-title fontBlack noHover").text

	
		return appversion, downloadlinks
	except:
		return "NULL", "NULL"

def get_apk_version_info(links, appversion, appID, proxylist):
	# print("get apk get_apk_version_info")
	#scraper = cfscrape.create_scraper()
	apk_verion_list = []
	for url in links:
		random.shuffle(proxylist)
		proxy = proxylist[0]

		proxies = None
		if ( proxy[3] in "yes"):
			proxies = {"http": "{0}://{1}:{2}".format("http", proxy[0], proxy[1])}

		elif(proxy[2] in "yes"):
			proxies = {"https": "{0}://{1}:{2}".format("https", proxy[0], proxy[1])}


		req = requests.get(url, proxies=proxies, timeout=60)
		soup = bs(req.content, 'html.parser')
		data = soup.find('div', id = 'content', class_= 'col-md-8 content-area', role='main')
		apkDetailsTable = data.find('div', class_='apk-detail-table')
		downloadLink = base_URL +  data.find('a', class_="btn btn-flat downloadButton").get('href')[1:]

		rows =  apkDetailsTable.find_all('div', class_='appspec-row')
		apkDetail = {}
		apkDetail['download-link'] = downloadLink
		apkDetail['version-detail'] = rows[0].text
		apkDetail['size'] = rows[1].text
		apkDetail['os-detail'] = rows[2].text
		apkDetail['screen-detail'] = rows[3].text
		apkDetail['date-published'] = rows[len(rows)-1].text

		apk_verion_list.append(apkDetail)

	try:
		os.makedirs(os.path.dirname('apk_files/'+appID + '/'+ appversion.replace(' ','_') + '.json'))	
		with open('apk_files/'+appID + '/'+ appversion.replace(' ','_') + '.json', 'w') as outfile:
			json.dump({'apkvariants': apk_verion_list, 'appID':appID, 'appVersion':appversion}, outfile)
	
	except :
		with open('apk_files/'+appID + '/'+ appversion.replace(' ','_') + '.json', 'w') as outfile:
			json.dump({'apkvariants': apk_verion_list, 'appID':appID, 'appVersion':appversion}, outfile)





# END OF FUNCTIONS, MAIN CODE BELOW THIS LINE

# Starting from here

def getLinks(url, proxylist):
	links = []
	post_url = None
	while True:
		random.shuffle(proxylist)
		proxy = proxylist[0]

		proxies = None
		if ( proxy[3] in "yes"):
			proxies = {"http": "{0}://{1}:{2}".format("http", proxy[0], proxy[1])}

		elif(proxy[2] in "yes"):
			proxies = {"https": "{0}://{1}:{2}".format("https", proxy[0], proxy[1])}

		# url = base_URL + post_url[1:]
		scraper = cfscrape.create_scraper()
		print('url: {}'.format(url))
		req = scraper.get(url)
		# print(req.content)
		# break
		soup = bs(req.content, 'html.parser')
		data = soup.find('div', id='content', class_='col-md-8 content-area search-area', role = 'main')
		# print(data)
		data = data.find_all('div', class_='appRow')
		for div in  data:
			for div2 in div.find_all('div', class_='downloadIconPositioning'):	
				a = div2.find('a')

				appTitle = div.find('h5', class_="appRowTitle wrapText marginZero block-on-mobile").text.lower()
				alphaBetaCheck = 'alpha' in appTitle  or 'beta' in appTitle 


				if not alphaBetaCheck:
					links.append(base_URL + a.get('href')[1:])

			
		next_div = soup.find('div', class_='pagination desktop')
		url_div = next_div.find('a')
		
		if 'next' not in url_div.text.lower():
			break

		url = base_URL + url_div.get('href')
		
	return links


def process_batch(appIds, proxies):

	for appId in appIds[:1]:
		print("Starting ", appId)

		apk_url = base_URL+search_URL+appId


		links = getLinks(apk_url, proxies)
		# print(links)
		# print(len(links))
		# return
		try:
			os.mkdir('apk_files/'+appId+'/')
		except:
			pass

		for url in links:
			print("app:{} , url: {}".format(appId, url))
			appversion, downloadPageLinks = get_download_page_links(url, proxies)

			if(appversion == "NULL" or downloadPageLinks == "NULL"):
				print('passing')
			else:
				get_apk_version_info(downloadPageLinks, appversion, appId, proxies)

		with open('log', 'a') as f:
			f.write(appId + '\n')
		print("Done ", appId)



def main():
	if len(sys.argv) != 2:
		print('Usage: python crawler.py <appslist.txt>')
		return
	fname = sys.argv[1]
	list_apps = None
	with open(fname, 'r') as f:
		list_apps = f.read().split('\n')



	while True:
		log = None
		with open('log', 'r') as f:
			log = f.read().split('\n')
				
		appIds = list(filter(lambda x: x not in log, list_apps))

		print("Apps left: ", len(appIds))


		THREAD_COUNT = 1
		BATCH_SIZE = ceil(len(appIds) / THREAD_COUNT)

		print(THREAD_COUNT, BATCH_SIZE)

		threads = []
		for i in range(THREAD_COUNT):
			proxies = fetch_proxies()
			
			t = Thread(target=process_batch, args=(appIds[i * BATCH_SIZE:i * BATCH_SIZE + BATCH_SIZE],proxies, ))
			t.start()
			threads.append(t)

		for t in threads:
			t.join()
			print("thread joined!")
		break
main()