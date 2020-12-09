import unittest
import requests
import sqlite3
import json
import os
import csv
from datetime import datetime, timedelta

'''
1. pull cases from each day for 100 days (USA)
2. Total Cases until now (100 countries) vs. GDP
'''

#stringency

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

# def setUpCasesTable(cur, conn):
#     cur.execute('CREATE TABLE IF NOT EXISTS Stringencies (Date CHAR(10), Stringencies INTEGER)')
#     all_cases = get_data('2020-08-01', '2020-12-01')
#     n = 0
#     x = 25
#     cur.execute('SELECT Date FROM Stringencies ORDER BY Date DESC LIMIT 1')
#     try:
#         last_entry = cur.fetchone()[0]
#         for index in range(len(all_cases)):
#             if all_cases[index][0] == last_entry:
#                 n = index + 1
#                 x = n + 25
#     except:
#         last_entry = 0

#     for i in range(len(all_cases[n:x])):
#         data = all_cases[n + i]
#         date = data[0]
#         cases = data[1]
#         cur.execute('INSERT INTO Stringencies (Date, Stringencies) VALUES (?,?)', (date, cases))
#     conn.commit()

def cases_per_day(cur, conn):
    avg_cases = []
    cur.execute('SELECT United_States, Russia, Poland, Norway, Egypt, New_Zealand, Cuba, Ghana, Lebanon, Uganda FROM Cases ORDER BY Date ASC LIMIT 1')
    first_cases = cur.fetchall()[0]
    cur.execute('SELECT United_States, Russia, Poland, Norway, Egypt, New_Zealand, Cuba, Ghana, Lebanon, Uganda FROM Cases ORDER BY Date DESC LIMIT 1')
    last_cases = cur.fetchall()[0]
    cur.execute('SELECT Date FROM Cases')
    num_days = cur.fetchall()
    countries = ['United_States', 'Russia', 'Poland', 'Norway', 'Egypt', 'New_Zealand', 'Cuba', 'Ghana', 'Lebanon', 'Uganda']
    for index in range(len(first_cases)):
        averages = (last_cases[index] - first_cases[index]) / len(num_days)
        avg_cases.append((countries[index], averages))
    return avg_cases

def percentage_recovered(cur, conn):
    cur.execute('SELECT Country_ID, Cases, Recovered FROM CountryData')
    percentage_list = []
    all_data = cur.fetchall()
    for data in all_data:
        country_id = data[0]
        cases = data[1]
        recovered = data[2]
        percent = (recovered / cases) * 100
        percentage_list.append((country_id, percent))
    return percentage_list


def write_csv(cur, conn, filename):
    percent_data = percentage_recovered(cur, conn)
    avg_cases = cases_per_day(cur, conn)
    fieldnames = ['Country_ID', 'Percent', '', 'Country', 'Average Cases Per Day']
    outFile = open(filename, 'w', encoding="utf8", newline = '')
    csv_writer = csv.writer(outFile, delimiter=',')
    csv_writer.writerow(fieldnames)
    for i in range(len(percent_data)):
        if i < 10:
            csv_writer.writerow([percent_data[i][0], percent_data[i][1], '', avg_cases[i][0], avg_cases[i][1]])
            i += 1
        else:
            csv_writer.writerow([percent_data[i][0], percent_data[i][1]])
    outFile.close()




def main():
    # USA_cases = dayCase('2020-08-01', '2020-12-01')
    # USA_cases.create_request_url()
    # USA_cases.get_data()
    # create_request_url('2020-08-01', '2020-12-01')




    cur, conn = setUpDatabase('Covid_Cases_USA.db')
    cases_per_day(cur, conn)
    percentage_recovered(cur, conn)
    write_csv(cur, conn, 'calculations.csv')
    # setUpCasesTable(cur, conn)

    conn.close()
    # json_data = readDataFromFile('yelp_data.txt')
    # setUpCategoriesTable(json_data, cur, conn)
    

if __name__ == "__main__":
	main()