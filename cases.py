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

#cases

# I dont know if we need this function
# def readDataFromFile(filename):
#     full_path = os.path.join(os.path.dirname(__file__), filename)
#     f = open(full_path, encoding='utf-8')
#     file_data = f.read()
#     f.close()  
#     json_data = json.loads(file_data)
#     return json_data

def setUpDatabase(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn

def setUpCasesTable(cur, conn):
    cur.execute('CREATE TABLE IF NOT EXISTS Cases (Date CHAR(10), Cases INTEGER)')
    all_cases = get_data('2020-08-01', '2020-12-01')
    n = 0
    x = 25
    cur.execute('SELECT Date FROM Cases ORDER BY Date DESC LIMIT 1')
    try:
        last_entry = cur.fetchone()[0]
        for index in range(len(all_cases)):
            if all_cases[index][0] == last_entry:
                n = index + 1
                x = n + 25
    except:
        last_entry = 0

    for i in range(len(all_cases[n:x])):
        data = all_cases[n + i]
        date = data[0]
        cases = data[1]
        cur.execute('INSERT INTO Cases(Date, Cases) VALUES (?,?)', (date, cases))
    conn.commit()

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
    #         cur.execute('INSERT INTO Cases (Date, Cases) VALUES (?, ?)', (i[0], i[1]))
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
def setUpTotalCasesTable(cur, conn):
    cur.execute('CREATE TABLE IF NOT EXISTS CountryData (Country_ID INTEGER, Cases INTEGER, Recovered INTEGER, Population INTEGER)')
    all_data = country_data(cur, conn)
    n = 0
    x = 25
    cur.execute('SELECT Country_ID FROM CountryData ORDER BY Country_ID DESC LIMIT 1')
    try:
        last_entry = cur.fetchone()[0]
        for index in range(len(all_data)):
            if all_data[index][0] == last_entry:
                n = index + 1
                x = n + 25
    except:
        last_entry = 0

    for i in range(len(all_data[n:x])):
        data = all_data[n + i]
        ids = data[0]
        cases = data[1]
        recovered = data[2]
        population = data[3]
        cur.execute('INSERT INTO CountryData (Country_ID, Cases, Recovered , Population ) VALUES (?,?,?,?)', (ids, cases, recovered, population))
    conn.commit()

def get_data(start_date, end_date):
    request_url = f'https://covidtrackerapi.bsg.ox.ac.uk/api/v2/stringency/date-range/{start_date}/{end_date}'
    request = requests.get(request_url)
    jsons = json.loads(request.text)
    data = jsons.get('data')
    dateCases = []
    for date in data:
        USA = data[date].get('USA')
        if USA is None:
            continue
        else:
            cases = USA.get('confirmed')
            dateCases.append((date, cases))
    return dateCases

def country_data(cur, conn):
    cur.execute('SELECT Country_ID, Country FROM GDP')
    id_name = cur.fetchall()
    per_country = []
    
    url = 'https://covid-api.mmediagroup.fr/v1/cases'
    request = requests.get(url)
    jsons = json.loads(request.text)
    for country in jsons:
        for name in id_name:
            if country == 'US':
                country = 'United States'
            if country == 'Taiwan*':
                country = 'Taiwan'
            if country == name[1]:
                country_id = name[0]
                if country == 'United States':
                    country = 'US'
                if country == 'Taiwan':
                    country = 'Taiwan*'
                data = jsons[country].get('All')
                confirmed = data.get('confirmed')
                recovered = data.get('recovered')
                population = data.get('population')
                per_country.append((country_id, confirmed, recovered, population))
    return per_country


def main():
    # USA_cases = dayCase('2020-08-01', '2020-12-01')
    # USA_cases.create_request_url()
    # USA_cases.get_data()
    get_data('2020-08-01', '2020-12-01')
    cur, conn = setUpDatabase('Covid_Cases_USA.db')
    setUpCasesTable(cur, conn)
    setUpTotalCasesTable(cur, conn)
    conn.close()
    # json_data = readDataFromFile('yelp_data.txt')
    # setUpCategoriesTable(json_data, cur, conn)
    

if __name__ == "__main__":
	main()