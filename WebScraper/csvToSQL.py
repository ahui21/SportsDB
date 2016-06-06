# TODO: find alternative if table is not to be dropped and should be updated
#       instead
# TODO: include alternatives for double, integer, and string
# TODO: automate data type selections for each
# TODO: check if fields match data types given

# Description:  A Python program that takes in a command-line argument of a csv
#               file and then converts it into a SQL dump file.
# Written by:   Alwin Hui (ahui21)
# Created:      June 2nd, 2016

import sys
import csv
import os
import io

fileName = ''
tableName = ''
dropTable = False
data = []
dataTypes = []
sqlFileName = ''
reservedKeywords = ['Date', 'From', 'To']


def parse_args():
    global fileName

    if len(sys.argv) == 2:
        fileName = sys.argv[1]
    else:
        raise ValueError('Incorrect number of arguments (%i) found.' %
                         len(sys.argv))


def parse_inputs():
    global tableName
    global dropTable

    tableName = (str(raw_input('\nEnter the name of the '
                               'table: '))).replace(" ", "_")

    dropTableRepeat = True

    while dropTableRepeat:
        dropTableString = str(raw_input('If this table already exists, shall '
                                        'we drop it? '))

        if dropTableString == 'Yes' or dropTableString == 'Y'
        or dropTableString == 'yes' or dropTableString == 'y':
            dropTable = True
            dropTableRepeat = False
        elif dropTableString == 'No' or dropTableString == 'N'
        or dropTableString == 'no' or dropTableString == 'n':
            dropTableRepeat = False


def parse_csv():
    global fileName
    global data
    global dataTypes
    global reservedKeywords

    longestLength = 0

    with io.open(fileName, encoding='utf-8-sig') as csvFile:
        reader = csv.reader(csvFile)
        firstRow = True
        rowLength = 0

        for row in reader:
            if firstRow:
                firstRow = False
                rowLength = len(row)
                longestLength = len(max(row, key=len))

                for i in range(rowLength):
                    data.append([])

            currentRowLength = len(row)

            for i in range(rowLength):
                if currentRowLength > 0:
                    data[i].append(row[i])
                    currentRowLength = currentRowLength - 1
                else:
                    data[i].append('')

    print ''

    for i in range(len(data)):
        typeStringRepeat = True
        dataType = ''

        while typeStringRepeat:
            typeString = str(raw_input('What type of variable is \"' +
                                       data[i][0] + '\" (double, integer, '
                                       'string, other)? '))

            if typeString == 'double' or typeString == 'Double':
                digits1 = int(raw_input('How many digits before the decimal to'
                                        ' be allocated? '))
                digits2 = int(raw_input('How many digits after the decimal to '
                                        'be allocated? '))

                dataType = ('NUMERIC(' + str(digits1 + digits2) + ',' +
                            str(digits2) + ') ')

                typeStringRepeat = False

            elif typeString == 'integer' or typeString == 'Integer'
            or typeString == 'int' or typeString == 'Int':
                dataType = 'INTEGER '

                typeStringRepeat = False

            elif typeString == 'string' or typeString == 'String':
                chars = int(raw_input('How many characters to be '
                                      'allocated? '))

                dataType = 'VARCHAR(' + str(chars) + ') '

                typeStringRepeat = False

            elif typeString == 'other' or typeString == 'Other':
                print 'This functionality is currently not supported.'
                break

            if not typeStringRepeat:
                nullRepeat = True

                while nullRepeat:
                    null = str(raw_input('Can this field be null? '))

                    if null == 'Yes' or null == 'Y' or null == 'yes'
                    or null == 'y':
                        nullRepeat = False
                    elif null == 'No' or null == 'N' or null == 'no'
                    or null == 'n':
                        dataType = dataType + ' NOT NULL'
                        nullRepeat = False

            print ''

    column_name_cleanup()

    for i in range(len(data)):
        spaces = ''

        for j in range(longestLength - len(data[i][0]) + 1):
            spaces = spaces + ' '

        dataTypes.append(data[i][0] + spaces + dataType)


def column_name_cleanup():
    global data

    # if column names match reserved keywords, modify them slightly
    for i in range(len(data)):
        if data[i][0] in reservedKeywords:
            data[i][0] = data[i][0] + '_'

    # modify column names to PascalCase
    for i in range(len(data)):
        finalColumnName = ''

        for j in data[i][0].split():
            finalColumnName = finalColumnName + j.capitalize()

        data[i][0] = finalColumnName


def create_SQL():
    global tableName
    global dropTable
    global fileName
    global sqlFileName
    global dataTypes
    global data

    condensedFileName = fileName[fileName.rfind('/') + 1:]

    sqlFileName = (condensedFileName[:condensedFileName.rfind('.')] +
                   '_dump.sql')

    replaceExistingFile = False

    firstTime = True
    counter = 0

    while os.path.isfile(sqlFileName) and not replaceExistingFile:
        replaceExistingFileRepeat = True

        while replaceExistingFileRepeat:
            replaceExistingFileString = str(raw_input('File ' + sqlFileName +
                                                      ' currently exists. '
                                                      'Replace current '
                                                      'file? '))

            if replaceExistingFileString == 'Yes'
            or replaceExistingFileString == 'Y'
            or replaceExistingFileString == 'yes'
            or replaceExistingFileString == 'y':
                replaceExistingFile = True
                replaceExistingFileRepeat = False
            elif replaceExistingFileString == 'No'
            or replaceExistingFileString == 'N'
            or replaceExistingFileString == 'no'
            or replaceExistingFileString == 'n':
                replaceExistingFileRepeat = False
                sqlFileName = (sqlFileName[:sqlFileName.index('.')] +
                               str(counter) + '.sql')
                counter = counter + 1

    sqlFile = open(sqlFileName, 'w+')

    sqlFile.write('/* SQL statements automatically generated from ' +
                  condensedFileName + ' */')
    sqlFile.write('\n')
    sqlFile.write('\n')

    if dropTable:
        sqlFile.write('DROP TABLE IF EXISTS ' + tableName + ';')
        sqlFile.write('\n')
        sqlFile.write('\n')
        sqlFile.write('CREATE TABLE IF NOT EXISTS ' + tableName + '(')
        sqlFile.write('\n')

    firstDataType = True
    for i in dataTypes:
        if firstDataType:
            sqlFile.write('   ' + i)
            sqlFile.write('\n')
            firstDataType = False
        else:
            sqlFile.write('  ,' + i)
            sqlFile.write('\n')

    sqlFile.write(');')
    sqlFile.write('\n')
    sqlFile.write('\n')

    prequel = 'INSERT INTO ' + tableName + '('

    firstTime = True

    for i in data:
        if firstTime:
            prequel = prequel + i[0]
            firstTime = False
        else:
            prequel = prequel + ',' + i[0]

    prequel = prequel + ') VALUES ('

    firstRow = True

    for i in range(len(data[0])):
        if firstRow:
            firstRow = False
        else:
            total = ''
            firstTime = True
            numeric = False
            empty = False

            for j in range(len(data)):
                if 'INTEGER ' in dataTypes[j] or 'NUMERIC' in dataTypes[j]:
                    numeric = True
                else:
                    numeric = False

                if not data[j][i]:
                    empty = True
                else:
                    empty = False

                # if data[j][i] includes a single quotation mark, double up on
                # the single quote
                toBeEntered = data[j][i]

                if '\'' in data[j][i]:
                    toBeEntered = (toBeEntered[:toBeEntered.index('\'')] +
                                   '\'' +
                                   toBeEntered[toBeEntered.index('\''):])

                if firstTime:
                    if empty:
                        total = prequel + 'NULL'
                    elif numeric:
                        total = prequel + toBeEntered
                    else:
                        total = prequel + '\'' + toBeEntered + '\''
                    firstTime = False
                else:
                    if empty:
                        total = total + ',NULL'
                    elif numeric:
                        total = total + ',' + toBeEntered
                    else:
                        total = total + ',\'' + toBeEntered + '\''
            total = total + ');'

            sqlFile.write(total)
            sqlFile.write('\n')


def main():
    parse_args()
    parse_inputs()
    parse_csv()
    create_SQL()


if __name__ == '__main__':
    main()
