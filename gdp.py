from bs4 import BeautifulSoup
import unittest
import requests
import sqlite3
import json
import os
from datetime import datetime, timedelta

'''
1. pull cases from each day for 100 days (USA)
2. Total Cases until now (100 countries) vs. GDP
'''
def readDataFromFile(filename):
    full_path = os.path.join(os.path.dirname(__file__), filename)
    f = open(full_path, encoding='utf-8')
    file_data = f.read()
    f.close()  
    json_data = json.loads(file_data)
    return json_data

def setUpDatabase(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn

def setUpGDPTable(cur, conn):
    cur.execute('CREATE TABLE IF NOT EXISTS GDP (country TEXT, current INTEGER, previous INTEGER, date CHAR(6))')
    all_data = get_data()
    country_list = []
    GDP_list = []
    previous_GDP_list = []
    date_list = []
    n = 0
    x = 25
    for i in range(len(all_data[n:x])):
        data = all_data[i]
        country = data[0]
        country_list.append(country)
        GDP = data[1]
        GDP_list.append(GDP)
        previous_GDP = data[2]
        previous_GDP_list.append(previous_GDP)
        date = data[3]
        date_list.append(date)
        cur.execute('INSERT INTO GDP (country, current, previous, date) VALUES (?, ?, ?, ?)', (country, GDP, previous_GDP, date,))
        n += 25
        x += 25

    conn.commit()

# 

    # n = 25
    # x = 0
    # for i in range(5):
    #     specific_date = datetime(2020, 8, 1)
    #     start_date1 = specific_date + timedelta(x)
    #     startpoint = (str((start_date1)).split()[0])
    #     new_date = specific_date + timedelta(n)
    #     endpoint = (str((new_date)).split()[0])
    #     functionData = get_data(startpoint, endpoint)
        
    #     for i in functionData:
    #         cur.execute('INSERT INTO GDP Growth (country, current, previous, date) VALUES (?, ?, ?, ?)', (i[0], i[1]))
    #     n += 25
    #     x += 25

    # functionData1 = get_data('2020-08-26', '2020-09-20')
    # for i in functionData1:
    #     cur.execute('INSERT INTO Cases (Date, Cases) VALUES (?, ?)', (i[0], i[1]))
    # functionData2 = get_data('2020-09-21', '2020-10-16')
    # for i in functionData2:
    #     cur.execute('INSERT INTO Cases (Date, Cases) VALUES (?, ?)', (i[0], i[1]))


#class dayCase:

    #def __init__(self, start_date, end_date):
    #    self.start_date = start_date
    #    self.end_date = end_date

def get_data():
    # url = 'https://data.worldbank.org/indicator/NY.GDP.MKTP.KD.ZG'
    url = 'https://tradingeconomics.com/country-list/gdp'
    all_data = []
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
        previous = country_data[2]
        update_month = country_data[3]
        all_data.append((country, current, previous, update_month))
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
        previous = country_data[2]
        update_month = country_data[3]
        all_data.append((country, current, previous, update_month))
    return all_data



def main():
    # USA_cases = dayCase('2020-08-01', '2020-12-01')
    # USA_cases.create_request_url()
    # USA_cases.get_data()
    # create_request_url('2020-08-01', '2020-12-01')
    # get_data('2020-08-01', '2020-12-01')
    get_data()
    cur, conn = setUpDatabase('Covid_Cases_USA.db')
    setUpGDPTable(cur, conn)

    conn.close()
    # json_data = readDataFromFile('yelp_data.txt')
    # setUpCategoriesTable(json_data, cur, conn)
    

if __name__ == "__main__":
	main()