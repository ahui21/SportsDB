from lxml import html
import requests

webURL = 'http://www.basketball-reference.com/players/a/'
alphabet = []

# players has 10 columns (player name, from, to, position, height, weight, birth date, college, currently active, hall of fame
players = [ [],
            [],
            [],
            [],
            [],
            [],
            [],
            [],
            [],
            [] ]

def scraper():
    global webURL

    page = requests.get(webURL)
    tree = html.fromstring(page.content)

    for i in tree.xpath('//following::h1'):
        for j in i.xpath('//following::*'):
            print j.text
            print '**************************************************'

def main():
    scraper()

if __name__ == '__main__':
    main()

