from all_urls import get_urls
from get_emails import my_func
from keep_pertinent_emails import sort_emails, sort_emails_by_countries
import os
import shutil

COUNTRY = 'France'
if __name__ == '__main__':
    get_urls()
    my_func(True)
    sort_emails()
    sort_emails_by_countries(COUNTRY)
    os.remove('emails2.csv')
    os.remove('universities.csv')
    os.remove('Countries-Continents.csv')
    os.remove('retrieved_emails.csv')
    shutil.rmtree('urls')
