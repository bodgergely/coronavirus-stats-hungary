#!python
from collections import defaultdict
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
        url = create_url(page)
        sys.stderr.write(f"Downloading {url}\n")
        sys.stderr.flush()
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



g_unicode_to_ascii_table = {
    '\xa0' : ' ',
    'á': 'a',
    'û': 'u',
    'ú': 'u',
    'ü': 'u',
    'õ': 'o',
    '”': "\"",
    '„': '\"',
    'ó': 'o',
    'í': 'i',
    'ö': 'o',
    'é': 'e'
}

def remove_unicode(text, convert_table=g_unicode_to_ascii_table) -> str:
    res = []
    for c in text:
        if c in convert_table:
            res.append(convert_table[c])
        else:
            res.append(c)
    return "".join(res)

def reload(filepath: str, asciifi=True) -> List[Record]:
    records = []
    tokens_less_than_four_error = 0
    for line in open(filepath):
        line = line.strip()
        tokens = line.split(" ")
        if len(tokens) < 4:
            tokens_less_than_four_error += 1
            continue
        id = tokens[0]
        gender = tokens[1].lower()
        if asciifi:
            gender = remove_unicode(gender, {'é':'e', 'õ': 'o'}).lower();
        age = tokens[2]
        illnesses = [remove_unicode(t.lower()) for t in "".join(tokens[3:]).split(",") if t != '']
        records.append(Record(id, gender, age, illnesses))
    sys.stderr.write("tokens_less_than_four_error: " + str(tokens_less_than_four_error))
    return records



def determine_chars_from_illnesses(records: List[Record]):
    chars = set()
    for r in records:
        chars = chars.union(character_types(",".join(r.illnesses)))
    return chars

def count_genders(records: List[Record]):
    res = defaultdict(int)
    for r in records:
        res[r.gender] += 1
    return res

def count_illness_types(records: List[Record]):
    res = defaultdict(int)
    for r in records:
        for illness in r.illnesses:
            res[illness] += 1
    return res

def count_ages(records: List[Record]):
    res = defaultdict(int)
    for r in records:
        res[r.age] += 1
    return res


def character_types(text):
    chars = set()
    for c in text:
        chars.add(c)
    return chars

def statistics(records: List[Record]):
    print("Total records")
    print("--------------------------------")
    print(len(records))
    print("\nGender:Count of the given gender")
    print("--------------------------------")
    gender_stat = count_genders(records)
    gender_stat = sorted(gender_stat.items(), key=lambda x: x[1], reverse=True)
    for gender, count in gender_stat:
        print(gender + ":" + str(count))



    age_stat = count_ages(records)
    age_to_count = sorted(age_stat.items(), key=lambda x: x[1], reverse=True)
    print("\nAge:Count of the given age")
    print("----------------------------")
    for age, count in age_to_count:
        print(str(age) + ":" + str(count))
    print("\nAge:Count of the given age")
    print("----------------------------")
    age_to_count = sorted(age_stat.items(), key=lambda x: x[0], reverse=True)
    for age, count in age_to_count:
        print(str(age) + ":" + str(count))

    print("\nIllness:Count of the given illness")
    print("------------------------------------")

    illness_stat = count_illness_types(records)
    illness_stat = sorted(illness_stat.items(), key=lambda x: x[1], reverse=True)
    for illness, count in illness_stat:
        print(illness + ":" + str(count))


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
        statistics(records)

"""
./corona.py scrape 0 586 > records.txt
./corona.py reload ./records.txt > stats.txt
"""
if __name__ == "__main__":
    main(sys.argv[1:])