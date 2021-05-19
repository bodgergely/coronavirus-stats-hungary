#!python
from os import error
import sys
import requests
import bs4
import pickle
from typing import List
from bs4 import BeautifulSoup


URL_BASE = "https://koronavirus.gov.hu/elhunytak"

def create_url(page_num: int):
    return URL_BASE + "?" + "page=" + str(page_num)


def parse(soup: BeautifulSoup) -> List[List[str]]:
    table_body: bs4.element.Tag = soup.find(name="tbody")
    rows: bs4.element.ResultSet = table_body.find_all(name="tr")
    result = []
    for row in rows:
        tds: bs4.element.ResultSet = row.find_all(name="td")
        record = []
        for td in tds:
            td: bs4.element.Tag = td
            el: bs4.element.NavigableString = td.contents[0]
            record.append(el.strip())
        result.append(record)
    return result

class Record:
    def __init__(self, id, gender, age, illnesses) -> None:
        self.id = int(id)
        self.gender = gender
        self.age = int(age)
        self.illnesses = illnesses
    def __str__(self) -> str:
        return str(self.id) + " " + self.gender + " " + str(self.age) + " " + ",".join(self.illnesses)


def scrape(argv):
    if(len(argv) == 0):
        start_page = 0
        end_page = 9
    else:
        start_page = int(argv[0])
        end_page = int(argv[1])
    parse_errors = 0
    unicode_errors = 0
    for page in range(start_page, end_page+1):
        sys.stderr.write("Page: " + str(page))
        url = create_url(page)
        html_text = requests.get(url).text
        soup = BeautifulSoup(html_text, "html.parser")
        rows = parse(soup)
        for row in rows:
            if(len(row) != 4):
                parse_errors += 1
                continue
            id, gender, age, illnesses = row
            illnesses = [illness.strip() for illness in illnesses.split(',')]
            record = Record(id, gender, age, illnesses)
            try:
                print(record)
            except UnicodeEncodeError:
                unicode_errors += 1
                continue
    sys.stderr.write("parse_errors: " + str(parse_errors))
    sys.stderr.write('\n')
    sys.stderr.write("unicode_errors: " + str(unicode_errors))
    sys.stderr.write('\n')


def reload(filepath: str) -> List[Record]:
    records = []
    tokens_less_than_four_error = 0
    for line in open(filepath):
        line = line.strip()
        tokens = line.split(" ")
        if len(tokens) < 4:
            tokens_less_than_four_error += 1
            continue
        id = tokens[0]
        gender = tokens[1]
        age = tokens[2]
        illnesses = "".join(tokens[3:]).split(",")
        records.append(Record(id, gender, age, illnesses))
    sys.stderr.write("tokens_less_than_four_error: " + str(tokens_less_than_four_error))
    return records

def main(argv):
    if len(argv) < 1:
        print("Specify command!")
        exit(255)
    command = argv[0]
    if command == "scrape":
        scrape(argv[1:])
    elif command == "reload":
        if len(argv) < 2:
            print("Specify filepath!")
            exit(255)
        filepath = argv[1]
        records = reload(filepath)
        for r in records:
            print(r)



if __name__ == "__main__":
    main(sys.argv[1:])