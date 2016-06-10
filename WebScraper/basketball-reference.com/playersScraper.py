from lxml import html
import requests
import os

webURL = 'http://www.basketball-reference.com/players/'
alphabet = []

# players has 10 columns (player name, from, to, position, height, weight, birth date, college, currently active, hall of fame, link to webpage)
players = [[],
           [],
           [],
           [],
           [],
           [],
           [],
           [],
           [],
           [],
           []]

playersHeader = False


def scraper_main():
    global alphabet

    scraper_alphabet()

    #for i in alphabet:
    #    scraper_individual(i)

    scraper_individual('a')


def scraper_alphabet():
    global webURL
    global alphabet

    page = requests.get(webURL)
    tree = html.fromstring(page.content)

    alphabet = tree.xpath('//table//td[@class="align_center bold_text valign_bottom xx_large_text"]//a/text()')


def scraper_individual(firstLetter):
    global webURL
    global players
    global playersHeader

    newWebURL = webURL + firstLetter.lower()
    curPage = webURL[webURL.index('.com') + 4:]

    page = requests.get(newWebURL)
    tree = html.fromstring(page.content)

    for table in tree.xpath('//table'):
        header = [th.text_content() for th in table.xpath('//th')]
        data = [[td for td in tr.xpath('td')] for tr in table.xpath('//tr')]

        for tr in table.xpath('//tr'):
            for td in tr.xpath('td'):
                print td.text_content()
                bolded_text = td.xpath('//strong//a/text()')
                for i in bolded_text:
                    print i.text_content()

        bolded_Text = data[1][0].xpath('//strong//a/text()')

        link = data[1][0].xpath('//a/@href')
        link[:] = [url for url in link if (curPage in url) and (len(url) - len(curPage) > 2)]

        for i in range(len(data)):
            for j in range(len(data[i])):
                data[i][j] = data[i][j].text_content()

        data = [row for row in data if len(row) == len(header)]

        if playersHeader is False:
            for i in range(len(header)):
                players[i].append(header[i])

            players[8] = ['Active']
            players[9] = ['Hall Of Fame']
            players[10] = ['Webpage Link']

            playersHeader = True

        counter = 0

        for i in data:
            for j in range(len(header)):
                if j == 0:
                    # checks if player is in Hall of Fame
                    if '*' in i[j]:
                        players[9].append(True)
                        i[j] = i[j].replace("*", "")
                    else:
                        players[9].append(False)

                    # checks if player is currently active
                    # assumes that Hall of Fame players are not currently active (which is always true unless HOF eligibility rules are changed)
                    if i[j] in bolded_Text:
                        players[8].append(True)
                    else:
                        players[8].append(False)

                    # add link to webpage
                    players[10].append(link[counter])
                    counter = counter + 1

                players[j].append(i[j])


def convert_to_CSV():
    global players

    fileName = str(raw_input('What should we title this CSV file? ')) + '.csv'

    replaceExistingFile = False

    firstTime = True
    counter = 0

    while os.path.isfile(fileName) and not replaceExistingFile:
        replaceExistingFileRepeat = True

        while replaceExistingFileRepeat:
            replaceExistingFileString = str(raw_input('File ' + fileName + ' currently exists. Replace current file? '))

            if replaceExistingFileString == 'Yes' or replaceExistingFileString == 'Y' or replaceExistingFileString == 'yes' or replaceExistingFileString == 'y':
                replaceExistingFile = True
                replaceExistingFileRepeat = False
            elif replaceExistingFileString == 'No' or replaceExistingFileString == 'N' or replaceExistingFileString == 'no' or replaceExistingFileString == 'n':
                replaceExistingFileRepeat = False
                fileName = (fileName[:fileName.index('.')] + str(counter) + '.csv')
                counter = counter + 1

    file = open(fileName, 'w+')

    for i in range(len(players[0])):
        line = ''
        firstTime = True

        for j in range(len(players)):
            toInsert = ''

            if ',' in str(players[j][i]):
                toInsert = "\"" + str(players[j][i]) + "\""
            else:
                toInsert = str(players[j][i])

            if firstTime:
                line = toInsert
                firstTime = False
            else:
                line = line + ',' + toInsert

        file.write(line)
        file.write('\n')


def main():
    scraper_main()
    convert_to_CSV()


if __name__ == '__main__':
    main()
