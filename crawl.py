import requests
from urllib.request import urlparse, urljoin
from bs4 import BeautifulSoup

def is_valid(url):
    """
    Checks whether `url` is a valid URL.
    """
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)

def get_all_page_links(url):
    """
    Returns all URLs that is found on `url` in which it belongs to the same website
    """
    # all URLs of `url`
    urls = set()
    # domain name of the URL without the protocol
    domain_name = urlparse(url).netloc
    soup = BeautifulSoup(requests.get(url).content, "html.parser")
    for a_tag in soup.findAll("a"):
        href = a_tag.attrs.get("href")
        if href == "" or href is None:
            # href empty tag
            continue
        # join the URL if it's relative (not absolute link)
        href = urljoin(url, href)
        parsed_href = urlparse(href)
        # remove URL GET parameters, URL fragments, etc.
        href = parsed_href.scheme + "://" + parsed_href.netloc + parsed_href.path
        if not is_valid(href):
            # not a valid URL
            continue
        if domain_name not in href:
            # external link
            continue
        urls.add(href)
    return urls

def crawl(url, max_depth=-1):
    def crawl_impl(url, max_depth):
        nonlocal visited_urls
        links = get_all_page_links(url)
        all_links = set(links)
        visited_urls.add(url)
        if not max_depth:
            return all_links
        for link in filter(lambda url: url not in visited_urls, links):
            all_links |= crawl(link, max_depth - 1)
        return all_links

    visited_urls = set()
    return crawl_impl(url, max_depth)
