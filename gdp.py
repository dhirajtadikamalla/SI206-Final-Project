from bs4 import BeautifulSoup
import unittest
import requests
import sqlite3
import json
import os
from datetime import datetime, timedelta

#run this first

def setUpDatabase(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn

def setUpGDPTable(cur, conn):
    cur.execute('CREATE TABLE IF NOT EXISTS GDP (Country_ID INTEGER, Country TEXT, GDP INTEGER)')
    countries = get_countries()
    gdps = get_data(cur, conn)
    n = 0
    x = 25
    cur.execute('SELECT Country_ID FROM GDP ORDER BY Country_ID DESC LIMIT 1')
    try:
        last_entry = cur.fetchone()[0]
        for index in range(len(countries)):
            if countries[index][0] == last_entry:
                n = index + 1
                x = n + 25
    except:
        last_entry = 0
    for i in range(len(countries[n:x])):
        id_list = countries[n + i]
        data = gdps[n + i]
        if id_list[1] == data[0]:
            country_id = id_list[0]
            country = data[0]
            GDP = data[1]
        cur.execute('INSERT INTO GDP (Country_ID, Country, GDP) VALUES (?,?, ?)', (country_id, country, GDP))
    conn.commit()

def get_countries():
    url = 'https://tradingeconomics.com/country-list/gdp'
    countries = []
    request = requests.get(url)
    soup = BeautifulSoup(request.text, 'html.parser') 
    table = soup.find('div', class_='table-responsive')
    rows = table.find_all('tr', class_='datatable-row')
    order = 1
    for row in rows:
        datas = row.find('td')
        country = datas.text.strip()
        countries.append((order, country))
        order += 2
    rows = table.find_all('tr', class_='datatable-row-alternating') 
    order = 2
    for row in rows:
        datas = row.find('td')
        country = datas.text.strip()
        countries.append((order, country))
        order += 2
    countries_list = sorted(countries)[:111]
    countries = []
    api = 'https://covid-api.mmediagroup.fr/v1/cases'
    request = requests.get(api)
    jsons = json.loads(request.text)
    for country in jsons:
        if country == 'US':
            country = 'United States'
        if country == 'Taiwan*':
            country = 'Taiwan'
        for tup in countries_list:
            if country == tup[1]:
                countries.append(country)
    countries = sorted(countries)
    country_id = 0
    id_name = []
    for name in countries:
        id_name.append((country_id, name))
        country_id += 1
    return id_name


def get_data(cur, conn):
    countries = get_countries()
    url = 'https://tradingeconomics.com/country-list/gdp'
    all_data = []
    country_gdp = []
    request = requests.get(url)
    soup = BeautifulSoup(request.text, 'html.parser') 
    table = soup.find('div', class_='table-responsive')
    rows = table.find_all('tr', class_='datatable-row')
    for row in rows:
        datas = row.find_all('td')
        country_data = []
        for data in datas:
            num = data.text
            stripped = num.strip()
            country_data.append(stripped)
        country = country_data[0]
        current = country_data[1]
        # previous = country_data[2]
        # update_month = country_data[3]
        for tup in countries:
            if country == tup[1]:
                all_data.append((country, current))
    rows = table.find_all('tr', class_='datatable-row-alternating') 
    for row in rows:
        datas = row.find_all('td')
        country_data = []
        for data in datas:
            num = data.text
            stripped = num.strip()
            country_data.append(stripped)
        country = country_data[0]
        current = country_data[1]
        # previous = country_data[2]
        # update_month = country_data[3]
        for tup in countries:
            if country == tup[1]:
                all_data.append((country, current))
    country_gdp = sorted(all_data)
    return country_gdp



def main():

    cur, conn = setUpDatabase('Covid_Cases_USA.db')
    setUpGDPTable(cur, conn)

    conn.close()
    

if __name__ == "__main__":
	main()