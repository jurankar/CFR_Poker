###NODES
class node_betting_map:

    def __init__(self, infoSet):
        self.node_legit = False

        self.betting_map = {}
        self.new_cards = {}

        # Terminal state k rabs pr payoutu
        self.infoSet = infoSet
        current_stage = self.infoSet.split("|")[(self.infoSet.count("|") + 1) - 1]
        self.terminal = isTerminalState(infoSet)
        if self.terminal != False:
            self.pot_size = infoSet.count("b")
            self.player = (current_stage.count("b") + current_stage.count("p")) % 2  # -->TO BE optimized


class node:
    NUM_ACTIONS = 2

    def __init__(self, infoSet):
        self.node_legit = True

        # Algoritem
        self.infoSet = infoSet
        self.regretSum = [50, 50]
        self.strategy = [0, 0]   # verjetnost da zberemo PASS ali BET
        self.strategySum = [0, 0]
        self.avgStrat = []              # --> to be optimized !

        # Nadaljne veje iz drevesa
        self.betting_map = {}  # pri vsaki iteraciji imaš 4 nova stanja pp, pb, bp, bb --> razen ko p0 prvic igra, takrat samo 2 stanja p in b

        # Terminal state k rabs pr payoutu
        self.gameStage = self.infoSet.count("|") + 1
        current_stage = self.infoSet.split("|")[self.gameStage - 1]
        self.terminal = isTerminalState(infoSet)
        if self.terminal:
            self.pot_size = infoSet.count("b")
        self.player = (current_stage.count("b") + current_stage.count("p"))%2   # -->TO BE optimized

        # Ostalo
        #self.newStage = isNewStage(infoSet) or isNewStage(infoSet[:-2])   # --> TODO neki ne dela ok
        #if self.newStage == True:  --> OPTIMIZACIJA nared da se to kreira samo v nodih kjer je potrebno (na nodih ko pridemo v nov stage)
        self.new_cards = {}  #list nodov za vsako kombinacijo novih kart ki padejo na flopu, turnu in riverju

    #strategy[] je ubistvu sam normaliziran regretSum[] --> skor copy paste iz RM rock paper scissors
    def getStrat(self, realizationWeight):

        # if(not (self.regretSum[0] == 0 and self.regretSum[1] == 0) ):    # if da ne gre pr prvi iteraciji notr
        normalizingSum = 0

        for i in range(self.NUM_ACTIONS):
            self.strategy[i] = self.regretSum[i] if self.regretSum[i] > 0 else 0
            normalizingSum += self.strategy[i]

        for i in range(self.NUM_ACTIONS):
            if(normalizingSum > 0):
                self.strategy[i] /= normalizingSum
            else:
                self.strategy[i] = 1.0 / self.NUM_ACTIONS
            self.strategySum[i] += realizationWeight * self.strategy[i]

        #debugging
        #self.avgStrat = self.getAvgStrat()

        return self.strategy


    # vzamemo povprečno strategijo ki jo mamo v stretegySum[] od prej
    # ker vsaka posamična strategija je lahko negativna
    # ubistvu sam normaliziramo strategySum[]
    def getAvgStrat(self):
        avgStrat = [0, 0]
        normalizingSum = 0
        for i in range(self.NUM_ACTIONS):
            normalizingSum += self.strategySum[i]
        for i in range(self.NUM_ACTIONS):
            if(normalizingSum > 0):
                avgStrat[i] = self.strategySum[i] / normalizingSum
            else:
                #print("error bruh")
                avgStrat[i] = 1.0 / self.NUM_ACTIONS
        return avgStrat



# --------------------------------------------------------------------------------------------------


##GLOBAL FUNCTIONS
def isNewStage_(infoSet):  # da vemo ce je nasledna flop, turn, river
    if infoSet != "" and infoSet[-1] == '|':
        infoSet = infoSet[:-1]

    # pregledamo mozne bete in passe
    splitHistory = infoSet.split("|")
    gameStage = len(splitHistory)
    current_stage = (splitHistory[gameStage - 1])
    končna_stanja = ["pp", "pbb", "bb"]
    for i in končna_stanja:
        if current_stage == i:
            return True
    return False


# nam pove če smo zaključili rundo ali ne
def isTerminalState(infoSet):
    # pregledamo mozne bete in passe
    splitHistory = infoSet.split("|")
    gameStage = len(splitHistory)
    current_stage = (splitHistory[gameStage - 1])
    stg_len = len(current_stage)

    # ce igrata do konca da odpreta karte
    if gameStage == 4 and isNewStage_(infoSet):
        return "call_betterCards"   #--> sta igrala do konca kazeta karte
    # ce nekdo nekje folda
    else:
        if stg_len >=1 and current_stage[0] == "p":
            if stg_len >=2 and current_stage[1] == "p":
                return False
            elif stg_len >=2 and current_stage[1] == "b":
                if stg_len >=3 and current_stage[2] == "p":
                    return "p1_win"
                elif stg_len >=3 and current_stage[2] == "b":
                    return False
                else:
                    return False
            else:
                return False
        elif stg_len >=1 and current_stage[0] == "b":
            if stg_len >=2 and current_stage[1] == "p":
                return "p0_win"
            elif stg_len >=2 and current_stage[1] == "b":
                return False
            else:
                return False
        else:
            return False    #prazen infoSet