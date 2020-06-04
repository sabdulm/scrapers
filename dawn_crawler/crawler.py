from bs4 import BeautifulSoup
import requests
import os
from math import ceil
from threading import Thread
import json
import sys
from tqdm import tqdm
import urllib3
import random
import time
import queue
import cfscrape
from fake_useragent import UserAgent
import os
import csv
import datetime

global global_ua

proxy_queue = queue.Queue()
errpage = []


def fetch_proxies():
	scraper = cfscrape.create_scraper()
	proxies = []
	PROXY_URLS = ["https://free-proxy-list.net/"]
	for url in PROXY_URLS:
		success = False
		while not success:
			try:
				page = requests.get(url)
				soup = BeautifulSoup(page.content, "html.parser")
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


def refresh_proxy_queue():
	proxies = fetch_proxies()
	#print (proxies);
	for proxy in proxies:
		proxy_queue.put(proxy)








log_file = open('log', 'a')

def log(msg):
	# print(msg)
	log_file.write(msg + '\n')


not_found = []

def parse_soup(soup):
	story = {}
	story['title'] = soup.find('h2', attrs={'class':'story__title'}).text.strip()
	story['body'] = soup.find('div', attrs={'class':'story__content'}).text.strip()
	story['author'] = soup.find('span', attrs={'class':'story__byline'}).text.strip()
	story['pub_date'] = soup.find('span', attrs={'class':'story__time'}).text.strip()
	return story


def soupify(url, proxies):
	global not_found
	page = requests.get(url, proxies = proxies, timeout= 100 )

	if page.status_code == 200:
		soup = BeautifulSoup(page.content, 'html.parser')
	else:
		if page.status_code == 404:
			not_found.append(url)
		raise Exception(str(page.status_code))			

	return soup

def process(url, proxies):
	soup = soupify(url, proxies)
	story = parse_soup(soup)
	story['url'] = url
	return story

def process_batch(urls, proxylist):
	for i in range(len(urls)):

		url = urls[i]


		name = url[url.rindex('/')+1:]
		fname = 'stories/' + name
				

		if os.path.isfile(fname):
			log('in file ' + name)
			continue

		
		proxy = proxylist[i%(len(proxylist))]

		if ( proxy[3] in "yes"):
			proxies = {"http": "{0}://{1}:{2}".format("http", proxy[0], proxy[1])}

		elif(proxy[2] in "yes"):
			proxies = {"https": "{0}://{1}:{2}".format("https", proxy[0], proxy[1])}


		try:
			story = process(url, proxies)
			open(fname, 'w').write(json.dumps(story))
			log("success " + name)
			print(datetime.datetime.now(),name, "done!")
		except Exception as e:
			log("failed " + name +" "+ str(e))




# urls = open('t-collect-urls').read().split('\n')




while True:
	urls = open('t-collect-urls').read().split('\n')
	urls_done = os.listdir('stories/')
	print(len(urls_done), 'crawled')
	urls = set(urls)
	urls_done = set(urls_done)

	urls = list(urls.difference(urls_done))

	print(str(len(urls)) + " to be crawled" )

	urls = (set(urls).difference(not_found))
	print(str(len(urls)) + " to be crawled" )

	urls = list(map(lambda x : 'https://dawn.com/news/'+x, urls))
	random.shuffle(urls)


	THREAD_COUNT = 4
	BATCH_SIZE = ceil(len(urls) / THREAD_COUNT)

	print(THREAD_COUNT, BATCH_SIZE)

	proxylist = fetch_proxies()

	threads = []
	print("Number of URLS not found: ", len(not_found))
	not_found = []
	for i in range(THREAD_COUNT):
		t = Thread(target=process_batch, args=(urls[i * BATCH_SIZE:i * BATCH_SIZE + BATCH_SIZE],proxylist, ))
		t.start()
		threads.append(t)

	for t in threads:
		t.join()
		print("thread joined!")
