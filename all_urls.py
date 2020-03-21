from crawl import crawl
from utils import *
from urllib.request import urlparse
import tldextract

def get_urls():
    all_unis = read_csv('universities.csv')
    universities = filter_by_continent(all_unis, 'Europe')

    for count, school in enumerate(universities, start = 1):
        url = school['website']
        netloc = urlparse(url).netloc
        
        print(str(count) + ':   ' + netloc + ' - Crawl... ', end = '')
        try:
            links = crawl(url, max_depth=0)
        except:
            print('Fail')
            continue
        print('Done (' + str(len(links)) + ' urls) - Write... ', end = '')

        domain = tldextract.extract(url).registered_domain
        with open(f"urls/{domain}.txt", "w") as f:
            print(url, file=f)
            for link in links:
                try:
                    print(link.strip(), file=f)
                except:
                    continue
        print('Done')

if __name__ == "__main__":
    get_urls()
