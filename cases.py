import unittest
import requests
import sqlite3
import json
import os

'''
1. pull cases from each day for 100 days (USA)
2. Total Cases until now (100 countries) vs. GDP
'''
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
        for date in data:
            dates = date
            USA = data[date]['USA']
            cases = USA.get('confirmed')
            
        return jsons



def main():
    USA_cases = dayCase('2020-08-01', '2020-12-01')
    USA_cases.create_request_url()
    USA_cases.get_data()

if __name__ == "__main__":
	main()