This python script was made to take data stored on the following pages:
    
    -Super Monkey Ball (https://cyberscore.me.uk/game/16)
    -Super Monkey Ball 2 - NTSC (https://cyberscore.me.uk/game/20)
    -Super Monkey Ball 2 - PAL (https://cyberscore.me.uk/game/247)
    -Super Monkey Ball Deluxe (https://cyberscore.me.uk/game/184)
    
and store it locally. This is as a means of backup, just in-case cyberscore goes down in the future. If you would like to run this script yourself, here are the instructions. (NOTE: You must have python 3 installed on your machine.)

1.) Download this repository as a zip, and extract the files.

2.) Open the terminal, and move to the directory containing the extracted files.

3.) Then, run the following command in the terminal:

    python smb_cs_scrape.py
    
4.) The program will then begin in the terminal. From here, you will be asked if you wish to gather all the data from cyberscore, or just one particular section. If you choose to gather all the data, the program will immediately begin scraping cyberscore. If not, you will then be prompted to select which section you wish to collect. Once you have made your choice, the program will begin.

5.) Once execution is compete, you will have a new directory called 'chart-data,' which contains all of the cyberscore data for each game and mode of choice.
