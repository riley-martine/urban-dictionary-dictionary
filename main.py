import string
from bs4 import BeautifulSoup
import urllib2
import time
import os
import argparse

API = "http://www.urbandictionary.com/browse.php?character={0}&page={1}"

MAX_ATTEMPTS = 10
DELAY = 10

# http://stackoverflow.com/a/554580/306149
class NoRedirection(urllib2.HTTPErrorProcessor):
    def http_response(self, request, response):
        return response
    
    https_response = http_response

def extract_page_entries(html):
    soup = BeautifulSoup(html, "html.parser")
    list = soup.find(id="columnist").find('ul')
    for li in list.find_all('li'):
        yield li.find('a').string

def extract_letter_entries(letter):
    page = 1
    attempt = 0
    while True:
        print(page)
        url = API.format(letter, page)
        response = urllib2.urlopen(url)
        code = response.getcode()
        if code == 200:
            yield extract_page_entries(response.read())
            page += 1
            attempt = 0
        if code == 301 or code == 302:
            # end of pages
            break
        else:
            attempt += 1
            if attempt > MAX_ATTEMPTS:
                break
            time.sleep(DELAY * attempt)

opener = urllib2.build_opener(NoRedirection, urllib2.HTTPCookieProcessor())
urllib2.install_opener(opener)


letters = list(string.ascii_uppercase) + ['#']

def download_letter_entries(letter, file):
    file = file.format(letter)
    for entry_set in extract_letter_entries(letter):
        with open(file, 'a') as f:
            data = ('\n'.join(entry_set)).encode('utf8')
            f.write(data)

def download_entries(letters, file):
    for letter in letters:
        print('======={0}======='.format(letter))
        download_letter_entries(letter, file)

parser = argparse.ArgumentParser(description='Process some integers.')

parser.add_argument('letters', metavar='N', nargs='+',
                   help='letters to download entries for')

parser.add_argument('--out', dest='out',
                   help='output file name. May be a format string')

args = parser.parse_args()

download_entries(args.letters, args.out)
