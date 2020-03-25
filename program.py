from random import random as randDec
import random
import time



class node:
    NUM_ACTIONS = 2

    def __init__(self):
        self.infoSet = ""
        self.regretSum = [0, 0]
        self.strategy = [0, 0]   # verjetnost da zberemo PASS ali BET
        self.strategySum = [0, 0]
        self.avgStrat = []              # --> to be optimized !

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

    def toString(self):
        return ((self.infoSet),":   ",self.getAvgStrat())

# --------------------------------------------------------------------------------------------------



class Poker_Learner:
    PASS = 0
    BET = 1
    NUM_ACTIONS = 2
    nodeMap = {}    # ta dictionary povezuje infoSete z nodi


    def isTerminalState(self, infoSet):
        # pregledamo mozne bete in passe
        splitHistory = infoSet.split("|")
        stage_num = len(splitHistory) - 1
        if len((splitHistory[stage_num]).split(",")) == 1:   # pr payoffu pr flopu in turnu ne zazna
            stage_num -= 1

        current_stage = splitHistory[stage_num].split(",")
        stg_len = len(current_stage)

        if(stg_len > 1 and current_stage[1] == "P0p"):
            if(stg_len > 2 and current_stage[2] == "P1p"):
                return True
            elif(stg_len > 2 and current_stage[2] == "P1b"):
                if(stg_len > 3 and  current_stage[3] == "P0p"):
                    return True
                elif(stg_len > 3 and  current_stage[3] == "P0b"):
                    return True
                else:
                    return False
            else:
                return False
        elif(stg_len > 1 and current_stage[1] == "P0b"):
            if(stg_len > 2 and current_stage[2] == "P1p"):
                return True
            elif stg_len > 2 and current_stage[2] == "P1b":
                return True
            else:
                return False
        else:
            return False

    def betterCards(self, playerCards, opponentCards):  # --> return TRUE ce ma players bolse karte in FALSE ce ma slabse
        # tuki bomo gledal sam poker, full house, tris, dva para, par, pa High Card
        pari_pl = []
        trisi_pl = []
        poker_pl = []
        # lestvica_pl = []     --> TO DO ko bojo karte 2-A

        pari_op = []
        trisi_op = []
        poker_op = []
        # lestvica_op = []     --> TO DO ko bojo karte 2-A

        #pogledamo pokre, trise in pare
        for i in range(7, 0, -1):
            i = str(i)
            if playerCards.count(i) == 4:
                poker_pl.append(int(i))
            if opponentCards.count(i) == 4:
                poker_op.append(int(i))

            if playerCards.count(i) == 3:
                trisi_pl.append((int(i)))
            if opponentCards.count(i) == 3:
                trisi_op.append((int(i)))

            if playerCards.count(i) == 2:
                pari_pl.append(int(i))
            if opponentCards.count(i) == 2:
                pari_op.append(int(i))
        trisi_op.sort(reverse=True)
        trisi_pl.sort(reverse=True)
        pari_op.sort(reverse=True)
        pari_pl.sort(reverse=True)

        # če ma nekdo poker pol vemo iz prve da je zmagu ker je to najbolsa kombinacija
        if len(poker_pl) == 1 and len(poker_op) == 1:
            return True if poker_pl[0] > poker_op[0] else False
        elif len(poker_pl) == 1 and len(poker_op) == 0:
            return True
        elif len(poker_pl) == 0 and len(poker_op) == 1:
            return False

        # pogledamo HC
        for i in range(8):
            i = str(i)
            if playerCards.count(i) > 0:
                hc_pl = int(i)
            if opponentCards.count(i) > 0:
                hc_opp = int(i)

        #tuki zdj primerjamo hande med sabo

        #full house
        if len(trisi_pl) > 0 and len(pari_pl) > 0 and len(trisi_op) > 0 and len(pari_op) > 0:   #oba mata full house
            if trisi_pl[0] > trisi_op[0]:
                return True
            elif trisi_pl[0] < trisi_op[0]:
                return False
            else:   #trisa sta enaka
                if pari_pl[0] > pari_op[0]:
                    return True
                elif pari_pl[0] < pari_op[0]:
                    return False
                else:   #para sta enaka
                    return True if hc_pl >= hc_opp else False   # --> TO DO split ce je isti high card

        elif len(trisi_pl) > 0 and len(pari_pl) > 0 and (len(trisi_op) == 0 or len(pari_op) == 0):  #player ma full opp ne
            return True
        elif len(trisi_op) > 0 and len(pari_op) > 0 and (len(trisi_pl) == 0 or len(pari_pl) == 0):  # opp ma full player ne
            return False

        #tris
        if len(trisi_pl) > 0 and len(trisi_op) > 0: #oba tris
            if trisi_pl[0] > trisi_op[0]:
                return True
            elif trisi_pl[0] < trisi_op[0]:
                return False
            else:   #isti tris
                return True if hc_pl >= hc_opp else False  # --> TO DO split ce je isti high card
        elif len(trisi_pl) > 0 and len(trisi_op) == 0:
            return True
        elif len(trisi_pl) == 0 and len(trisi_op) > 0:
            return False

        #dva para
        if len(pari_pl) > 1 and len(pari_op) > 1:   #oba mata 2 para
            if pari_pl[0] > pari_op[0]: return  True
            elif pari_pl[0] < pari_op[0]: return False
            else:   #isti top pair
                if pari_pl[1] > pari_op[1]: return True
                elif pari_pl[1] < pari_op[1]: return False
                else:   # isti second pair
                    return True if hc_pl >= hc_opp else False  # --> TO DO split ce je isti high card
        elif len(pari_pl) > 1 and len(pari_op) <= 1:
            return True
        elif len(pari_pl) <= 1 and len(pari_op) > 1:
            return False

        #en par
        if len(pari_pl) == 1 and len(pari_op) == 1:
            if pari_pl[0] > pari_op[0]: return  True
            elif pari_pl[0] < pari_op[0]: return False
            else:
                return True if hc_pl >= hc_opp else False  # --> TO DO split ce je isti high card
        elif len(pari_pl) == 1 and len(pari_op) == 0:
            return True
        elif len(pari_pl) == 0 and len(pari_op) == 1:
            return False

        return True if hc_pl >= hc_opp else False  # --> TO DO split ce je isti high card


    # payoff for terminal states --> preveri če je konc runde in če je izplačaj zmagovalnega igralca
    def payoff(self, player_infoset, cards, player):

        if self.isTerminalState(player_infoset):
            splitHistory = player_infoset.split("|")
            gameStage = len(splitHistory)   # --> a smo preflop/flop/river/turn

            if len((splitHistory[gameStage - 1]).split(",")) == 1:  # pr payoffu pr flopu in turnu ne zazna
                gameStage -= 1

            #kakšne karte mamo  --> če smo na riverju da primerjamo karte z nasprotnikom
            cards_on_table = str(cards[4]) + str(cards[5]) + str(cards[6]) + str(cards[7]) + str(cards[8])
            if player == 0:
                player_cards = str(cards[0]) + str(cards[1]) + cards_on_table
                opponent_cards = str(cards[2]) + str(cards[3]) + cards_on_table
            else:
                player_cards = str(cards[2]) + str(cards[3]) + cards_on_table
                opponent_cards = str(cards[0]) + str(cards[1]) + cards_on_table

            # pregledamo mozne bete in passe --> continue / to do
            current_round = splitHistory[gameStage - 1].split(",")  # --> da smo v končnem stanju pogleda self.isTerminalState


            začetna_stava = 0.5 # --> untested
            if player == 0:
                reward = player_infoset.count("P1b") + začetna_stava
                penalty = -player_infoset.count("P0b") - začetna_stava
            elif player == 1:
                reward = player_infoset.count("P0b") + začetna_stava
                penalty = -player_infoset.count("P1b") - začetna_stava
            else:
                return "error"

            if(current_round[1] == "P0p"):
                if(current_round[2] == "P1p" and gameStage == 4):
                    if self.betterCards(player_cards, opponent_cards):
                        return reward
                    else:
                        return penalty
                elif(current_round[2] == "P1b"):
                    if(current_round[3] == "P0p"):
                        return penalty if player == 0 else reward
                    elif(current_round[3] == "P0b"  and gameStage == 4):
                        if self.betterCards(player_cards, opponent_cards):
                            return reward
                        else:
                            return penalty
                    else:
                        return "continue"
                else:
                    return "continue"
            elif(current_round[1] == "P0b"):
                if(current_round[2] == "P1p"):
                    return reward if player == 0 else penalty
                elif current_round[2] == "P1b" and gameStage == 4:
                    if self.betterCards(player_cards, opponent_cards):
                        return reward
                    else:
                        return penalty
                else:
                    return "continue"
            else:
                return "error"
        else:
            return "continue"

    # dobimo node aka. stanje v katerem smo
    def nodeInformation(self, infoSet):

        if infoSet in self.nodeMap:
            newNode = self.nodeMap[infoSet]
        else:
            newNode = node()   # --> ko se node kreira se ze skopirajo ostale vrednosti iz drugih nodov...ne gre iz nule
            newNode.infoSet = infoSet
            self.nodeMap[infoSet] = newNode

        return newNode

    def poVrsti(self, cards):
        cards.sort()
        cards_string = ""
        for i in range (len(cards)):
            cards_string += str(cards[i])

        return cards_string

    # player_infoset in opp_infoset se skupi cez prenasa in se oba hkrati posodabla
    def cfr(self, cards, p0, p1, infoSet):

        # priprava
        splitHistory = infoSet.split("|")
        gameStage = len(splitHistory)
        currentHis = splitHistory[gameStage-1]
        plays = currentHis.count(",")
        # imamo player1 in player2 aka player in opponent
        player = plays % 2      # --> to test
        if player == 0:
            player_infoset = self.poVrsti([cards[0], cards[1]]) + infoSet
        elif player == 1:
            player_infoset = self.poVrsti([cards[2], cards[3]]) + infoSet
        else:
            return "error"

        # dobimo payoff ce je končno stanje
        payoff = self.payoff(player_infoset, cards, player)
        if payoff != "continue":
            return payoff

        # dobimo v katerem stanju/nodu/situaciji trenutno smo
        newNode1 = self.nodeInformation(player_infoset)

        # rekurzivno kličemo self.cfr za opcijo bet in opcijo pass
        strategy = newNode1.getStrat(p0 if player == 0 else p1)
        util = [0, 0]   # kolk utila mamo za bet pa kolk za pass
        nodeUtil = 0

        for i in range(self.NUM_ACTIONS):
            # --> tuki prevermo ce je terminal state in če je pol na konc dodamo še '|', drugač pa sam dodaš in greš spet
            new_infoset = str(infoSet) + "," + "P" + str(player) + ("p" if i == 0 else "b")  # infoset + 0p, --> 0 pove da je odigral player 0

            # pogledamo če je terminal state in gremo v novo rundo
            if self.isTerminalState(new_infoset):
                if gameStage <= 3:
                    new_infoset += "|"
                if gameStage == 1:  #flop
                    new_infoset += self.poVrsti([cards[4], cards[5], cards[6]])
                elif gameStage == 2:    #turn
                    new_infoset += str(cards[7])
                elif gameStage == 3:    #river
                    new_infoset += str(cards[8])


            if (player == 0):
                util[i] = - self.cfr(cards, p0 * strategy[i], p1, new_infoset)  # --> player pa opp infoset obrnemo ko je drug na vrsti
            else:
                util[i] = - self.cfr(cards, p0, p1 * strategy[i], new_infoset)

            nodeUtil += strategy[i] * util[i]

        # zdj pa seštejemo counter factual regret
        for i in range(self.NUM_ACTIONS):
            regret = util[i] - nodeUtil
            if (player == 0):
                newNode1.regretSum[i] += p1 * regret
            else:
                newNode1.regretSum[i] += p0 * regret

        return nodeUtil


    def train(self, stIteracij):
        # prvi dve sta od playerja, drugi dve sta od opponenta, naslednjih 5 je na mizi
        cards = [1,1,1,1, 2,2,2,2, 3,3,3,3 ,4,4,4,4, 5,5,5,5, 6,6,6,6]
        util = 0

        trash_hands = []  # #--> to do

        for i in range(stIteracij):

            if i % (stIteracij/100) == 0:
                print(i / (stIteracij/100), " %")

            random.shuffle(cards)
            player_cards = self.poVrsti([cards[0], cards[1]])
            # vecina projev na zacetku ze raisa, ce nima nekega trash handa
            if player_cards not in trash_hands:
                util += self.cfr(cards, 1, 1, "")


        print("Average game return: ", util / stIteracij)


# --------------------------------------------------------------------------------------------------



def stevilkaVKarto(st):

    switcher = {
        1: "9",
        2: "10",
        3: "J",
        4: "Q",
        5: "K",
        6: "A",
    }

    return (switcher.get(st, "Error ni te karte"))

def game_payoff(learner, stanjePlayer, botInfoSet, cards):
    payoff = learner.payoff(botInfoSet, cards, 0)
    if payoff != "continue":
        if payoff < 0:
            print("Izgubili ste ", payoff, " vra.")
        elif payoff > 0:
            print("Dobili ste ", payoff, " vra.")
        elif payoff == 0:
            print("Si na nuli --> preflop fold probably")
        stanjePlayer += payoff
        return stanjePlayer, True

    return stanjePlayer, False

def igrajIgro(learner): # --> TO DO ne dela ok
    cards = [1,1,1,1, 2,2,2,2, 3,3,3,3 ,4,4,4,4, 5,5,5,5, 6,6,6,6]
    input_word = "hec"

    stanjePlayer = 30

    print("\n\n\n\n\nmozne karte so od 8 do As")
    print("če želiš zaključiti igro vpiši besedo end\n\n")
    while input_word != "end":
        random.shuffle(cards)
        plays = 0
        moji_karti_str = stevilkaVKarto(cards[0]) + "," + stevilkaVKarto(cards[1])
        bot_karti_str = stevilkaVKarto(cards[2]) + "," + stevilkaVKarto(cards[3])
        botInfoSet = learner.poVrsti([cards[2], cards[3]])

        print("\n\ntvoji karti sta: ", moji_karti_str)
        karte_na_mizi = ""
        end_round = False
        for i in range(4):  #preflop, flop, turn, river

            if i != 0:
                print("Na mizi so karte: ", karte_na_mizi, "      Tvoji karti sta: ", moji_karti_str)

            print("če želiš staviti napiši b, če pa želiš checkati pa vpiši p")
            actionPlayer = input("Vnesi: ")
            plays += 1

            #zdj določm še za bota action
            botInfoSet += ",P0" + str(actionPlayer)
            node = learner.nodeInformation(botInfoSet)
            if node.strategySum[0] == 0 and node.strategySum[1] == 0:
                print ("\nnew node --> ", botInfoSet + "\n")
            strat = node.getAvgStrat()
            if(randDec() > strat[0]):
                actionBot = "b"
                print("Bot se odločil za bet   oz. B")
            else:
                actionBot = "p"
                print("Bot se odločil za pass  oz.  P")
            plays += 1
            botInfoSet += ",P1" + actionBot
            stanjePlayer, end_round = game_payoff(learner, stanjePlayer, botInfoSet, cards)
            if end_round: break


            if actionPlayer == "p" and actionBot == "b":
                print("če želiš staviti napiši b, če pa želiš checkati pa vpiši p")
                actionPlayer = input("Vnesi: ")
                botInfoSet += ",P0" + actionPlayer

            if i == 0:
                new_cards = learner.poVrsti([cards[4], cards[5], cards[6]])
                karte_na_mizi += stevilkaVKarto(cards[4]) + "," + stevilkaVKarto(cards[5]) + "," + stevilkaVKarto(cards[6])
            elif i == 1:
                new_cards = str(cards[7])
                karte_na_mizi += "," + stevilkaVKarto(cards[7])
            elif i == 2:
                new_cards = str(cards[8])
                karte_na_mizi += "," + stevilkaVKarto(cards[8])
            botInfoSet += "|" + new_cards
            stanjePlayer, end_round = game_payoff(learner, stanjePlayer, botInfoSet, cards)
            if end_round: break

        print("Na mizi: ", karte_na_mizi, "     Player: ", moji_karti_str, "    Bot: ", bot_karti_str)
        print("Vaše novo stanje je ", stanjePlayer)


        #konec igre
        if(stanjePlayer >= 60):
            print("\n\n\nČestitke porazili ste bota")
            break
        elif(stanjePlayer <= 0):
            print("\n\n\nŽal ste izgubili")
            break


if __name__ == "__main__":
    start_time = time.time()
    learner = Poker_Learner()
    learner.train(1000000)
    print("Čas izvajanja prigrama: ", (time.time() - start_time))

    # igranje igre
    igrajIgro(learner)

"""
Zdaj razvijam osnovno obliko pokra s kartami 9-A, kjer bomo gledali samo High card, par, dva para, tris, full house,
poker.
Ta verzija bo brez dreves, da bom nato videl razliko glede časa z drevesi. Prav tako bos lahko stavil samo
1 bet na potezo. 
Čas izvajanja s slovarjem aka. brez dreves za 1000000 iteracij: 5848.5 sekund --> 97.5 minut
"""

"""
TODO:
- dodj vse karte notr od 2 do A
    --> pol dodeli funkcijo self.betterCards (dodj lestvice)
- preber navodila kako je s kickerjom 
- včasih checka full house kar mi je mal čudno, mogoče treba kej popraut funkcijo
- trash handi --> handi k jih iz prve foldaš ker so trash (uzemi bolj "tight" tehniko kjer velik foldaš in velik raisaš ker to bl zmede beginner playerje)

"""