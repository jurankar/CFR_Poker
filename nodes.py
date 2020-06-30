import numpy as np


###NODES

#uporabljamo ko je node v terminal stanju (igra se zaključi ker je nekdo foldou ali pa sta pokazala karte)
#tukaj rabimo samo infoset ker ga rabmo samo za payoffe
class node_payoff:
    #__slots__ = ["infoSet"]
    def __init__(self, infoSet):
        self.infoSet = infoSet

#uporabljamo ko pridemo v nov stage
class node_new_cards:
    #__slots__ = ["infoSet", "new_cards"]
    def __init__(self, infoSet):
        self.infoSet = infoSet
        self.new_cards = {}

#uporabljamo ko player ni na vrsti ampak samo belezimo akcijo prejsnjega igralca
class node_betting_map:
    #__slots__ = ["infoSet", "betting_map"]
    def __init__(self, infoSet):
        # Terminal state k rabs pr payoutu
        self.infoSet = infoSet
        self.betting_map = {}

#TODO nastimi da gre lohka regret sum pa strategy sum max do Max_Integer da ne dobis integer overflow
# Implement __slots__
#uporabljamo ko smo na potezi in racunamo verjetnosi in se odločamo kakšno potezo bomo naredili
class node:
    NUM_ACTIONS = 3
    #__slots__ = ["infoSet", "regretSum", "strategySum", "avg_strategy", "strategy", "betting_map"]
    def __init__(self, infoSet):
        self.infoSet = infoSet
        num_of_actions = num_actions(infoSet, self.NUM_ACTIONS)
        self.regretSum = np.zeros(num_of_actions)
        self.strategySum = np.zeros(num_of_actions) # verjetnost da zberemo PASS ali BET
        self.avg_strategy = np.zeros(num_of_actions)  # --> to be deleted
        self.strategy = np.zeros(num_of_actions)    # --> to be deleted

        # Nadaljne veje iz drevesa
        self.betting_map = {}  # pri vsaki iteraciji imaš 4 nova stanja pp, pb, bp, bb --> razen ko p0 prvic igra, takrat samo 2 stanja p in b


    #strategy[] je ubistvu sam normaliziran regretSum[] --> skor copy paste iz RM rock paper scissors
    def getStrat(self, realizationWeight):

        # if(not (self.regretSum[0] == 0 and self.regretSum[1] == 0) ):    # if da ne gre pr prvi iteraciji notr
        normalizingSum = 0
        num_actions = len(self.regretSum)
        strategy = np.zeros(num_actions)

        for i in range(num_actions):
            strategy[i] = self.regretSum[i] if self.regretSum[i] > 0 else 0
            normalizingSum += strategy[i]

        for i in range(num_actions):
            if(normalizingSum > 0):
                strategy[i] /= normalizingSum
            else:
                strategy[i] = 1.0 / num_actions
            self.strategySum[i] += realizationWeight * strategy[i]

        #debugging
        self.strategy = strategy
        self.avg_strategy = self.getAvgStrat()
        return strategy


    # vzamemo povprečno strategijo ki jo mamo v stretegySum[] od prej
    # ker vsaka posamična strategija je lahko negativna
    # ubistvu sam normaliziramo strategySum[]
    def getAvgStrat(self):
        num_actions = len(self.regretSum)
        avgStrat = np.zeros(num_actions)
        normalizingSum = 0
        for i in range(num_actions):
            normalizingSum += self.strategySum[i]
        for i in range(num_actions):
            if(normalizingSum > 0):
                avgStrat[i] = self.strategySum[i] / normalizingSum
            else:
                avgStrat[i] = 1.0 / num_actions
        self.avg_strategy = avgStrat
        return avgStrat



# --------------------------------------------------------------------------------------------------


##GLOBAL FUNCTIONS
# TODO tuki naprej deli
def isNewStage(infoSet):  # da vemo ce je nasledna flop, turn, river
    if infoSet != "" and infoSet[-1] == '|':
        infoSet = infoSet[:-1]

    # pregledamo mozne bete in passe
    splitHistory = infoSet.split("|")
    gameStage = len(splitHistory)
    current_stage = (splitHistory[gameStage - 1]).split("b")
    del current_stage[0]

    if len(current_stage) > 1 and (int(current_stage[0]) == 0):# p0 checka    # TODO ko nastimas da ne stavi skos iste vrednosti poprau to vrstico !!!
        if len(current_stage) == 2 and int(current_stage[1]) == 0:  # oba checkata
            return True
        elif len(current_stage) == 3:  # check bet fold/call
            if int(current_stage[2]) == 0:  # check bet fold
                return False
            else:   # check bet call
                return True
        else:   #  check bet
            return False

    elif len(current_stage) > 1 and int(current_stage[0]) > 0:   #p0 betta
        if len(current_stage) == 2: # bett call/fold
            if int(current_stage[1]) == 1:
                return True   # bet call
            else:
                return False    # bet fold --> ni new round ker je nekdo lih zgubu
    elif len(current_stage) == 0 or len(current_stage) == 1:
        return False
    else:
        return "error"  # ne bi smel sm pridt


# nam pove ali smo na potezi ko stavimo (smo prvi na potezi ali pa je player pred nami checkal) ali smo v stanju ko callamo/foldamo
def is_betting_round(infoSet):
    split_history = infoSet.split("|")
    last_round = split_history[len(split_history)-1]
    split_round = last_round.split("b")
    del split_round[0]
    len_round = len(split_round)
    # betting round je, ko je player prvi na vrsti ali pa je player pred njim checkou
    if len_round == 0 or (len_round == 1 and split_round[0] == "0"):
        return True
    else:
        return False

# ko smo v betting stagu imamo NUM_ACTIONS moznih potez, ko pa nismo v betting stagu pa imamo samo fold/call
def num_actions(infoSet, NUM_ACTIONS):
    if is_betting_round(infoSet):
        return NUM_ACTIONS
    else:
        return 2



"""
TODO
    -Elimineri infoset iz noda in ga prenasi zravn skupi z rekurzijo --> po tem bodo nodi dokončno optimizirani
"""