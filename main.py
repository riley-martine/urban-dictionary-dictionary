#!/usr/bin/env python3

import argparse
import asyncio
import itertools
import random
import string

import aiohttp
from bs4 import BeautifulSoup

# This whole thing could probably be about 200x faster if we parsed the sitemap instead:
# https://www.urbandictionary.com/sitemap-https.xml.gz
# it contains links to other sitemaps, e.g.
# sitemap1403-https.xml
# <url>
# <loc>
# https://www.urbandictionary.com/define.php?term=Lesida
# </loc>
# </url>
# if these are up to date (CHECK), then we should be able to pull all and
# use those as input for the js downloader.

API = "https://www.urbandictionary.com/browse.php?character={0}"

MAX_ATTEMPTS = 10

# To only parse soup once, final yield is the next page.
def extract_page_entries(html):
    soup = BeautifulSoup(html, "lxml")
    # find word list element, this might change in the future
    ul = soup.find_all("ul", class_="mt-3 columns-2 md:columns-3")[0]
    lis = ul.find_all("li")
    if not lis:
        return
    for li in lis:
        a = li.find("a").string
        if a:
            yield a
    next_link = soup.find("a", {"rel": "next"})
    if next_link:
        href = next_link["href"]
        yield "https://www.urbandictionary.com" + href


async def extract_letter_entries(session, letter):
    url = API.format(letter)
    attempt = 0
    while url:
        print(url)
        async with session.get(url) as response:
            code = response.status
            if code == 200:
                content = await response.text()
                page_entries_and_url = list(extract_page_entries(content))
                if page_entries_and_url and page_entries_and_url[-1].startswith(
                    "https://www.urbandictionary.com/browse.php?character"
                ):
                    yield page_entries_and_url[:-1]
                    url = page_entries_and_url[-1]
                else:
                    yield page_entries_and_url
                    url = None
                attempt = 0
            else:
                print(f"Trying again, expected response code: 200, got {code}")
                attempt += 1
                if attempt > MAX_ATTEMPTS:
                    break
                await asyncio.sleep(2**attempt + (random.randint(1, 100) / 100))


letters = list(string.ascii_uppercase) + ["#"]


async def download_letter_entries(session, letter, file, remove_dead):
    file = file.format(letter)
    entries = []
    async for entry in extract_letter_entries(session, letter):
        entries.append(entry)

    entries = itertools.chain.from_iterable(entries)

    if remove_dead:
        all_data = entries
    else:
        with open(file, "r", encoding="utf-8") as f:
            old_data = [line.strip() for line in f.readlines()]
        all_data = sorted(set(old_data).union(set(entries)), key=str.casefold)

    with open(file, "w", encoding="utf-8") as f:
        f.write("\n".join(all_data) + "\n")


async def download_entries(letters, file, remove_dead):
    session = aiohttp.ClientSession()
    async with asyncio.TaskGroup() as tg:
        for letter in letters:
            print(f"======={letter}=======")
            tg.create_task(download_letter_entries(session, letter, file, remove_dead))
    await session.close()


parser = argparse.ArgumentParser(description="Download urban dictionary words.")

parser.add_argument(
    "letters", metavar="L", type=str, nargs="*", help="Letters to download."
)

parser.add_argument(
    "--ifile",
    dest="ifile",
    help="input file name. Contains a list of letters separated by a newline",
    default="input.list",
)

parser.add_argument(
    "--out",
    dest="out",
    help="output file name. May be a format string",
    default="data/{0}.data",
)

parser.add_argument(
    "--remove-dead", action="store_true", help="Removes entries that no longer exist."
)

args = parser.parse_args()

letters = [letter.upper() for letter in args.letters]
if not letters:
    with open(args.ifile, "r") as ifile:
        for row in ifile:
            letters.append(row.strip())

asyncio.run(download_entries(letters, args.out, args.remove_dead))
