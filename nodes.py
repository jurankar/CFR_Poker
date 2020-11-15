import numpy as np
import sys

#CONSTANTS
COMPUTED_NODE_REGRET_REQUIREMENT = 7000      # to je meja regreta (max value v arrayu node.regretSum), ki sem jo določil da je node izracunan --> kasneje, ko ga boš zares učil to povečaj


###NODES

#uporabljamo ko je node v terminal stanju (igra se zaključi ker je nekdo foldou ali pa sta pokazala karte)
#tukaj rabimo samo infoset ker ga rabmo samo za payoffe
class node_payoff:
    __slots__ = ["infoSet"]
    def __init__(self, infoSet):
        self.infoSet = infoSet

#uporabljamo ko pridemo v nov stage
class node_new_cards:
    __slots__ = ["infoSet", "new_cards"]
    def __init__(self, infoSet):
        self.infoSet = infoSet
        self.new_cards = {}

#uporabljamo ko player ni na vrsti ampak samo belezimo akcijo prejsnjega igralca
class node_betting_map:
    __slots__ = ["infoSet", "betting_map"]
    def __init__(self, infoSet):
        # Terminal state k rabs pr payoutu
        self.infoSet = infoSet
        self.betting_map = {}


#uporabljamo ko smo na potezi in racunamo verjetnosi in se odločamo kakšno potezo bomo naredili
class node:
    NUM_ACTIONS = 6
    __slots__ = ["infoSet", "regretSum", "strategySum", "betting_map", "computed_node"]
    def __init__(self, infoSet):
        self.infoSet = infoSet
        num_of_actions = num_actions(infoSet, self.NUM_ACTIONS)
        self.regretSum = np.full(num_of_actions, 10.0) if num_of_actions != 2 else np.full(num_of_actions, 20.0)
        self.strategySum = np.zeros(num_of_actions) # verjetnost da zberemo PASS ali BET
        #self.avg_strategy = np.zeros(num_of_actions)  # --> to be deleted
        #self.strategy = np.zeros(num_of_actions)    # --> to be deleted

        # Ce je node ze "izracunan" aka. smo ga tolikokrat simulirali, da vemo kaj je najbolsa opcija in drugih opcij ne gledamo več
        self.computed_node = False      # --> samo betting node computamo

        # Nadaljne veje iz drevesa
        self.betting_map = {}  # pri vsaki iteraciji imaš 4 nova stanja pp, pb, bp, bb --> razen ko p0 prvic igra, takrat samo 2 stanja p in b



    def is_computed(self):
        max_regret = np.max(self.regretSum)
        min_regret = np.min(self.regretSum)

        if max_regret > COMPUTED_NODE_REGRET_REQUIREMENT or min_regret < -COMPUTED_NODE_REGRET_REQUIREMENT:
            self.computed_node = True
            max_index = np.argmax(self.regretSum)
            for i in range(len(self.strategySum)):
                #vse opcije ki niso naša najbolša pobrišemo node in nastavimo verjetnosi na 0
                if i != max_index:
                    self.strategySum[i] = 0.0
                    bet_type = "b" + str(i)
                    del self.betting_map[bet_type]  # --> brisemo iz curr_noda
                    #del non_curr_node.betting_map[bet_type]     # --> brisemo iz non_curr_noda

            #zdj nastavimo "izracunano" najbolso opcijo na 1
            self.strategySum[max_index] = 1.0



    #strategy[] je ubistvu sam normaliziran regretSum[] --> skor copy paste iz RM rock paper scissors
    def getStrat(self, realizationWeight):

        # Če smo node že "izračunali", potem ne računamo več verjetnosti --> vrnemo samo array kjer ima ena izmed opcij 100% oz. 1.0 (to je shranjeno v strategy sum)
        if self.computed_node:
            return self.strategySum
        else:
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

        # preverimo če mode sedaj "izračunan" aka "computed"
        if len(self.regretSum) != 2:  # --> samo betting node computamo
            self.is_computed()

        #debugging
        #self.strategy = strategy
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
        #self.avg_strategy = avgStrat
        return avgStrat



# --------------------------------------------------------------------------------------------------


##GLOBAL FUNCTIONS
def isNewStage(infoSet):  # da vemo ce je nasledna flop, turn, river
    if infoSet != "" and infoSet[-1] == '|':
        infoSet = infoSet[:-1]

    # pregledamo mozne bete in passe
    splitHistory = infoSet.split("|")
    gameStage = len(splitHistory)
    current_stage = (splitHistory[gameStage - 1]).split("b")
    del current_stage[0]

    if len(current_stage) > 1 and (int(current_stage[0]) == 0):# p0 checka
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
        return NUM_ACTIONS if infoSet != "" else NUM_ACTIONS + 1    # --> če imamo prvi krog, pol imamo eno opcijo več pri bettanju, ker imamo hkrati fold, call in raise
    else:
        return 2



"""
TODO
    -Elimineri infoset iz noda in ga prenasi zravn skupi z rekurzijo --> po tem bodo nodi dokončno optimizirani
"""