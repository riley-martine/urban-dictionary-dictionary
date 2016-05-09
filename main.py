import string
from bs4 import BeautifulSoup
import urllib2
import time
import os
import argparse
import re

API = "http://www.urbandictionary.com/browse.php?word={0}"

MAX_ATTEMPTS = 10
DELAY = 10

NUMBER_SIGN = "#"


# http://stackoverflow.com/a/554580/306149
class NoRedirection(urllib2.HTTPErrorProcessor):
    def http_response(self, request, response):
        return response
    
    https_response = http_response

def extract_page_entries(letter, html):
    soup = BeautifulSoup(html, "html.parser")
    list = soup.find(id="columnist").find('ul')
    for li in list.find_all('li'):
        a = li.find('a').string
        if a:
            if letter == NUMBER_SIGN and not re.match('[a-z]', a, re.I):
                yield a
            elif letter != NUMBER_SIGN and not re.match(chr(ord(letter) + 1), a, re.I):
                yield a

def get_next(letter, html):
    soup = BeautifulSoup(html, "html.parser")
    next = soup.find('a', {"rel":"next"})
    if next:
        href = next['href']
        if letter == NUMBER_SIGN:
            if re.search('word=[a-z]', href, re.I):
                return None
        elif re.search('word={0}'.format(chr(ord(letter) + 1)), href, re.I):
            return None    
        return 'http://www.urbandictionary.com' + href
    return None
    
def extract_letter_entries(letter):
    if letter == NUMBER_SIGN:
        start = ''
    else:
        start = letter + 'a'
    url = API.format(start)
    attempt = 0
    while url:
        print(url)
        response = urllib2.urlopen(url)
        code = response.getcode()
        if code == 200:
            content = response.read()
            yield list(extract_page_entries(letter, content))
            url = get_next(letter, content)
            attempt = 0
        else:
            print('retry')
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
            f.write(data + '\n')

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
