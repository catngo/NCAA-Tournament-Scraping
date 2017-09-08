import requests
import csv
from bs4 import BeautifulSoup


#for the 2016 NCAA Bracket 
DofURLs = {"UNC":"http://www.sports-reference.com/cbb/schools/north-carolina/2016-schedule.html"} # you guys can add more teams and URLs to this dictionary. Or write a funciton that would loop through the years and name
LofStats = ['opp_name','pts','opp_pts','date_game','game_location','game_type'] # you guys can add more stats to this list if you want. Note that ast, trb and tov only have stats for each players. Not the whole team stats.

def gethtml(link):
    """ Get html file from link
    """
    html = requests.get(link)
    return html

def getnumber(result):
    """ Take in the result of soup.find_all and convert it to a list with only numbers
    """
    L = []
    for td in result:
        print(td)
        word = [td.text]#split()
        if word == []: # some players don't have stats for certain categories so the website leave it blank. This makes sure it says 0
            word = '0'
        print(word)
        L += word
    return L

def scrape():
    """ Use BeautifulSoup to scrape data from the URLs and return a List of List to export it as a csv file
    """

    for key in DofURLs:
        L = [] #empty list where we store all stats of team
        html = gethtml(DofURLs[key])
        soup = BeautifulSoup(html.text,"lxml")
        for stat in LofStats:
            roughNumber = soup.find_all('td',{'data-stat':stat})
            neatNumber = [stat]
            print(neatNumber)
            neatNumber += getnumber(roughNumber)
            L += [neatNumber]
        write_to_csv(L,key+".csv") #write to csv


def write_to_csv( list_of_rows, filename ):
    """ write csv takes a list of list and write them out as csv files
    """
    try:
        csvfile = open( filename, "w", newline='' )
        filewriter = csv.writer( csvfile, delimiter=",")
        for row in list_of_rows:
            filewriter.writerow( row )
        csvfile.close()
    except:
        print("File", filename, "could not be opened for writing...")