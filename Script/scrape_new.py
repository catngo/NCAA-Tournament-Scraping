import requests
import csv
from bs4 import BeautifulSoup
import numpy as np


#for the 2016 NCAA Bracket 
#DofURLs = {"UNC":"http://www.sports-reference.com/cbb/schools/north-carolina/2016.html","Kentucky":"http://www.sports-reference.com/cbb/schools/kentucky/2016.html"} # you guys can add more teams and URLs to this dictionary. Or write a funciton that would loop through the years and name
LofStats = ['g', 'fg_pct', 'fga','fg2_pct', 'fg2a', 'fg3_pct', 'fg3a','ft_pct', 'fta','pts_per_g', 'orb', 'drb','ast', 'stl', 'blk','tov', 'pf', 'opp_fg_pct', 'opp_fg2_pct', 'opp_fg3_pct', 'opp_orb', 'opp_drb', 'opp_ast', 'opp_stl', 'opp_blk', 'opp_tov', 'opp_pf', 'opp_pts_per_g'] # you guys can add more stats to this list if you want. Note that ast, trb and tov only have stats for each players. Not the whole team stats.
numStats = len(LofStats)+4 #team name and strength of schedule, Offensive and Defensive Ratings plus number of stats accounted for



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

def readcsv( csv_file_name ):
    """ readcsv takes as
         + input:  csv_file_name, the name of a csv file
        and returns
         + output: a list of lists, each inner list is one row of the csv
           all data items are strings; empty cells are empty strings
    """
    try:
        csvfile = open( csv_file_name, newline='' )  # open for reading
        csvrows = csv.reader( csvfile )              # creates a csvrows object

        all_rows = []                               # we need to read the csv file
        for row in csvrows:                         # into our own Python data structure
            all_rows.append( row )                  # adds only the word to our list

        del csvrows                                  # acknowledge csvrows is gone!
        csvfile.close()                              # and close the file
        return all_rows                              # return the list of lists

    except FileNotFoundError as e:
        print("File not found: ", e)
        return []

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
        word = td.text.split()
        if word == []: # some players don't have stats for certain categories so the website leave it blank. This makes sure it says 0
            word = '0'
        L += word
    return L

number = ['SOS:','ORtg:','DRtg:']

def getOtherStat(result):
    """ Get soup.findall of 'p' and convert into a list with numbers and tag
    """
    L = []
    for p in result:
        word = p.text.split()
        if word[0] in number:
            L += [word[:2]]
    return L
    

def getURLs(url,year):
    """ From a link of the Bracket (e.g. http://www.sports-reference.com/cbb/postseason/2015-ncaa.html), get a list of links of all the participating schools
    """
    html = gethtml(url)
    soup = BeautifulSoup(html.text,"lxml")
    L = []
    for anchor in soup.findAll('a', href=True):
        if "schools" in anchor['href'] and str(year) in anchor['href']:
            L += [anchor['href']]
    L = L[4:] #remove the first four because that's the final four
    R = []
    for i in L:
        if "http://www.sports-reference.com"+ i not in R:
            R += ["http://www.sports-reference.com"+i]
    return R

def getBracketURL():
    """ Get bracket URLs from 2016 to 2010
    """
    d ={}
    for i in range(2010,2018):
        d[i] = "http://www.sports-reference.com/cbb/postseason/"+str(i)+"-ncaa.html"
    return d

BracketURLs = getBracketURL()

def scrape(year):
    """ Use BeautifulSoup to scrape data from the URLs and return a List of List to export it as a csv file
    """
    TeamsURLs = getURLs(BracketURLs[year],year)
    L = [] #empty list where we store all stats of team
    for url in TeamsURLs:
        L += [[url[44:len(url)-10]]]
        html = gethtml(url)
        soup = BeautifulSoup(html.text,"lxml")
        for stat in LofStats:
            roughNumber = soup.find_all('td',{'data-stat':stat})
            neatNumber = [stat]
            neatNumber += getnumber(roughNumber)
            L += [neatNumber]
        stat = soup.find_all('p',)
        stuff = getOtherStat(stat) # for more stats
        L += stuff
    write_to_csv(L,str(year)+".csv") #write to csv

def condenseBigList(L):
    """ Condenses the data for every team and every player to the usable team stats only
    """
    newL = []
    for i in range(len(L)):
        if (i%(numStats) == 0):
            newL += L[i]
        else:
            newL += L[i][1:2] #only care about team stats, not player stats
    return newL

def turnToNumbers(L):
    """ Turns the strings of numbers to float type numbers and modifies necessary stats
    """
    newL = []
    LofSOS = []
    for i in range(len(L)):
        if (i%numStats != 0): #avoid the team name
            newL += [float(L[i])]
            if (i%numStats >= 16 and i%numStats <= 25 or i%numStats == 28 or i%numStats == 31): #these stats are harmful (turnovers, fouls, etc), to keep comparisons consistent, take the opposite
                newL[i] *= -1
            if i%numStats == 29:
                LofSOS += [float(L[i])]
            if (i%numStats != 1 and i%numStats != 2 and i%numStats != 4 and i%numStats != 6 and i%numStats != 8 and i%numStats != 10 and i%numStats != 18 and i%numStats != 19 and i%numStats != 20 and i%numStats != 28 and i%numStats != 31 and i%numStats != 30 and i%numStats != 29):
                newL[i] = newL[i] / newL[int(i+1-i%numStats)] #some stats are only given as totals, so divide by number of games to get comparable data
        else:
            newL += [L[i]]
    highestSOS = max(LofSOS) # start of weighing the stats based on SOS
    lowestSOS = min(LofSOS)
    return weigh(newL,lowestSOS,highestSOS,LofSOS)

def weigh(newL,low,high,LofSOS):
    """ Weigh a list of stats based on each team's SOS 
    """
    index = 0
    LofWeight = []
    for i in range(len(LofSOS)):
        weight = getWeight(low,high,LofSOS[i])
        LofWeight += [weight]
    for weight in LofWeight:
        index = LofWeight.index(weight)
        for stat in range(numStats):
            if stat == 0 or stat == 29 :
                continue # ignore the name and SOS
            else:
                if newL[stat+numStats*index] > 0:
                    newL[stat+numStats*index] *= weight
                else: newL[stat+numStats*index] *= (1/weight)
    return newL

def separateByTeam(L):
    """ Creates a dictionary with key of teamname and value of the list of that team's data
    """
    D = {}
    for i in range(len(L)):
        if (i%numStats == 0):
            D[L[i]] = L[i+1:i+numStats] #creates a dictionary with key of team0, team1, etc and value of the list of that teams data
    for key in D:
        del(D[key][28]) #take out SOS
        D[key] = D[key][1:] #cut out the number of games
    return D

def getTeamData(year):
    """ returns the dictionary of the data for every team in the bracket of a given year
     """
    # scrape(year)
    allData = readcsv(str(year)+".csv")
    condensedData = condenseBigList(allData)
    usableData = turnToNumbers(condensedData)
    return separateByTeam(usableData)

def scrapeAll():
    """ Scrape all 7 years
    """
    for key in BracketURLs:
        scrape(key)

def getAllDict():
    """ Get all the dictionary
    """
    for year in range(2010,2018):
        d = getTeamData(year)
        np.save(str(year)+'.npy', d)

lower_lim = 0.8
high_lim = 1

def getWeight(low,high,own):
    """ Based on the lowest and highest SOS and the team's own SOS Have a weight to team stats based on SRS
    """
    total = high - low
    return (high_lim-lower_lim)*((own-low)/total) + lower_lim

def scrape2017(L):
    """ Use a list of URLs from 2017
    """
    TeamsURLs = L
    L = [] #empty list where we store all stats of team
    for url in TeamsURLs:
        L += [[url[44:len(url)-10]]]
        html = gethtml(url)
        soup = BeautifulSoup(html.text,"lxml")
        for stat in LofStats:
            roughNumber = soup.find_all('td',{'data-stat':stat})
            neatNumber = [stat]
            neatNumber += getnumber(roughNumber)
            L += [neatNumber]
        stat = soup.find_all('p',)
        stuff = getOtherStat(stat) # for more stats
        L += stuff
    write_to_csv(L,"2017.csv")

List2017 = ['http://www.sports-reference.com/cbb/schools/villanova/2017.html',
 'http://www.sports-reference.com/cbb/schools/mount-st-marys/2017.html',
 'http://www.sports-reference.com/cbb/schools/wisconsin/2017.html',
 'http://www.sports-reference.com/cbb/schools/virginia-tech/2017.html',
 'http://www.sports-reference.com/cbb/schools/virginia/2017.html',
 'http://www.sports-reference.com/cbb/schools/north-carolina-wilmington/2017.html',
 'http://www.sports-reference.com/cbb/schools/florida/2017.html',
 'http://www.sports-reference.com/cbb/schools/east-tennessee-state/2017.html',
 'http://www.sports-reference.com/cbb/schools/southern-methodist/2017.html',
 'http://www.sports-reference.com/cbb/schools/southern-california/2017.html',
 'http://www.sports-reference.com/cbb/schools/baylor/2017.html',
 'http://www.sports-reference.com/cbb/schools/new-mexico-state/2017.html',
 'http://www.sports-reference.com/cbb/schools/south-carolina/2017.html',
 'http://www.sports-reference.com/cbb/schools/marquette/2017.html',
 'http://www.sports-reference.com/cbb/schools/duke/2017.html',
 'http://www.sports-reference.com/cbb/schools/troy/2017.html',
 'http://www.sports-reference.com/cbb/schools/north-carolina-central/2017.html',
 'http://www.sports-reference.com/cbb/schools/kansas/2017.html',
 'http://www.sports-reference.com/cbb/schools/miami-fl/2017.html',
 'http://www.sports-reference.com/cbb/schools/michigan-state/2017.html',
 'http://www.sports-reference.com/cbb/schools/iowa-state/2017.html',
 'http://www.sports-reference.com/cbb/schools/nevada/2017.html',
 'http://www.sports-reference.com/cbb/schools/purdue/2017.html',
 'http://www.sports-reference.com/cbb/schools/vermont/2017.html',
 'http://www.sports-reference.com/cbb/schools/creighton/2017.html',
 'http://www.sports-reference.com/cbb/schools/rhode-island/2017.html',
 'http://www.sports-reference.com/cbb/schools/oregon/2017.html',
 'http://www.sports-reference.com/cbb/schools/iona/2017.html',
 'http://www.sports-reference.com/cbb/schools/michigan/2017.html',
 'http://www.sports-reference.com/cbb/schools/oklahoma-state/2017.html',
 'http://www.sports-reference.com/cbb/schools/louisville/2017.html',
 'http://www.sports-reference.com/cbb/schools/jacksonville-state/2017.html',
 'http://www.sports-reference.com/cbb/schools/north-carolina/2017.html',
 'http://www.sports-reference.com/cbb/schools/texas-southern/2017.html',
 'http://www.sports-reference.com/cbb/schools/arkansas/2017.html',
 'http://www.sports-reference.com/cbb/schools/seton-hall/2017.html',
 'http://www.sports-reference.com/cbb/schools/minnesota/2017.html',
 'http://www.sports-reference.com/cbb/schools/middle-tennessee/2017.html',
 'http://www.sports-reference.com/cbb/schools/butler/2017.html',
 'http://www.sports-reference.com/cbb/schools/winthrop/2017.html',
 'http://www.sports-reference.com/cbb/schools/cincinnati/2017.html',
 'http://www.sports-reference.com/cbb/schools/kansas-state/2017.html',
 'http://www.sports-reference.com/cbb/schools/ucla/2017.html',
 'http://www.sports-reference.com/cbb/schools/kent-state/2017.html',
 'http://www.sports-reference.com/cbb/schools/dayton/2017.html',
 'http://www.sports-reference.com/cbb/schools/wichita-state/2017.html',
 'http://www.sports-reference.com/cbb/schools/kentucky/2017.html',
 'http://www.sports-reference.com/cbb/schools/northern-kentucky/2017.html',
 'http://www.sports-reference.com/cbb/schools/gonzaga/2017.html',
 'http://www.sports-reference.com/cbb/schools/south-dakota-state/2017.html',
 'http://www.sports-reference.com/cbb/schools/northwestern/2017.html',
 'http://www.sports-reference.com/cbb/schools/vanderbilt/2017.html',
 'http://www.sports-reference.com/cbb/schools/notre-dame/2017.html',
 'http://www.sports-reference.com/cbb/schools/princeton/2017.html',
 'http://www.sports-reference.com/cbb/schools/west-virginia/2017.html',
 'http://www.sports-reference.com/cbb/schools/bucknell/2017.html',
 'http://www.sports-reference.com/cbb/schools/maryland/2017.html',
 'http://www.sports-reference.com/cbb/schools/xavier/2017.html',
 'http://www.sports-reference.com/cbb/schools/florida-state/2017.html',
 'http://www.sports-reference.com/cbb/schools/florida-gulf-coast/2017.html',
 'http://www.sports-reference.com/cbb/schools/saint-marys-ca/2017.html',
 'http://www.sports-reference.com/cbb/schools/virginia-commonwealth/2017.html',
 'http://www.sports-reference.com/cbb/schools/arizona/2017.html',
 'http://www.sports-reference.com/cbb/schools/north-dakota/2017.html']