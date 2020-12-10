import requests
import sqlite3
import json
import os
import csv
import re
import matplotlib
import matplotlib.pyplot as plt
import datetime as dt
import matplotlib.dates as mdates
import numpy as np
import plotly.express as px
import pandas as pd

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
    new_cases = []
    cur.execute("SELECT Date, United_States FROM Cases")
    us = cur.fetchall()
    for i in range(1, len(us)):
        difference = us[i][1] - us[i - 1][1]
        new_cases.append((us[i][0], difference))
    return new_cases

def avg_new_cases(cur, conn):
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
    cur.execute('SELECT CountryData.Cases, CountryData.Recovered, GDP.Country, GDP.GDP FROM CountryData INNER JOIN GDP ON CountryData.Country_ID = GDP.Country_ID')
    percentage_list = []
    all_data = cur.fetchall()
    for data in all_data:
        cases = data[0]
        recovered = data[1]
        country = data[2]
        gdp = data[3]
        percent = (recovered / cases) * 100
        percentage_list.append((country, percent, gdp))
    return percentage_list


def write_csv(cur, conn, filename):
    percent_data = percentage_recovered(cur, conn)
    avg_cases = avg_new_cases(cur, conn)
    new_cases = cases_per_day(cur, conn)
    fieldnames = ['Country', 'Percent', 'GDP', ' ', 'Country', 'Average Cases Per Day', ' ', 'Date', 'New Cases']
    outFile = open(filename, 'w', encoding="utf8", newline = '')
    csv_writer = csv.writer(outFile, delimiter=',')
    csv_writer.writerow(['PERCENT RECOVERED', ' ', ' ',' ', 'AVERAGE DAILY CASES', ' ', '', 'NEW DAILY CASES'])
    csv_writer.writerow(fieldnames)
    for i in range(len(new_cases)):
        if i < 10:
            csv_writer.writerow([percent_data[i][0], percent_data[i][1], percent_data[i][2], ' ', avg_cases[i][0], avg_cases[i][1], ' ', new_cases[i][0], new_cases[i][1]])
        elif i >= 10 and i < 100:
            csv_writer.writerow([percent_data[i][0], percent_data[i][1], percent_data[i][2], ' ', ' ', ' ', ' ', new_cases[i][0], new_cases[i][1]])
        else:
            csv_writer.writerow([' ', ' ', ' ', ' ', ' ', ' ', ' ', new_cases[i][0], new_cases[i][1]])
    outFile.close()

#VISUALIZATIONS
def new_cases_US(cur, conn):
    x = []
    y = []
# Data for plotting
    new_cases = cases_per_day(cur, conn)
    for date, cases in new_cases:
        x.append(date)
        y.append(cases)
    start = x[0]
    date1 = start.split('-')
    start_year = int(date1[0])
    start_month = int(date1[1])
    start_day = int(date1[2])
    end = x[-1]
    date2 = end.split('-')
    end_year = int(date2[0])
    end_month = int(date2[1])
    end_day = int(date2[2])

    
    #dates = mdates.drange(dt.datetime(start_year, start_month, start_day), dt.datetime(end_year, end_month, end_day), dt.timedelta(weeks=3))
    # create the line graph
    fig, ax = plt.subplots()
    ax.plot(x,y)
    ax.set_xlabel('Date')
    ax.set_ylabel('Number of New Cases')
    ax.set_title('Daily New Cases in the US')
    ax.grid()
    fig.autofmt_xdate()
    # N = 5
    # ind = np.arange(N)
    # ax.set_xticks(ind)
    # ax.set_xticklabels(('August 2020', 'September 2020', 'October 2020', 'November 2020', 'December 2020'))
    plt.xticks(y, x, rotation='vertical')
    N = 122
    data = np.linspace(0, N, N)

    plt.plot(data)

    plt.xticks(range(N)) # add loads of ticks
    plt.grid()

    plt.gca().margins(x=0)
    plt.gcf().canvas.draw()
    tl = plt.gca().get_xticklabels()
    maxsize = max([t.get_window_extent().width for t in tl])
    m = 0.2 # inch margin
    s = maxsize/plt.gcf().dpi*N+2*m
    margin = m/plt.gcf().get_size_inches()[0]

    plt.gcf().subplots_adjust(left=.07, right=1.-margin)
    plt.gcf().set_size_inches(s, plt.gcf().get_size_inches()[1])

    plt.tick_params(axis='x', which='major', labelsize=4)
    plt.tick_params(axis='y', which='major', labelsize=4)
    # save the line graph
    fig.savefig("newcases.png")

    # show the line graph
    plt.show()

def case_vs_population(cur, conn):
    x = []
    y = []
    avg_cases = avg_new_cases(cur, conn)
    for country, cases in avg_cases:
        country = country.replace('_', ' ')
        cur.execute(f'SELECT Country_ID FROM GDP WHERE Country = "{country}"')
        country_id = cur.fetchone()[0]
        cur.execute(f'SELECT Population FROM CountryData WHERE Country_ID = "{country_id}"')
        population = cur.fetchone()[0]
        x.append(population)
        y.append(cases)
    fig, ax = plt.subplots()
    ax.set_xlabel('Population')
    ax.set_ylabel('Average Daily Cases')
    ax.set_title('Population vs. Average Daily Cases')
    plt.scatter(x, y)
    fig.savefig("avgcases.png")
    plt.show()

def recovered_vs_gdp(cur, conn):
    x = []
    y = []
    recovered = percentage_recovered(cur, conn)
    for country, percent, gdp in recovered:
        x.append(gdp)
        y.append(percent)
    fig, ax = plt.subplots()
    ax.set_xlabel('GDP')
    ax.set_ylabel('Percent Recovered')
    ax.set_title('GDP vs. Percent Recovered')
    plt.scatter(x, y)
    fig.savefig("recovered.png")
    plt.show()

def zoomed_in(cur, conn):
    x = []
    y = []
    recovered = percentage_recovered(cur, conn)
    for country, percent, gdp in recovered:
        if country != 'United States':
            if country != 'China':
                x.append(gdp)
                y.append(percent)
    fig, ax = plt.subplots()
    ax.set_xlabel('GDP')
    ax.set_ylabel('Percent Recovered')
    ax.set_title('GDP vs. Percent Recovered (Zoomed)')
    plt.scatter(x, y)
    fig.savefig("zoomed.png")
    plt.show()



def main():
    # USA_cases = dayCase('2020-08-01', '2020-12-01')
    # USA_cases.create_request_url()
    # USA_cases.get_data()
    # create_request_url('2020-08-01', '2020-12-01')




    cur, conn = setUpDatabase('Covid_Cases_USA.db')
    avg_new_cases(cur, conn)
    cases_per_day(cur, conn)
    percentage_recovered(cur, conn)
    write_csv(cur, conn, 'calculations.csv')
    # setUpCasesTable(cur, conn)
    recovered_vs_gdp(cur, conn)
    zoomed_in(cur, conn)
    case_vs_population(cur, conn)
    new_cases_US(cur, conn)
    conn.close()
    # json_data = readDataFromFile('yelp_data.txt')
    # setUpCategoriesTable(json_data, cur, conn)
    

if __name__ == "__main__":
	main()