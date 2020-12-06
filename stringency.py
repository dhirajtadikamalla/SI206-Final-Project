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

#stringency

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

def setUpCasesTable(cur, conn):
    cur.execute('CREATE TABLE IF NOT EXISTS Stringencies (Date CHAR(10), Stringencies INTEGER)')
    get_data('2020-08-01', '2020-08-25')
    n = 25
    x = 0
    for i in range(5):
        specific_date = datetime(2020, 8, 1)
        start_date1 = specific_date + timedelta(x)
        startpoint = (str((start_date1)).split()[0])
        new_date = specific_date + timedelta(n)
        endpoint = (str((new_date)).split()[0])
        functionData = get_data(startpoint, endpoint)
        for i in functionData:
            cur.execute('INSERT INTO Stringencies (Date, Stringencies) VALUES (?, ?)', (i[0], i[1]))
        n += 25
        x += 25

    # functionData1 = get_data('2020-08-26', '2020-09-20')
    # for i in functionData1:
    #     cur.execute('INSERT INTO Cases (Date, Cases) VALUES (?, ?)', (i[0], i[1]))
    # functionData2 = get_data('2020-09-21', '2020-10-16')
    # for i in functionData2:
    #     cur.execute('INSERT INTO Cases (Date, Cases) VALUES (?, ?)', (i[0], i[1]))


        
    conn.commit()


#class dayCase:

    #def __init__(self, start_date, end_date):
    #    self.start_date = start_date
    #    self.end_date = end_date
def create_request_url(start_date, end_date):
    url = f'https://covidtrackerapi.bsg.ox.ac.uk/api/v2/stringency/date-range/{start_date}/{end_date}'
    return url

def get_data(start_date, end_date):
    request_url = create_request_url(start_date, end_date)
    request = requests.get(request_url)
    jsons = json.loads(request.text)
    data = jsons.get('data')
    dateStringencies = []
    for date in data:
        USA = data[date].get('USA')
        if USA is None:
            continue
        else:
            stringencies = USA.get('stringency')
            dateStringencies.append((date, stringencies))
    return dateStringencies



def main():
    # USA_cases = dayCase('2020-08-01', '2020-12-01')
    # USA_cases.create_request_url()
    # USA_cases.get_data()
    create_request_url('2020-08-01', '2020-12-01')
    get_data('2020-08-01', '2020-12-01')
    cur, conn = setUpDatabase('Covid_Cases_USA.db')
    setUpCasesTable(cur, conn)

    conn.close()
    # json_data = readDataFromFile('yelp_data.txt')
    # setUpCategoriesTable(json_data, cur, conn)
    

if __name__ == "__main__":
	main()