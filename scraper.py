import os, sys, time, random
import csv
from bs4 import BeautifulSoup
import urllib3
import xlsxwriter
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import random
import requests
import time
from datetime import datetime
import re
import sqlite3

'''
Setup a chromium engine headless browser
'''
def setup_browser() -> webdriver.Chrome:
    options = webdriver.ChromeOptions()
    options.add_argument("headless")
    options.add_argument("incognito")
    options.add_argument('disable-gpu') if os.name == 'nt' else None # Windows workaround
    options.add_experimental_option("detach", True)
    # options.add_argument("verbose")
    options.add_argument('ignore-certificate-errors')
    return webdriver.Chrome(ChromeDriverManager().install(), options=options)

def save_page(soup):
    with open("newsweb.html", "w") as file:
        file.write(str(soup))

def insert_data(conn, entry):
    sql = ''' INSERT INTO dividend_history(ticker,ex_date,dividends_paid,message)
        VALUES(?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, entry)
    conn.commit()

conn = sqlite3.connect('financial-database.db')

driver = setup_browser()

url = "https://newsweb.oslobors.no/search?category=1101&issuer=&fromDate=2012-01-01&toDate=2013-01-01&market=XOSL&messageTitle="

driver.get(url)
time.sleep(5)
soup = BeautifulSoup(driver.page_source, 'lxml')

#source = open("newsweb.html", "r")
#soup = BeautifulSoup(source.read(), 'lxml')

#soup = soup.select('#root > div > main > table')
soup.select("#root > div > main > table > tbody")
#print(soup.prettify())

table = soup.find('table')
table_rows = table.find_all('tr')

for tr in table_rows:
    td = tr.find_all('td')
    row = [i.text for i in td]
    if len(row) == 7:
        message = row[3].lower()
        if 'utbytte' in message and ('nok' in message or 'kr' in message):
            ex_date = datetime.strptime(row[0], '%d.%m.%Y %H:%M')
            ticker = row[2]

            dividends_paid = re.findall("\d+\.\d+", message) 
            if len(dividends_paid) == 0:
                dividends_paid = re.findall("\d+\,\d+", message)
            
            if not ex_date or not ticker or len(dividends_paid) > 0: 
                dividends_paid = dividends_paid[0].replace(',', '.')
                entry = (ticker, ex_date, dividends_paid, message)
                insert_data(conn, entry)