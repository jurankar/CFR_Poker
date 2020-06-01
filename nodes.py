###NODES
class node_betting_map:

    def __init__(self, infoSet):

        # Terminal state k rabs pr payoutu
        self.infoSet = infoSet


        self.betting_map = {}
        if isNewStage_(infoSet):
            self.new_cards = {}



class node:
    NUM_ACTIONS = 2

    def __init__(self, infoSet):

        #TODO nastimi da gre lohka regret sum pa strategy sum max do Max_Integer da ne dobis integer overflow
        # Algoritem
        self.infoSet = infoSet
        self.regretSum = [0, 0]
        self.strategy = [0, 0]   # verjetnost da zberemo PASS ali BET
        self.strategySum = [0, 0]

        # Nadaljne veje iz drevesa
        self.betting_map = {}  # pri vsaki iteraciji imaš 4 nova stanja pp, pb, bp, bb --> razen ko p0 prvic igra, takrat samo 2 stanja p in b

        # Terminal state k rabs pr payoutu
        if isNewStage_(infoSet):
            self.new_cards = {}


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



"""
TODO
    -Elimineri infoset iz noda in ga prenasi zravn skupi z rekurzijo --> po tem bodo nodi dokončno optimizirani
"""