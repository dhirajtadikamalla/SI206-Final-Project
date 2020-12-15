import sqlite3
import json
import os
import csv
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
matplotlib.use('qt4agg')


#Run gdp.py first 4 times, then run cases.py 5 times, then run analysis.py once
#Open calculations.csv with excel

def setUpDatabase(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn

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
    fieldnames = ['Country', 'Percent', 'GDP', '', 'Country', 'Average Cases Per Day', '', 'Date', 'New Cases']
    outFile = open(filename, 'w', encoding="utf8", newline = '')
    csv_writer = csv.writer(outFile, delimiter=',')
    csv_writer.writerow(['PERCENT RECOVERED', '', '','', 'AVERAGE DAILY CASES', '', '', 'NEW DAILY CASES'])
    csv_writer.writerow(fieldnames)
    for i in range(len(new_cases)):
        if i < 10:
            csv_writer.writerow([percent_data[i][0], percent_data[i][1], percent_data[i][2], '', avg_cases[i][0], avg_cases[i][1], '', new_cases[i][0], new_cases[i][1]])
        elif i >= 10 and i < 100:
            csv_writer.writerow([percent_data[i][0], percent_data[i][1], percent_data[i][2], '', '', '', '', new_cases[i][0], new_cases[i][1]])
        else:
            csv_writer.writerow(['', '', '', '', '', '', '', new_cases[i][0], new_cases[i][1]])
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
    fig, ax = plt.subplots()
    ax.plot(x,y)
    ax.set_xlabel('Date')
    ax.set_ylabel('Number of New Cases')
    ax.set_title('Daily New Cases in the US')
    ax.grid()
    fig.autofmt_xdate()
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
    fig.savefig("newcases.png")

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
    ax.set_xlabel('Population (1e8)')
    ax.set_ylabel('Average Daily Cases')
    ax.set_title('Population vs. Average Daily Cases')
    plt.scatter(x, y)
    fig.savefig("avgcases.png")
    plt.show()

def case_vs_country(cur, conn):
    x = []
    y = []
    avg_cases = avg_new_cases(cur, conn)
    for country, cases in avg_cases:
        x.append(country)
        y.append(cases)
    fig = plt.figure()
    ax = fig.add_subplot()
    ax.bar(x,y)
    ax.set_xlabel('Country')
    ax.set_ylabel('Average Daily Cases')
    ax.set_title('Average Daily Cases per Country')
    plt.tick_params(axis='x', which='major', labelsize=6)
    plt.tick_params(axis='y', which='major', labelsize=6)
    fig.savefig("case_country.png")
    plt.show()

def case_vs_country_zoomed(cur, conn):
    x = []
    y = []
    avg_cases = avg_new_cases(cur, conn)
    for country, cases in avg_cases:
        x.append(country)
        y.append(cases)
    fig = plt.figure()
    ax = fig.add_subplot()
    ax.bar(x[1:],y[1:])
    ax.set_xlabel('Country')
    ax.set_ylabel('Average Daily Cases')
    ax.set_title('Average Daily Cases per Country (Zoomed)')
    plt.tick_params(axis='x', which='major', labelsize=6)
    plt.tick_params(axis='y', which='major', labelsize=6)
    fig.savefig("case_country_zoomed.png")
    plt.show()

def recovered_vs_gdp(cur, conn):
    x = []
    y = []
    recovered = percentage_recovered(cur, conn)
    for country, percent, gdp in recovered:
        x.append(gdp)
        y.append(percent)
    fig, ax = plt.subplots()
    ax.set_xlabel('GDP (USD Billion)')
    ax.set_ylabel('Percent Recovered (%)')
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
    ax.set_xlabel('GDP (USD Billion)')
    ax.set_ylabel('Percent Recovered (%)')
    ax.set_title('GDP vs. Percent Recovered (Zoomed)')
    plt.scatter(x, y)
    fig.savefig("zoomed.png")
    plt.show()



def main():
    cur, conn = setUpDatabase('Covid_Cases_USA.db')
    avg_new_cases(cur, conn)
    cases_per_day(cur, conn)
    percentage_recovered(cur, conn)
    write_csv(cur, conn, 'calculations.csv')

    #VISUALIZATIONS
    new_cases_US(cur, conn)
    case_vs_country(cur, conn)
    case_vs_country_zoomed(cur, conn)
    case_vs_population(cur, conn)
    recovered_vs_gdp(cur, conn)
    zoomed_in(cur, conn)
    
    conn.close()
    

if __name__ == "__main__":
	main()