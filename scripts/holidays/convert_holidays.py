#!/usr/bin/env python
from bs4 import BeautifulSoup
from datetime import datetime
import requests

URLS = ['https://www.kalender-365.be/feestdagen/2016.html',
        'https://www.kalender-365.be/feestdagen/2017.html',
        'https://www.kalender-365.be/feestdagen/2018.html',
        'https://www.kalender-365.be/feestdagen/2019.html']

MONTHS = ['januari', 'februari', 'maart', 'april', 'mei', 'juni', 'juli',
        'augustus', 'september', 'oktober', 'november', 'december']

def convert_date(time_str, year):
    day, month = time_str.split()
    day = int(day)
    month = MONTHS.index(month.lower()) + 1 # Months ar encoded between 1..12
    print(day, month, year)
    timestamp = datetime.now().replace(day=day,
                                       month=month,
                                       year=year,
                                       hour=0,
                                       minute=0,
                                       second=0,
                                       microsecond=0)
    return timestamp.isoformat()

def strip_years(holiday_name):
    h = holiday_name.split()[:-1]
    return ' '.join(h)

def parse(html, year):
    soup = BeautifulSoup(html, features='html.parser')
    data = []
    # Holidays table of kalender365.be
    table = soup.find('table', attrs={'class':'table table-striped table-hover tablesorter table-small-font tablesorter-default sort-v1'})
    table_body = table.find('tbody')

    rows = table_body.find_all('tr')
    for row in rows:
        cols = row.find_all('td')
        cols = [ele.text.strip() for ele in cols]
        cols = cols[:-1] # Remove useless column with only '-' in it
        cols[0] = convert_date(cols[0], year) # Convert date
        cols[1] = strip_years(cols[1])
        data.append([ele for ele in cols if ele]) # Get rid of empty values

    with open('{}.csv'.format(year), 'w') as f:
        for d in data:
            f.write(','.join(d) + '\n')

if __name__ == '__main__':
    for url in URLS:
        r = requests.get(url)
        parse(r.text, int(url.split('/')[-1].replace('.html', '')))
