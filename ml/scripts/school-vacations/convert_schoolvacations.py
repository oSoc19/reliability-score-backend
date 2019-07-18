#!/usr/bin/env python

import requests
from bs4 import BeautifulSoup
from datetime import datetime
SCHOOL_VACATIONS_URL = 'https://onderwijs.vlaanderen.be/nl/schoolvakanties-vorige-schooljaren'

MONTHS = ['januari', 'februari', 'maart', 'april', 'mei', 'juni', 'juli',
        'augustus', 'september', 'oktober', 'november', 'december']

def extract_date(vacation):
    vacation = vacation.split('(')[0] # Remove notes
    day_from = None
    day_to = None
    month_from = None
    month_to = None
    year_from = None
    year_to = None

    # Try to find the months
    for word in vacation.split():
        if word in MONTHS:
            if not month_from:
                month_from = MONTHS.index(word) + 1
            else:
                month_to = MONTHS.index(word) + 1

    # Handle same month
    if not month_to:
        month_to = month_from

    # Find year and days:
    for word in vacation.split():
        if word.isdigit():
            value = int(word)
            # Not more than 31 days in a month
            if value > 31:
                if not year_from:
                    year_from = value
                else:
                    year_to = value
            else:
                if not day_from:
                    day_from = value
                else:
                    day_to = value

    # Handle same day or year
    if not day_to:
        day_to = day_from
    if not year_to:
        year_to = year_from

    timestamp_from = datetime.now().replace(month=month_from, day=day_from,
            year=year_from, hour=0, minute=0, second=0, microsecond=0)
    timestamp_to = datetime.now().replace(month=month_to, day=day_to,
            year=year_to, hour=0, minute=0, second=0, microsecond=0)
    return timestamp_to, timestamp_from

def parse(raw_data):
    soup = BeautifulSoup(raw_data, features='html.parser')
    vacations_html = soup.find('div', {'class': 'field-item even'}).findAll('li')
    vacations_html = [ele.text.strip() for ele in vacations_html]

    data = {}
    for v in vacations_html:
        if 'vakantie:' in v:
            name = v.split(':')[0]
            timestamp_to, timestamp_from = extract_date(v)
            if not name in data:
                data[name] = []
            data[name].append({
                "from": timestamp_from.isoformat(),
                "to": timestamp_to.isoformat()
                })
    return data

def save(data):
    with open('vacations.csv', 'w') as f:
        for d in data:
            for entries in data[d]:
                f.write('{},{},{}\n'.format(d, entries['from'], entries['to']))

if __name__ == '__main__':
    r = requests.get(SCHOOL_VACATIONS_URL)
    d = parse(r.text)
    save(d)
