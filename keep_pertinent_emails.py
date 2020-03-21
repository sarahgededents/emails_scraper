import re
import csv
from utils import *

REGEX = r"""[a-zA-Z0-9._-]+@[a-zA-Z0-9_-]+\.[a-zA-Z]+(\.[a-zA-Z]+)?"""

def is_email_valid(email):
    return re.fullmatch(REGEX, email) \
        and 'admission' not in email \
        and 'alumni' not in email \
        and email.rsplit('.', 1)[-1] not in { 'png', 'jpg', 'jpeg', 'pdf', 'mp4', 'webm', 'mpeg', 'html' }

def sort_emails(file='retrieved_emails.csv', new_file='emails2.csv'):
    with open(file, 'r', encoding='utf-8', newline='') as f:
        lines = list(csv.reader(f))
    new_lines = []
    for line in lines:
        emails = filter(is_email_valid, line[1:])
        new_lines.append([line[0]] + list(emails))
    with open(new_file, 'w', encoding='utf-8', newline='') as f:
        csv.writer(f).writerows(new_lines)

def make_country_predicate(country='France'):
    csv = read_csv('universities.csv')
    csv = filter_by_country(csv, country)
    names = csv_to_colset(csv, 'name')
    return lambda name: name in names

def sort_emails_by_countries(country_to_sort = 'France', file='emails2.csv'):
    in_france = make_country_predicate(country_to_sort)
    with open(file, 'r', encoding='utf-8', newline='') as f:
        lines = list(csv.reader(f))
    lines_in_france = filter(lambda l: in_france(l[0]), lines)
    lines_foreign = filter(lambda l: not in_france(l[0]), lines)
    with open('emails_fr.csv', 'w', encoding='utf-8', newline='') as f:
        csv.writer(f).writerows(lines_in_france)
    with open('emails_foreign.csv', 'w', encoding='utf-8', newline='') as f:
        csv.writer(f).writerows(lines_foreign)
