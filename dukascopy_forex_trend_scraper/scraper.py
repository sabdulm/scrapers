#!/usr/bin/python3

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
import time
from bs4 import BeautifulSoup
import re
import dominate
from dominate.tags import table, tr, td, th, img, span
import os
import datetime


start_url = "https://www.dukascopy.com/swiss/english/marketwatch/sentiment/"
xpath_iframe_lp = '//*[@id="main-center-col"]/div/p[12]/iframe'
xpath_lp = "//*[text()='Liquidity providers']"
currencies_needed = [
    'AUD/CAD', 'AUD/CHF', 'AUD/JPY', 'AUD/NZD', 'AUD/USD', 'CAD/CHF', 'CAD/JPY', 'CHF/JPY', 'EUR/AUD', 'EUR/CAD', 'EUR/CHF', 'EUR/GBP', 'EUR/JPY', 'EUR/NZD', 'EUR/USD', 'GBP/AUD', 'GBP/CAD', 'GBP/CHF', 'GBP/JPY', 'GBP/NZD', 'GBP/USD', 'NZD/CAD', 'NZD/CHF', 'NZD/JPY', 'NZD/USD', 'USD/CAD', 'USD/CHF', 'USD/JPY', 'XAG/USD', 'XAU/USD']


def get_html_from_site():
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)

    try:
        driver.get(start_url)

        iframe = driver.find_element_by_xpath(xpath_iframe_lp)  # switch to it
        driver.switch_to.frame(iframe)

        liquidity_providers = driver.find_element_by_xpath(xpath_lp)
        liquidity_providers.click()

        table = driver.find_elements_by_class_name("L-M-eb-ib")

        htmlstring = ""
        for row in table:
            htmlCode = row.get_attribute("outerHTML")
            htmlstring += htmlCode

        driver.switch_to.default_content()
    finally:
        driver.quit()

    return htmlstring


def convert_str_float(arr):
    result = []
    for i in arr:
        i = re.sub(r'[^\x00-\x7F]+', '-', i)
        result.append(float(i))
    return result


def clean_html(htmlstring):
    result = {}
    soup = BeautifulSoup(htmlstring, 'html.parser')

    # currencies
    currencies = soup.find_all('td', class_='L-Wb-kb-Yb')
    currencies = [i.text.strip() for i in currencies]

    # last updates
    lastUpdates = soup.find_all('td', class_="L-Wb-kb-Zb")
    lastUpdates = [i.text.strip().replace(' %', '') for i in lastUpdates]
    lastUpdates = convert_str_float(lastUpdates)
    # 6hours ago
    sixHrUpdates = soup.find_all('td', class_="L-Wb-kb-ac-bc")
    sixHrUpdates = [i.text.strip().replace(' %', '') for i in sixHrUpdates]
    sixHrUpdates = convert_str_float(sixHrUpdates)
    # 1 day ago
    oneDayUpdates = soup.find_all('td', class_="L-Wb-kb-cc-dc")
    oneDayUpdates = [i.text.strip().replace(' %', '') for i in oneDayUpdates]
    oneDayUpdates = convert_str_float(oneDayUpdates)

    numCurrencies = len(currencies)

    for i in range(numCurrencies):
        if currencies[i] in currencies_needed:
            # result[currencies[i]] = [lastUpdates[i], sixHrUpdates[i]]
            result[currencies[i]] = [lastUpdates[i],
                                     sixHrUpdates[i], oneDayUpdates[i]]

    return result


def process_data(data):
    result_vip = {}
    result_prem = {}
    for key in data.keys():
        [lu, su, _] = data[key]
        if 0 in data[key]:
            result_prem[key] = 0
        elif (lu < su) and (lu > 0 and su > 0):
            result_prem[key] = 1
        elif (lu < su) and (lu < 0 and su < 0):
            result_prem[key] = -1
        else:
            result_prem[key] = 0

    for key in data.keys():
        [lu, su, ou] = data[key]
        if 0 in data[key]:
            result_vip[key] = 0
        elif (lu < su and su < ou) and (lu > 0 and su > 0 and ou > 0):
            result_vip[key] = 1
        elif (lu < su and su < ou) and (lu < 0 and su < 0 and ou < 0):
            result_vip[key] = -1
        else:
            result_vip[key] = 0
    print(result_prem, result_vip)
    return result_prem, result_vip


def create_html(prem, vip):
    keys = list(prem.keys())
    keys.sort()

    prem_table = table(style='border: 1px solid black')
    prem_table += tr(th("Currency"), th("Buy"), th("Sell"), th("Hold"))
    for key in keys:

        # hold
        if prem[key] == 0:
            prem_table += tr(td(key), td(" "), td(" "), td("Hold"))

            # buy
        elif prem[key] == 1:
            prem_table += tr(td(key), td("Buy"),
                             td(" "), td(" "))

            # sell
        else:
            prem_table += tr(td(key), td(" "), td("Sell"),
                             td(" "))

    with open('prem_table.html', 'w') as f:
        f.write(prem_table.render())

    keys_vip = list(vip.keys())
    keys_vip.sort()

    vip_table = table(style='border: 1px solid black')
    vip_table += tr(th("Currency"), th("Buy"), th("Sell"), th("Hold"))
    for key in keys_vip:

        # hold
        if vip[key] == 0:
            vip_table += tr(td(key), td(" "), td(" "), td("Hold"))

            # buy
        elif vip[key] == 1:
            vip_table += tr(td(key), td("Buy"),
                            td(" "), td(" "))

            # sell
        else:
            vip_table += tr(td(key), td(" "), td("Sell"),
                            td(" "))

    with open('vip_table.html', 'w') as f:
        f.write(vip_table.render())


def main():
    htmlstring = get_html_from_site()
    dict_data = clean_html(htmlstring)
    prem, vip = process_data(dict_data)
    create_html(prem, vip)
    print(datetime.datetime.now(), ' script ran')


main()
