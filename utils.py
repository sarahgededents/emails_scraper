import csv

def read_csv(path):
    with open(path, 'r', newline='', encoding='UTF-8') as f:
        return list(csv.DictReader(f))

CONTINENTS = read_csv('Countries-Continents.csv')

def filter_by_continent(csv, continent='Europe', country_col='country'):
    continent = [ row['Country'] for row in CONTINENTS if row['Continent'] == continent ]
    return [ row for row in csv if row[country_col] in continent ]

def filter_by_country(csv, country='France', country_col='country'):
    return [ row for row in csv if row[country_col]==country ]

def csv_to_colset(csv, col='name'):
    return { row[col] for row in csv }
     
