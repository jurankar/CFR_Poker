###NODES
class node_betting_map:
    def __init__(self, infoSet):
        self.infoSet = infoSet  # --> debuging purposes
        self.new_cards = {}     # --> debugging k neki ne dela ok
        self.betting_map = {}
        self.betting_map_node = True    # --> more or less debugining purposes i think

        # Terminal state k rabs pr payoutu
        current_stage = self.infoSet.split("|")[(self.infoSet.count("|") + 1) - 1]
        self.terminal = isTerminalState(infoSet)
        if self.terminal != False:
            self.pot_size = current_stage.count("b")
            self.player = (current_stage.count("b") + current_stage.count("p")) % 2  # -->TO BE optimized


class node:
    NUM_ACTIONS = 2

    def __init__(self, infoSet):

        # Algoritem
        self.infoSet = infoSet
        self.regretSum = [0, 0]
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
            self.pot_size = current_stage.count("b")
        self.player = (current_stage.count("b") + current_stage.count("p"))%2   # -->TO BE optimized

        # Ostalo
        self.betting_map_node = False
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
    def getAvgStrat(self):  # --> cisti copy paste iz RM rock paper scissors
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
    # pregledamo mozne bete in passe
    splitHistory = infoSet.split("|")
    gameStage = len(splitHistory)
    current_stage = (splitHistory[gameStage - 1])
    stg_len = len(current_stage)

    if(stg_len >= 1 and current_stage[0] == "p"):
        if(stg_len >= 2 and current_stage[1] == "p"):
            return True
        elif(stg_len >= 2 and current_stage[1] == "b"):
            # v 3jem stagu sta bet in pass new stage
            if(stg_len >= 3):
                return True
            else:
                return False
        else:
            return False
    elif(stg_len >= 1 and current_stage[0] == "b"):
        #v 2gem stagu sta bet in pass new stage
        if(stg_len >= 2 and current_stage[1] == "b"):
            return True
        else:
            return False
    else:
        return False    #prazen infoSet


def isTerminalState(infoSet):
    # pregledamo mozne bete in passe
    splitHistory = infoSet.split("|")
    gameStage = len(splitHistory)
    if gameStage == 4:  #DEBUG --> pobirs pol
        debug = True
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