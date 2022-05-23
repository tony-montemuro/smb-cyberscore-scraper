# This file contains the code for a python script used to scrape
# leaderboard information from cyberscore charts. In particular, this
# script is designed for Super Monkey Ball charts (SMB1, SMB2, SMBDX, etc.)
# The output of this script is a series of csv files, each of which contains
# the data for each chart of a particular category (ex: smb1 score charts)

# imports: beautiful soup for web scraping 
# requests for making HTTP requests
# csv for creating csv files with cyberscore data
# os for making a new directory to store csv files
# re for regex used to remove leading 0s from strings
from bs4 import BeautifulSoup
import requests
import os
import csv
import re

def get_chart_vals(game, mode):
    # this function takes in a game and a mode, and returns the
    # starting and finishing chart numbers for each combination
    # if game is not one of the following:
        # 1, 2, p, or d
    # and if mode is not one of the following:
        # s or t
    # -1 and -1 are returned, representing an error
    if game == '1':
        if mode == 's':
            return 1054, 1171
        if mode == 't':
            return 141568, 141666
    if game == '2':
        if mode == 's':
            return 1401, 1550
        if mode == 't':
            return 141667, 141684
            # return 141685, 141959
    if game == 'p':
        if mode == 's':
            return 22451, 22600
        if mode == 't':
            return 141804, 141949
    if game == 'd':
        if mode == 's':
            return 14888, 16412
        if mode == 't':
            return 141271, 141558

    # user misentered inputs. return error codes
    return -1, -1

def elongate(n):
    # takes in the abbreviation of a name n, and returns the
    # elongated version
    if n == '1': return 'smb1'
    if n == '2': return 'smb2'
    if n == 'p': return 'smb2pal'
    if n == 'd': return 'smbdx'
    if n == 's': return 'score'
    if n == 't': return 'time'

    # invalid n value, return error code
    return -1

def remove_leading_zeros_from_str(s):
    # uses regex to remove leading 0 from a string representing an int
    regex = '^0(?!$)'
    s = re.sub(regex, '', s)
    return s

def ith_index_of_element(i, l, element):
    # returns the index of the ith occurence of an element in a python list
    return [j for j, n in enumerate(l) if n == element][i-1]

def get_title(names, game, mode):
    # takes the text scraped from the chart title, and returns the properly
    # formatted name
    start = ith_index_of_element(2, names, '→')

    # special case: smb2 score. must remove the '→ high score -' prefix
    if (game == 'smb2' or game == 'smb2pal') and mode == 'score':
        start += 4

    # otherwise, just skip over the '→' prefix
    else:
        start += 1

    # now, we can finally create the name variable
    name = names[start].lower()
    for i in range(start+1, len(names)):
        current = names[i].lower()
        if current != '–':
            name += f'-{names[i].lower()}'
    return name

def format_name(name):
    # takes in an full username (first, username, and last), extracts
    # just the 'username', and removes the apostrophes
    names = name.split()
    for n in names:
        if '“' in n:
            name = n
    name = name.replace('“', '')
    name = name.replace('”', '')
    return name

def fetch_all_submissions(s, f, game, mode):
    # for each chart in the range s to f, fetch the chart submissions
    # there are some charts (see skipped_charts list and skipped_range pair) 
    # that should be ignored. if chart_num is one of these, scraping will not 
    # be performed on that chart
    skipped_charts = [1154, 16403, 141607, 141660, 141774]
    skipped_range = (15188, 16401)
    skipped_range_2 = (141804, 141949)
    extra_chart_smb1_score = 367365
    extra_chart_smb1_time = 367366

    # loop through each chart in the range from s to f, and fetch the
    # submissions from each
    for chart_num in range(s, f+1):
        valid_chart = True

        # check if a chart is valid
        for skipped in skipped_charts:
            if chart_num == skipped: 
                valid_chart = False
        if chart_num >= skipped_range[0] and chart_num <= skipped_range[1]:
            valid_chart = False
        if (chart_num >= skipped_range_2[0] and chart_num <= skipped_range_2[1]) and game == 'smb2':
            valid_chart = False


        # if valid, we can go ahead and scrape the datas
        if valid_chart:
            fetch_chart_submissions(chart_num, game, mode)
    
    # now, do extra charts (if necessary)
    if game == 'smb1' and mode == 'score':
        fetch_chart_submissions(extra_chart_smb1_score, game, mode)
    if game == 'smb1' and mode == 'time':
        fetch_chart_submissions(extra_chart_smb1_time, game, mode)
        

def fetch_chart_submissions(chartNum, game, mode):
    # request html data from chart, and create soup
    html_text = requests.get(f'https://cyberscore.me.uk/chart/{chartNum}').text
    soup = BeautifulSoup(html_text, 'lxml')

    # next, get the name of the chart
    unformatted_name = soup.find('h1', class_='gamename').text.split()
    name = get_title(unformatted_name, game, mode)
    print(f'Getting {name} data...')

    # next, set up object used to write to a csv file
    f = open(f'chart-info/{game}/{mode}/{name}.csv', 'w', newline='')
    csv_writer = csv.writer(f)
    csv_writer.writerow(['Position', 'Name', f'{mode.capitalize()}', 'Day', 'Month', 'Year', 'Monkey', 'Proof'])

    # get the list of all submissions
    submissions = soup.find_all('tr', class_='not-friend')
    for submission in submissions:
        fetch_submission(submission, csv_writer, mode)
    f.close()

def fetch_submission(s, csv_writer, mode):
    # blank list which will contain a row of data
    row = []

    # first, grab the position of the submission, as well as the name
    # of who submitted
    pos = s.find('td', class_='pos').text.replace(' ', '').strip()
    name = s.find('div', class_='user-identification').b.text
    name = format_name(name)

    # next, grab position, and split into an array of strings. this details
    # array contains the date of submission, as well as character used
    details = s.find('div', class_='details').small.text.split()
    date = details[0].split('-')
    year, month, day = date[0], remove_leading_zeros_from_str(date[1]), remove_leading_zeros_from_str(date[2])
    monkey = details[3]

    # then, grab the proof, if there is one. if the score retrieved does not
    # contain http, this means it retrieved different data, implying no 
    # proof exists
    proof = s.find('td', class_='data').a['href']
    if 'http' not in proof:
        proof = 'none'

    # then, grab the score/time
    score = s.find('span', class_='bigger').text
    if mode == 'time':
        score = score[2:]

    # now, append each element to row list
    row.append(pos)
    row.append(name)
    row.append(score)
    row.append(day)
    row.append(month)
    row.append(year)
    row.append(monkey)
    row.append(proof)

    # finally, write data to the csv file using csv_writer
    csv_writer.writerow(row)

def begin_scrape(game, mode):
    # first, get the value of the starting end finishing chart based
    # on the game and mode
    s, f = get_chart_vals(game, mode)
    if s == -1:
        print("Invalid inputs! Please restart and try again.")
        quit()
    game, mode = elongate(game), elongate(mode)
    if game == -1 or mode == -1:
        print('Error with elongate function. Shutting down...')
        quit()

    # create a directory to store the chart data
    dir = f'chart-info/{game}/{mode}'
    if not os.path.exists(dir):
        os.makedirs(dir)
        print(f'\n{dir} created.')
    else:
        print(f'\n{dir} already exists. Continuing...')
    
    # finally, run the scraping script
    print(f'\nBeginning data collection for {game} {mode}...\n')
    fetch_all_submissions(s, f, game, mode)
    print(f'\nData collection of {game} {mode} complete!')

def init_scrape_all():
    # set up a loop that will select all the game types for
    # scraping, and scrape
    game_list = ["1", "2", "p", "d"]
    mode_list = ["s", "t"]
    for game in game_list:
        for mode in mode_list:
            begin_scrape(game, mode)
    print('\nData collection complete!')

def init_scrape():
    # prompt user to enter which game they wish to get data for
    # then, begin scrape process
    print("Select a game (1 for SMB1, 2 for SMB2, p for SMB2 PAL, d for SMBDX:")
    game = input().lower()
    print("Time or score (t for Time, s for Score):")
    mode = input().lower()
    begin_scrape(game, mode)

if __name__ == "__main__":
    # ask the user if they wish to scrape the entire monkey ball
    # cyberscore boards, or just one particular section
    print('Would you like to gather all monkey ball data (a), or just one particular section? (s)')
    decision = input().lower()
    if decision == 'a':
        init_scrape_all()
    elif decision == 's':
        init_scrape()
    else:
        print('Invalid input! Please restart and try again')
        quit()