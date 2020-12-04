import unittest
import requests
import sqlite3
import json
import os

'''
1. pull cases from each day for 100 days (USA)
2. Total Cases until now (100 countries) vs. GDP
'''
class dataBase:

    def readDataFromFile(self, filename):
        full_path = os.path.join(os.path.dirname(__file__), filename)
        f = open(full_path, encoding='utf-8')
        file_data = f.read()
        f.close()  
        json_data = json.loads(file_data)
        return json_data

    def setUpDatabase(self, db_name):
        path = os.path.dirname(os.path.abspath(__file__))
        conn = sqlite3.connect(path+'/'+db_name)
        cur = conn.cursor()
        return cur, conn

    def setUpCasesTable(self, cur, conn):
        functionData = dayCase.get_data(self)
        cur.execute('CREATE TABLE Cases (Date CHAR(10), Cases INTEGER)')
        for date, cases in functionData:
            cur.execute('INSERT INTO Cases (Date, Cases) VALUES (?, ?)', (date, cases))
            

        return cur, conn


class dayCase:

    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date
    def create_request_url(self):
        url = f'https://covidtrackerapi.bsg.ox.ac.uk/api/v2/stringency/date-range/{self.start_date}/{self.end_date}'
        return url
    def get_data(self):
        request_url = self.create_request_url()
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



def main():
    USA_cases = dayCase('2020-08-01', '2020-12-01')
    USA_cases.create_request_url()
    USA_cases.get_data()
    cur, conn = dataBase.setUpDatabase('Covid_Cases_USA.db')
    dataBase.setUpCasesTable(cur, conn)

    # json_data = readDataFromFile('yelp_data.txt')
    # setUpCategoriesTable(json_data, cur, conn)
    

if __name__ == "__main__":
	main()