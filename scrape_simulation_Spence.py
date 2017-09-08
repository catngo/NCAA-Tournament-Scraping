from truth import *
import random
import requests
import csv
from bs4 import BeautifulSoup


#for the 2016 NCAA Bracket 
#DofURLs = {"UNC":"http://www.sports-reference.com/cbb/schools/north-carolina/2016.html","Kentucky":"http://www.sports-reference.com/cbb/schools/kentucky/2016.html"} # you guys can add more teams and URLs to this dictionary. Or write a funciton that would loop through the years and name

# Some quantifiable stats I would like to include but don't know how to scrape: avg height and/or weight, avg player experience, coach experience, program history, +- in final minutes(?) and more
# Should definitely include win/loss previous matchup type stuff but how do you quantify it?
LofStats = ['g', 'fg_pct', 'fga','fg2_pct', 'fg2a', 'fg3_pct', 'fg3a','ft_pct', 'fta','pts_per_g', 'orb', 'drb','ast', 'stl', 'blk','tov', 'pf', 'opp_fg_pct', 'opp_fg2_pct', 'opp_fg3_pct', 'opp_orb', 'opp_drb', 'opp_ast', 'opp_stl', 'opp_blk', 'opp_tov', 'opp_pf', 'opp_pts_per_g'] # you guys can add more stats to this list if you want. Note that ast, trb and tov only have stats for each players. Not the whole team stats.
numStats = len(LofStats)+1 #team name plus number of stats accounted for

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
    for i in range(2010,2017):
        d[i] = "http://www.sports-reference.com/cbb/postseason/"+str(i)+"-ncaa.html"
    return d

BracketURLs = getBracketURL()

def scrape(year):
    """ Use BeautifulSoup to scrape data from the URLs and return a List of List to export it as a csv file
    """
    TeamsURLs = getURLs(BracketURLs[year],year)
    L = [[str(year)]] #empty list where we store all stats of team
    for url in TeamsURLs:
        L += [[url[44:len(url)-10]]]
        html = gethtml(url)
        soup = BeautifulSoup(html.text,"lxml")
        for stat in LofStats:
            roughNumber = soup.find_all('td',{'data-stat':stat})
            neatNumber = [stat]
            neatNumber += getnumber(roughNumber)
            L += [neatNumber]
    write_to_csv(L,str(year)+".csv") #write to csv

def condenseBigList(L):
    """ Condenses the data for every team and every player to the usable team stats only
    """
    newL = []
    L = L[1:] #get rid of the first entry - year
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
    for i in range(len(L)):
        if (i%numStats != 0):
            newL += [float(L[i])]
            if (i%numStats >= 16 and i%numStats <= 25 or i%numStats == 28): #these stats are harmful (turnovers, fouls, etc), to keep comparisons consistent, take the opposite
                newL[i] *= -1
            if (i%numStats != 1 and i%numStats != 2 and i%numStats != 4 and i%numStats != 6 and i%numStats != 8 and i%numStats != 10 and i%numStats != 18 and i%numStats != 19 and i%numStats != 20 and i%numStats != 28):
                newL[i] = newL[i] / newL[int(i+1-i%numStats)] #some stats are only given as totals, so divide by number of games to get comparable data
        else:
            newL += [L[i]]
    return newL

def separateByTeam(L):
    """ Creates a dictionary with key of teamname and value of the list of that team's data
    """
    D = {}
    for i in range(len(L)):
        if (i%numStats == 0):
            D[L[i]] = L[i+1:i+numStats] #creates a dictionary with key of team0, team1, etc and value of the list of that teams data
    return D

def getTeamData(year):
    """ Returns the dictionary of the data for every team in the bracket of a given year
        Assumes the csv file has already been created (saves runtime)
    """
    allData = readcsv(str(year)+".csv")
    condensedData = condenseBigList(allData)
    usableData = turnToNumbers(condensedData)
    return separateByTeam(usableData)





def matchup(team1, team2, teamData, weight):
    total1 = 0
    total2 = 0
    for i in range(len(weight)):
        if (teamData[team1][i] > teamData[team2][i]):
            total1 += weight[i]
        elif (teamData[team1][i] < teamData[team2][i]):
            total2 += weight[i]
    if (total1 >= total2):
        return team1
    else:
        return team2




def generateResult(year, weight):
    """ Fill out a bracket for a given year with a given weighting vector
    """
    data = getTeamData(year)
    result = []
    currentRound = BRACKET[year]
    while (len(currentRound) > 1):
        nextRound = []
        for i in range(len(currentRound)):
            if (i%2 == 0):
                winner = matchup(currentRound[i], currentRound[i+1], data, weight)
                nextRound += [winner]
        result += [nextRound]
        currentRound = nextRound
    return result

def numMatches(trueResult, myResult, round):
    """ Calculates the number of matches between an input bracket and the true bracket
    """
    count = 0
    for i in range(len(trueResult[round])):
        if trueResult[round][i] in myResult[round]:
            count += 1
    return count

def compareResults(year, weight):
    """ Computes the score of a generated bracket
    """
    trueResult = RESULT[year]
    myResult = generateResult(year, weight)
    total = 0
    total += 10*numMatches(trueResult, myResult, 0)
    total += 20*numMatches(trueResult, myResult, 1)
    total += 40*numMatches(trueResult, myResult, 2)
    total += 80*numMatches(trueResult, myResult, 3)
    total += 160*numMatches(trueResult, myResult, 4)
    total += 320*numMatches(trueResult, myResult, 5)
    return total


def simulation(year1, year2, year3, year4):
    bestValue = 0
    bestWeight = []
    for trial in range(100):
        weight = [0]
        for i in range(numStats-2):
            weight += [random.randint(0,100)]
        value = compareResults(year1, weight) + compareResults(year2, weight) + compareResults(year3, weight) + compareResults(year4, weight)
        if (value > bestValue):
            bestValue = value
            bestWeight = weight
    return (bestValue/4, bestWeight)

def bestWeightForStat(year, stat):
    bestValue = 0
    bestWeight = 0
    weight = []
    for i in range(numStats-1):
        weight += [50]
    for i in range(0,101):
        weight[stat] = i
        value = compareResults(year, weight)
        if (value > bestValue):
            bestValue = value
            bestWeight = i
    return bestWeight

def oneByOne(year):
    weight = []
    for stat in range(numStats-1):
        weight += [bestWeightForStat(year, stat)]
    return weight








"""
The result of each tournament based on pre-tournament seeds
"""

RESULT = {
2016 : [
["kansas","connecticut","maryland","hawaii","wichita-state","miami-fl","arizona","villanova","oregon","saint-josephs","yale","duke","northern-iowa","texas-am","virginia-commonwealth","oklahoma","north-carolina","providence","indiana","kentucky","notre-dame","stephen-f-austin","wisconsin","xavier","virginia","butler","arkansas-little-rock","iowa-state","gonzaga","utah","syracuse","middle-tennessee"],
["kansas","maryland","miami-fl","villanova","oregon","duke","texas-am","oklahoma","north-carolina","indiana","notre-dame","wisconsin","virginia","iowa-state","gonzaga","syracuse"],
["kansas","villanova","oregon","oklahoma","north-carolina","notre-dame","virginia","syracuse"],
["villanova","oklahoma","syracuse","north-carolina"],
["villanova","north-carolina"],
["villanova"]
]
,
2015 : [
["kentucky","cincinnati","west-virginia","maryland","butler","notre-dame","wichita-state","kansas","wisconsin","oregon","arkansas","north-carolina","xavier","georgia-state","ohio-state","arizona","villanova","north-carolina-state","northern-iowa","louisville","dayton","oklahoma","michigan-state","virginia","duke","san-diego-state","utah","georgetown","ucla","alabama-birmingham","iowa","gonzaga"],
["kentucky","west-virginia","notre-dame","wichita-state","wisconsin","north-carolina","xavier","arizona","north-carolina-state","louisville","oklahoma","michigan-state","duke","utah","ucla","gonzaga"],
["kentucky","notre-dame","wisconsin","arizona","louisville","michigan-state","duke","gonzaga"],
["kentucky","wisconsin","michigan-state","duke"],
["wisconsin","duke"],
["duke"]
]
,
2014 : [
["florida","pittsburgh","stephen-f-austin","ucla","dayton","syracuse","stanford","kansas","virginia","memphis","harvard","michigan-state","north-carolina","iowa-state","connecticut","villanova","arizona","gonzaga","north-dakota-state","san-diego-state","baylor","creighton","oregon","wisconsin","wichita-state","kentucky","saint-louis","louisville","tennessee","mercer","texas","michigan"],
["florida","ucla","dayton","stanford","virginia","michigan-state","iowa-state","connecticut","arizona","san-diego-state","baylor","wisconsin","kentucky","louisville","tennessee","michigan"],
["florida","dayton","connecticut","michigan-state","arizona","wisconsin","kentucky","michigan"],
["florida","connecticut","wisconsin","kentucky"],
["connecticut","kentucky"],
["connecticut"]
]
,
2013 : [
["louisville","colorado-state","oregon","saint-louis","memphis","michigan-state","creighton","duke","gonzaga","wichita-state","mississippi","la-salle","arizona","harvard","iowa-state","ohio-state","kansas","north-carolina","virginia-commonwealth","michigan","minnesota","florida","san-diego-state","florida-gulf-coast","indiana","temple","california","syracuse","butler","marquette","illinois","miami-fl"],
["louisville","oregon","michigan-state","duke","wichita-state","la-salle","arizona","ohio-state","kansas","michigan","florida","florida-gulf-coast","indiana","syracuse","marquette","miami-fl"],
["louisville","duke","wichita-state","ohio-state","michigan","florida","syracuse","marquette"],
["louisville","wichita-state","michigan","syracuse"],
["louisville","michigan"],
["louisville"]
]
,
2012 : [
["S1","S8","S12","S4","S11","S3","S10","S15","W1","W9","W5","W4","W6","W3","W7","W15","E1","E8","E5","E4","E6","E3","E7","E2","E1","E4","E6","E2","M1","M8","M12","M13","M11","M3","M10","M2"],
["S1","S4","S3","S10","W1","W4","W3","W4","W7","E1","E4","E6","E2","M1","M13","M11","M2"],
["S1","S3","W4","W7","E1","E2","M1","M2"],
["S1","W4","E2","M2"],
["S1","M2"],
["S1"]
]
,
# For 2011, S is Southeast and M is for Southwest

2011 : [
["E1","E8","E5","E4","E11","E3","E7","E2","W1","W8","W5","W4","W6","W3","W7","W2","M1","M9","M12","M13","M11","M3","M10","M2","S1","S8","S5","S4","S11","S3","S7","S2"],
["E1","E4","E11","E2","W1","W5","W3","W2","M1","M12","M11","M10","S8","S4","S3","S2"],
["E4","E2","W5","W3","M1","M11","S8","S2"],
["E4","W3","M11","S8"],
["W3","S8"],
["W3"]
]
,
2010 : [
["M1","M9","M5","M4","M6","M14","M10","M2","W1","W8","W5","W13","W16","W3","W7","W2","E1","E9","E12","E4","E11","E3","E10","E2","S1","S8","S5","S4","S11","S3","S10","S2"],
["M9","M5","M6","M2","W1","W5","W6","W2","E1","E12","E11","E2","S1","S4","S3","S10"],
["M5","M6","W5","W2","E1","E2","S1","S3"],
["M5","W5","E2","S1"],
["W5","S1"],
["S1"]
]
}

BRACKET = {

2016 : ["kansas","austin-peay","colorado","connecticut","maryland","south-dakota-state","california","hawaii","arizona","wichita-state","miami-fl","buffalo","iowa","temple","villanova","north-carolina-asheville","oregon","holy-cross","saint-josephs","cincinnati","baylor","yale","duke","north-carolina-wilmington","texas","northern-iowa","texas-am","green-bay","oregon-state","virginia-commonwealth","oklahoma","cal-state-bakersfield","north-carolina","florida-gulf-coast","southern-california","providence","indiana","chattanooga","kentucky","stony-brook","notre-dame","michigan","west-virginia","stephen-f-austin","wisconsin","pittsburgh","xavier","weber-state","virginia","hampton","texas-tech","butler","purdue","arkansas-little-rock","iowa-state","iona","seton-hall","gonzaga","utah","fresno-state","dayton","syracuse","michigan-state","middle-tennessee"],

2015: ["duke","robert-morris","san-diego-state","st-johns-ny","utah","stephen-f-austin","georgetown","eastern-washington","southern-methodist","ucla","iowa-state","alabama-birmingham","iowa","davidson","gonzaga","north-dakota-state","villanova","lafayette","north-carolina-state","louisiana-state","northern-iowa","wyoming","louisville","california-irvine","providence","dayton","oklahoma","albany-ny","michigan-state","georgia","virginia","belmont","wisconsin","coastal-carolina","oregon","oklahoma-state","arkansas","wofford","north-carolina","harvard","xavier","mississippi","baylor","georgia-state","virginia-commonwealth","ohio-state","arizona","texas-southern","kentucky","hampton","cincinnati","purdue","west-virginia","buffalo","maryland","valparaiso","butler","texas","notre-dame","northeastern","wichita-state","indiana","kansas","new-mexico-state"],

2014: ["florida","albany-ny","colorado","pittsburgh","virginia-commonwealth","stephen-f-austin","ucla","tulsa","ohio-state","dayton","syracuse","western-michigan","new-mexico","stanford","kansas","eastern-kentucky","virginia","coastal-carolina","memphis","george-washington","cincinnati","harvard","michigan-state","delaware","north-carolina","providence","iowa-state","north-carolina-central","connecticut","saint-josephs","villanova","milwaukee","arizona","weber-state","gonzaga","oklahoma-state","oklahoma","north-dakota-state","san-diego-state","new-mexico-state","baylor","nebraska","creighton","louisiana-lafayette","oregon","brigham-young","wisconsin","american","wichita-state","cal-poly","kentucky","kansas-state","saint-louis","north-carolina-state","louisville","manhattan","massachusetts","tennessee","duke","mercer","texas","arizona-state","michigan","wofford"],

2013: ["kansas","western-kentucky","north-carolina","villanova","virginia-commonwealth","akron","michigan","south-dakota-state","ucla","minnesota","florida","northwestern-state","san-diego-state","oklahoma","georgetown","florida-gulf-coast","indiana","james-madison","north-carolina-state","temple","nevada-las-vegas","california","syracuse","montana","butler","bucknell","marquette","davidson","illinois","colorado","miami-fl","pacific","gonzaga","southern","pittsburgh","wichita-state","wisconsin","mississippi","kansas-state","la-salle","arizona","belmont","new-mexico","harvard","notre-dame","iowa-state","ohio-state","iona","louisville","north-carolina-at","colorado-state","missouri","oklahoma-state","oregon","saint-louis","new-mexico-state","memphis","saint-marys-ca","michigan-state","valparaiso","creighton","cincinnati","duke","albany-ny"],

2012 : ["S1","S16","S8","S9","S5","S12","S4","S13","S6","S11","S3","S14","S7","S10","S2","S15","W1","W16","W8","W9","W5","W12","W4","W13","W6","W11","W3","W14","W7","W10","W2","W15","E1","E16","E8","E9","E5","E12","E4","E13","E6","E11","E3","E14","E7","E10","E2","E15","M1","M16","M8","M9","M5","M12","M4","M13","M6","M11","M3","M14","M7","M10","M2","M15"],

# For 2011, S is Southeast and M is for Southwest
2011: ["W1","W16","W8","W9","W5","W12","W4","W13","W6","W11","W3","W14","W7","W10","W2","W15","E1","E16","E8","E9","E5","E12","E4","E13","E6","E11","E3","E14","E7","E10","E2","E15","M1","M16","M8","M9","M5","M12","M4","M13","M6","M11","M3","M14","M7","M10","M2","M15","S1","S16","S8","S9","S5","S12","S4","S13","S6","S11","S3","S14","S7","S10","S2","S15"],

2010 : ["S1","S16","S8","S9","S5","S12","S4","S13","S6","S11","S3","S14","S7","S10","S2","S15","E1","E16","E8","E9","E5","E12","E4","E13","E6","E11","E3","E14","E7","E10","E2","E15","W1","W16","W8","W9","W5","W12","W4","W13","W6","W11","W3","W14","W7","W10","W2","W15","M1","M16","M8","M9","M5","M12","M4","M13","M6","M11","M3","M14","M7","M10","M2","M15"],

}