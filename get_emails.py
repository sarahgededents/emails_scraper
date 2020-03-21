import re
import tldextract
from pyppeteer.errors import *
from utils import read_csv, filter_by_continent
import csv
import os
from requests.exceptions import *
from functools import partial
import requests
#from time import sleep

def get_urls(school):
    url = school if isinstance(school, str) else school['website']
    domain = tldextract.extract(url).registered_domain
    with open(f'urls/{domain}.txt') as f: 
        return f.read().split('\n')

EMAIL_REGEX = r"""(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9]))\.){3}(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9])|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])"""
UNIS_CSV = 'universities.csv'
EMAILS_CSV = 'retrieved_emails.csv'
TEMP_EMAILS_CSV = 'temp_emails.csv'

def print_msg(letter, head, funcname=None, msg=None, url=None, short=True):
    fcn_part = "" if funcname is None else f": {funcname}"
    msg_part = "" if msg is None else f": {msg}"
    url_part = "" if url is None else f": {url}"
    ed = '' if short else '\n'
    print(letter if short else f"{head}{fcn_part}{msg_part}{url_part}", end=ed)

print_success = partial(print_msg, 'S', "SUCCESS")
print_error = partial(print_msg, 'E', "ERROR")
print_warning = partial(print_msg, 'W', "WARNING")
print_skip = partial(print_msg, 'X', "SKIP")

def get_page_rqs(url, short=True):
    fname = "get_page_rqs"
    if not url:
        print_warning(fname, "empty url (skipping)", url, short)
        return ""
    enc = None
    page = None
    while True:
        try:
            rq = requests.get(url, timeout=20)
            enc = rq.encoding if enc is None else enc
            page = rq.content.decode('utf-8' if enc is None else enc)
            break
        except requests.exceptions.MissingSchema as e:
            if url[0] == ' ':
                print_warning(fname, "skipping invalid url (starts with spaces)", url, short)
                return ""
            proto, uri = url.split('/', 1)
            if uri[0] == '/':
                print_error(fname, "missing schema", url, short)
                raise
            fixed_url = f"{proto}//{uri}"
            print_warning(fname, f"missing schema, retrying with {fixed_url}", url, short)
            url = fixed_url
            continue
        except (ConnectionError, InvalidSchema, requests.exceptions.InvalidURL, requests.exceptions.ReadTimeout) as e:
            print_error(fname, "skipping", url, short)
            return ""
        except (UnicodeDecodeError, ChunkedEncodingError, TooManyRedirects, requests.exceptions.ContentDecodingError) as e:
            print_error(fname, "cannot decode (skipping)", url, short)
            return ""
        except LookupError as e:
            print_warning(fname, f"wrong encoding, retrying with utf-8", url, short)
            enc = 'utf-8'
            continue
    print_success(fname, "extracted page", url, short)
    return page

def get_emails(url, short=True):
        page = get_page_rqs(url, short)
        if not page:
            return set()
        matches = re.finditer(EMAIL_REGEX, page)
        return set(map(lambda m: m.group(), matches))

def count_lines(file):
    try:
        with open(file, 'r', encoding='utf-8') as f:
            return len(f.readlines())
    except FileNotFoundError:
        return 0

def parse_temp_emails(path):
    try:
        with open(path, 'r', encoding='utf-8', newline='') as tempf:
            row = next(csv.reader(tempf), [0])
            return (int(row[0]), row[1:])
    except FileNotFoundError:
        return 0, []

def my_func(short=True):
    all_unis = read_csv(UNIS_CSV)
    universities = filter_by_continent(all_unis, 'Europe')
    lines_done = count_lines(EMAILS_CSV)
    urls_to_skip, temp_emails = parse_temp_emails(TEMP_EMAILS_CSV)
    with open(EMAILS_CSV, 'a', encoding='utf-8', newline='') as outf:
        writer = csv.writer(outf)
        for i, school in enumerate(universities):
            if i < lines_done :
                continue
            website = school['website']
            domain = tldextract.extract(website).registered_domain
            try:
                all_urls = get_urls(website)
            except FileNotFoundError:
                print(f'{i}: ERROR: no urls for ' + domain)
                all_urls = set()
            print(f'{i}: Gathering emails for {domain}...', end='')
            emails = set()
            if urls_to_skip > 0:
                emails = set(temp_emails)
            for j, url in enumerate(all_urls):
                if urls_to_skip > 0:
                    urls_to_skip -= 1
                    continue
                url = url.strip()
                if not url or url[0] == '/':
                    print_warning("main", "skip invalid url", url, short)
                    continue
                emails |= get_emails(url, short)
                with open(TEMP_EMAILS_CSV, 'w', encoding='utf-8', newline='') as tempf:
                    csv.writer(tempf).writerow([j+1] + list(emails))
                #sleep(5)
            try:
                os.remove(TEMP_EMAILS_CSV)
            except FileNotFoundError:
                pass
            count = len(emails)
            print(f' Done ({count} found) - Writing output... ', end='')
            writer.writerow([ school['name'] ] + list(emails))
            outf.flush()
            print('Done.')

if __name__ == '__main__':
    my_func(True)
