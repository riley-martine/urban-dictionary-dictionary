import string
from bs4 import BeautifulSoup
import urllib.request
import time
import os
import argparse
import re

API = "https://www.urbandictionary.com/browse.php?character={0}"

MAX_ATTEMPTS = 10
DELAY = 10

NUMBER_SIGN = "*"


# https://stackoverflow.com/a/554580/306149
class NoRedirection(urllib.request.HTTPErrorProcessor):
    def http_response(self, request, response):
        return response
    
    https_response = http_response

def extract_page_entries(letter, html):
    soup = BeautifulSoup(html, "html.parser")
    list = soup.find(id="columnist").find('ul')
    for li in list.find_all('li'):
        a = li.find('a').string
        if a:
            yield a

def get_next(letter, html):
    soup = BeautifulSoup(html, "html.parser")
    next = soup.find('a', {"rel":"next"})
    if next:
        href = next['href']
        return 'https://www.urbandictionary.com' + href
    return None
    
def extract_letter_entries(letter):
    url = API.format(letter)
    attempt = 0
    while url:
        print(url)
        response = urllib.request.urlopen(url)
        code = response.getcode()
        if code == 200:
            content = response.read()
            yield list(extract_page_entries(letter, content))
            url = get_next(letter, content)
            attempt = 0
        else:
            print(f"Trying again, expected response code: 200, got {code}")
            attempt += 1
            if attempt > MAX_ATTEMPTS:
                break
            time.sleep(DELAY * attempt)

opener = urllib.request.build_opener(NoRedirection, urllib.request.HTTPCookieProcessor())
urllib.request.install_opener(opener)


letters = list(string.ascii_uppercase) + ['#']

def download_letter_entries(letter, file):
    file = file.format(letter)
    for entry_set in extract_letter_entries(letter):
        with open(file, 'a', encoding='utf-8') as f:
            data = ('\n'.join(entry_set))
            f.write(data + '\n')

def download_entries(letters, file):
    for letter in letters:
        print(f"======={letter}=======")
        download_letter_entries(letter, file)

parser = argparse.ArgumentParser(description='Process some integers.')

parser.add_argument('--ifile', dest='ifile',
                   help='input file name. Contains a list of letters separated by a newline', default="input.list")

parser.add_argument('--out', dest='out',
                   help='output file name. May be a format string', default="data/{0}.data")

args = parser.parse_args()

letters = []
with open(args.ifile, 'r') as ifile:
    for row in ifile:
        letters.append(row.strip())

download_entries(letters, args.out)
