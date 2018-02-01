from result_with_names import *
import random
import numpy as np

start_year = 2010
end_year = 2018
no_of_stats = 29

d2010 = np.load('2010.npy').item()
d2011 = np.load('2011.npy').item()
d2012 = np.load('2012.npy').item()
d2013 = np.load('2013.npy').item()
d2014 = np.load('2014.npy').item()
d2015 = np.load('2015.npy').item()
d2016 = np.load('2016.npy').item()
d2017 = np.load('2017.npy').item()

D = [d2010,d2011,d2012,d2013,d2014,d2015,d2016,d2017]

class Team:
    def __init__(self,name,year,program):
        """ Define the team, data is the stats that will be analyzed, and ranking is the string of the ranked in tournament (like S1), and the year of the bracket, and the program that calculated the data
        """
        self.name = name
        self.data = D[year-start_year][name]
        self.program = program
    
    def __repr__(self):
        """ Print self
        """
        p = str(self.name)
        return p
    
    def play(self,t2):
        """ Take in two variables class Team and determine winner in head to head matchup based on each data
        """
        rankself = dot(self.data,self.program.rules)
        rankt2 = dot(t2.data,t2.program.rules)
        if rankself > rankt2:
            return self
        elif rankself < rankt2:
            return t2
        else:
            if self.data[6] > t2.data[6]: #this is free throws pct bc why not
                return self
            else:
                return t2
    
class Program: # program is how to evalutate the stats of each team and give a score
    def __init__(self):
        """ Define it 
        """
        self.rules = [] 

    def __repr__(self):
        return(str(self.rules))
    
    def randomize(self):
        for i in range(no_of_stats): #number of stats we got
            weigh = random.uniform(0,100)
            self.rules += [weigh]

    def crossover(self,p2):
        offspring = Program()
        limit = random.randint(0,no_of_stats-2)
        for weigh in range(limit+1):
            offspring.rules += [self.rules[weigh]]
        for weigh in range(limit+1,no_of_stats):
            offspring.rules += [p2.rules[weigh]]
        return offspring

    def mutate(self):
        weigh = random.randint(0,no_of_stats-1)
        self.rules[weigh] = random.uniform(0,100)

    def __gt__(self, other):
        """ To tiebreak in sorting
        """
        return random.choice([True, False])

    def __lt__(self, other):
        """ To tie break in sorting
        """
        return random.choice([True, False])

def getPopulation(size):
    """ create a population of programs """
    L = []
    for i in range(size):
        d = Program()
        d.randomize()
        L += [d]
    return L

def createList(year,program):
    """ From a dictionary of each year, create a list of 64 variables classed Team
    """
    bracket = BRACKET[year]
    L = []
    d = {} #dictionary that stores the variables team
    for team in bracket:
        d[team] = Team(team,year,program)
        L += [d[team]]
    return L


def tourney(L):
    """ return a List of List for the results
    input: L of 64 variables classes teams
    """
    R = []
    for r in range(6): #to represent six rounds of competition
        A = [] # list of teams' names
        B = [] # list of variables classed Team for further looping
        for x in range(len(L)):
            if x%2 == 0:
                winner = L[x].play(L[x+1])
                A += [winner.name]
                B += [winner]
        L = B
        R += [A]
    return R

def predict(program):
    """ Take in program and return a dictionary that can be compared with RESULT
    """
    prediction = {} #dictionary that contains the list of prediction of each year
    for year in range(start_year,end_year-1): #when I the new data of the current year (2017)
        L = createList(year,program)
        prediction[year] = tourney(L)
    return prediction

def accuracy(program):
    """ Return a dictionary of how many times the program got right each year
    """
    prediction = predict(program)
    score = {} # a dictionary where each key is the year and each value is a list that has 6 numbers, each saying how many times the prediction is correct in that round
    totalScore = 0
    for year in range(start_year,end_year-1):
        score[year] = []
        for r in range(6):
            correctScore = 0
            for i in range(len(RESULT[year][r])):
                if prediction[year][r][i] in RESULT[year][r]:
                    correctScore += 1
            score[year] += [correctScore]
    for key in score:
        L = score[key] # this is a list with 6 elements
        for r in range(6):
            point = 10*(2**r)*L[r] #following the ESPN score
            totalScore += point
    return totalScore/(1920*7)

def dot(L,K):
    """ Compute the dot product of two lists """
    if len(K) != len(L):
      return 0
    return sum(i[0] * i[1] for i in zip(K, L))

def GA(popsize,numgen):
    Pick = 50 # how many programs i take into next year
    MutRate = 40
    Population = getPopulation(popsize)
    for gen in range(numgen):
        L = []
        for program in Population:
            L += [(accuracy(program),program)]
        TotalFit = 0
        for i in range(len(L)):
            TotalFit += L[i][0]
        averageFit = TotalFit/len(L)
        maxFit = max(L)[0]
        # print("Generation",gen)
        # print("Average Fitness:",averageFit)
        # print("Max Fit:",maxFit)
        SL = sorted(L)
        SL = SL[-(Pick):]  
        SL = [ x[1] for x in SL ]
        nextPop = []
        for i in range(len(SL)):
            nextPop += [SL[i]] 
        for newchild in range(popsize - Pick):
            Parent1 = random.choice(SL)
            Parent2 = random.choice(SL)
            offspring = Parent1.crossover(Parent2)
            mut = random.randint(1,100)
            if mut <= MutRate:
                offspring.mutate()
            nextPop += [offspring]
        Population = nextPop[:]
    # saveToFile("fit",SL[-1])
    return SL[-1]

def saveToFile( filename, p ):
   """ saves the data from Program p
       to a file named filename """
   L = p.rules
   f = open( filename, "w" )
   for item in L:
       f.write("%s\n" % item)  # prints Picobot program from __repr__
   f.write(str(accuracy(p)*100)+"% accuracy")
   f.close()


Popsize = 300
numGen = 20
def BestofBest(numPop,filename):
    """ run GA a lot of time and see what gets right
    """
    Pop = []
    for i in range(numPop):
        P = GA(Popsize,numGen)
        Pop += [P]
    R = GeneAlg(Pop,20)
    saveToFile(filename,R)

def GeneAlg(L,numgen):
    """ Same to GA but instead take in a list of Programs """
    Pick = 50 # how many programs i take into next year
    MutRate = 5
    Population = L
    for gen in range(numgen):
        L = []
        for program in Population:
            L += [(accuracy(program),program)]
        TotalFit = 0
        for i in range(len(L)):
            TotalFit += L[i][0]
        averageFit = TotalFit/len(L)
        maxFit = max(L)[0]
        SL = sorted(L)
        SL = SL[-(Pick):]  
        SL = [ x[1] for x in SL ]
        nextPop = []
        for i in range(len(SL)):
            nextPop += [SL[i]] 
        for newchild in range(len(Population) - Pick):
            Parent1 = random.choice(SL)
            Parent2 = random.choice(SL)
            offspring = Parent1.crossover(Parent2)
            mut = random.randint(1,100)
            if mut <= MutRate:
                offspring.mutate()
            nextPop += [offspring]
        Population = nextPop[:]
    # saveToFile("fit",SL[-1])
    return SL[-1]
    
def loadFile(filename):
    """ From a txt file to get the algorithm
    """
    p = Program()
    LofFile = []
    f = open(filename,'r')
    for line in f:
        LofFile.append(line.strip().split(','))
    L = []
    for i in range(len(LofFile)-1):
        L += [float(LofFile[i][0])]
    p.rules = L
    return p
    
# for i in range(30):
#     BestofBest(100,"best"+str(i)+".txt") #this is just a crab shoot

def predict2017(p):
    """ Predict the 2017 bracket using a program
    """
    L = createList(2017,p)
    prediction = tourney(L)
    return prediction