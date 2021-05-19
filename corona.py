#!python
import sys
import requests
from bs4 import BeautifulSoup


URL_BASE = "https://koronavirus.gov.hu/elhunytak"

def create_url(page_num: int):
    return URL_BASE + "?" + "page=" + str(page_num)


def main(argv):
    if(len(argv) == 0):
        start_page = 0
        end_page = 10
    else:
        start_page = int(argv[0])
        end_page = int(argv[1])
    for page in range(start_page, end_page+1):
        url = create_url(page)
        html_text = requests.get(url).text
        soup = BeautifulSoup(html_text, "html.parser")
        print(soup.title)

if __name__ == "__main__":
    main(sys.argv[1:])