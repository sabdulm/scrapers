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
import re

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


def downloading_meta_info(appId, url):
	print(appId, url)
	scraper = cfscrape.create_scraper()
	resp = scraper.get(url)
	soup = bs(resp.content, 'html.parser')

	data = soup.find('div', class_ = 'table topmargin variants-table')
	dp_url_divs = data.find_all('div', class_='table-cell rowheight addseparator expand pad dowrap')
	url_div = dp_url_divs[0].find('a')
	nextpage_url = base_URL + url_div.get('href')[1:]
	appversion = soup.find('h1', class_="marginZero wrapText app-title fontBlack noHover").text.lower()

	# print(nextpage_url)

	resp = scraper.get(nextpage_url)
	soup = bs(resp.content, 'html.parser')
	data = soup.find('div', class_= 'noPadding col-md-6 col-sm-6 col-xs-12')
	apkDetailsTable = data.find('div', class_='apk-detail-table')
	
	rows =  apkDetailsTable.find_all('div', class_='appspec-row')
	apkDetail = {}
	apkDetail['version'] = appversion
	size = rows[1].text
	apkDetail['size'] = int(re.sub(r"\D", "", size.replace('\n', '').split('(')[1]))
	apkDetail['os_detail'] = rows[2].text.replace('\n', '')
	apkDetail['screen_detail'] = rows[3].text.replace('\n', '')
	apkDetail['date_published'] = rows[len(rows)-1].text.replace('\n', '')
	return apkDetail

	# apk_verion_list.append(apkDetail)




def getLinks(url, proxylist):
	links = []
	while True:
		random.shuffle(proxylist)
		proxy = proxylist[0]

		proxies = None
		if ( proxy[3] in "yes"):
			proxies = {"http": "{0}://{1}:{2}".format("http", proxy[0], proxy[1])}

		elif(proxy[2] in "yes"):
			proxies = {"https": "{0}://{1}:{2}".format("https", proxy[0], proxy[1])}

		_ = proxies
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

	for appId in appIds:
		print("Starting ", appId)

		apk_url = base_URL+search_URL+appId
		links = getLinks(apk_url, proxies)

		if len(links) == 0:
			with open('notFound', 'a') as f:
				f.write(appId + '\n')
			continue
		lst_apk_details = []
		for url in links:
			# print("app:{} , url: {}".format(appId, url))
			apkDetail = downloading_meta_info(appId, url)
			lst_apk_details.append(list(apkDetail.values()))

		df = pd.DataFrame(lst_apk_details, columns = ['version', 'size', 'os_detail', 'screen_detail', 'date_published'])
		df.to_csv('apk_files/{}.csv'.format(appId), index=False)
		
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
