from bs4 import BeautifulSoup
import unittest
import requests
import sqlite3
import json
import os
from datetime import datetime, timedelta

def setUpDatabase(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn

def setUpGDPTable(cur, conn):
    cur.execute('CREATE TABLE IF NOT EXISTS GDP (id INTEGER, country TEXT, current INTEGER, previous INTEGER, date CHAR(6))')
    all_data = get_data()
    n = 0
    x = 25
    cur.execute('SELECT id FROM GDP ORDER BY id DESC LIMIT 1')
    try:
        last_entry = cur.fetchone()[0]
        for a in all_data:
            if a[0] == last_entry:
                n = last_entry + 1
                x = n + 25
    except:
        last_entry = 0
    for i in range(len(all_data[n:x])):
        data = all_data[n + i]
        country_id = data[0]
        country = data[1]
        GDP = data[2]
        previous_GDP = data[3]
        date = data[4]
        cur.execute('INSERT INTO GDP (id, country, current, previous, date) VALUES (?,?, ?, ?, ?)', (country_id, country, GDP, previous_GDP, date,))
    conn.commit()

def get_data():
    url = 'https://tradingeconomics.com/country-list/gdp'
    all_data = []
    request = requests.get(url)
    soup = BeautifulSoup(request.text, 'html.parser') 
    table = soup.find('div', class_='table-responsive')
    rows = table.find_all('tr', class_='datatable-row')
    number = 0
    for row in rows:
        datas = row.find_all('td')
        country_data = []
        for data in datas:
            num = data.text
            stripped = num.strip()
            country_data.append(stripped)
        country_id = number
        country = country_data[0]
        current = country_data[1]
        previous = country_data[2]
        update_month = country_data[3]
        all_data.append((country_id, country, current, previous, update_month))
        number = number + 1
    rows = table.find_all('tr', class_='datatable-row-alternating') 
    for row in rows:
        datas = row.find_all('td')
        country_data = []
        for data in datas:
            num = data.text
            stripped = num.strip()
            country_data.append(stripped)
        country_id = number
        country = country_data[0]
        current = country_data[1]
        previous = country_data[2]
        update_month = country_data[3]
        all_data.append((country_id, country, current, previous, update_month))
        number = number + 1
    return all_data



def main():

    cur, conn = setUpDatabase('Covid_Cases_USA.db')
    setUpGDPTable(cur, conn)

    conn.close()
    

if __name__ == "__main__":
	main()