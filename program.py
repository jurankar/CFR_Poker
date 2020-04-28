from random import random as randDec
import random
import time

##GLOBAL VARIABLES


##GLOBAL FUNCTIONS
def isNewStage(infoSet):  # da vemo ce je nasledna flop, turn, river
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
    if gameStage == 4 and isNewStage(infoSet):
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




###NODES
class node_init_p1:
    def __init__(self):

        self.betting_map = {}

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

        # Ostalo
        self.terminal = isTerminalState(infoSet)
        self.gameStage = self.infoSet.count("|") + 1
        current_stage = self.infoSet.split("|")[self.gameStage - 1]
        self.player = (current_stage.count("b") + current_stage.count("p"))%2   # --> optimized
        self.pot_size = current_stage.count("b")
        self.newStage = isNewStage(infoSet) or isNewStage(infoSet[:-2])   # --> -2 je za p1 po tem ko je p0 že šel v novo rundo
        if self.newStage == True:
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

    def toString(self):
        return ((self.infoSet),":   ",self.getAvgStrat())

# --------------------------------------------------------------------------------------------------
###POKER_LEARNER_CFR


class Poker_Learner:
    PASS = 0
    BET = 1
    NUM_ACTIONS = 2
    nodeMap_p0 = {}    # ta dictionary povezuje infoSete z nodi
    nodeMap_p1 = {}

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
    def payoff(self, curr_node, cards):

        pot_size = curr_node.pot_size
        player = curr_node.player
        terminal_node = curr_node.terminal

        if terminal_node != False:
            # če kdo prej folda kot obicajno, pol nasprotnik dobi 1/2 pota + zadnjo stavo, ki je player ni callou
            # torej dobi pot/2 + 1
            ante = 0.5  # vsota ki jo vsak player da na mizo se preden dobi karte --> kasneje lahko zamenjas za small pa big blind
            winnings = pot_size/2 + ante
            if terminal_node == "p0_win":
                return winnings+1 if player == 0 else -(winnings + 1)
            elif terminal_node == "p1_win":
                return winnings+1 if player == 1 else -(winnings + 1)

            #kakšne karte mamo  --> če smo na riverju da primerjamo karte z nasprotnikom
            cards_on_table = str(cards[4]) + str(cards[5]) + str(cards[6]) + str(cards[7]) + str(cards[8])
            if player == 0:
                player_cards = str(cards[0]) + str(cards[1]) + cards_on_table
                opponent_cards = str(cards[2]) + str(cards[3]) + cards_on_table
            else:
                player_cards = str(cards[2]) + str(cards[3]) + cards_on_table
                opponent_cards = str(cards[0]) + str(cards[1]) + cards_on_table

            if terminal_node == "call_betterCards":
                # Vsak dobi sam pol pota ker tut v resnici staviš pol ti pol opponent in dejansko si na +/- sam za polovico pota
                # Gre ravno cez pol ker sta
                if self.betterCards(player_cards, opponent_cards):
                    return winnings # winnings = pot/2 + ante
                else:
                    return -winnings

            return "error1"

        else:
            return "continue"



    # dobimo node aka. stanje v katerem smo
    def nodeInformation(self, infoSet, player):
        # v nodemapu je drevo za vsak mozni zacetni hand
        if player == 0:
            if infoSet in self.nodeMap_p0:
                newNode = self.nodeMap_p0[infoSet]
            else:
                newNode = node("")   # --> ko se node kreira se ze skopirajo ostale vrednosti iz drugih nodov...ne gre iz nule
                self.nodeMap_p0[infoSet] = newNode
        elif player == 1:
            if infoSet in self.nodeMap_p1:
                newNode = self.nodeMap_p1[infoSet]
            else:
                newNode = node_init_p1()   # --> tuki ne rabmbo noda ker p1 na prvi potezi ne igra --> sprejmemo samo akcijo ob p0 in nato sele igra
                self.nodeMap_p1[infoSet] = newNode
        else:
            return "error"

        return newNode

    def poVrsti(self, cards):
        cards.sort()
        cards_string = ""
        for i in range (len(cards)):
            cards_string += str(cards[i])

        return cards_string

    # player_infoset in opp_infoset se skupi cez prenasa in se oba hkrati posodabla
    def cfr(self, cards, p0, p1, node_player0, node_player1, p0_turn):
        """
            node_player0 --> list nodov za vse mozne akcije playerja 0
            node_player1 --> list nodov za vse mozne akcije playerja 1
                --> v določeni iteraciji uporabljamo samo enega izmed njih, odvisno od tega ali je na vrsti p0 ali p1
            p0_turn nam pove ali je p0 na vrsti
        """

        player = 0 if p0_turn else 1
        if player == 0:
            p0_nextTurn = False
        else:
            p0_nextTurn = True
        curr_node = node_player0 if player == 0 else node_player1
        non_curr_node = node_player0 if player == 1 else node_player1

        # dobimo payoff ce je končno stanje
        payoff = self.payoff(curr_node, cards)
        if payoff != "continue":
            return payoff


        # rekurzivno kličemo self.cfr za opcijo bet in opcijo pass
        strategy = curr_node.getStrat(p0) if player == 0 else curr_node.getStrat(p1)
        util = [0, 0]   # kolk utila mamo za bet pa kolk za pass
        nodeUtil = 0

        # posodobimo in po potrebi ustvarimo nove sinove če še niso ustvarjeni
        # --> !! TO DO optimiziraj da ta informacija ze v nodih ne da vedno sprot računas --> trenutno je curr_node.newStage neki sfukan in ne kaze vedno prou
        new_stage_bool = isNewStage(curr_node.infoSet) #or isNewStage(curr_node.infoSet[:-2])   # --> ce je player1, potem zadnja dva znaka zbrisemo, ker jih je eno iteracijo prej dodal p0
        if new_stage_bool:
            curr_node.infoSet += "|"
            curr_game_stage = curr_node.gameStage

            #zdj preeidemo v nov node, ki je vezan na to kakšne karte padejo
            if curr_game_stage == 1:
                new_cards_ = "f" + self.poVrsti([cards[4],cards[5],cards[6]])   #flop
            elif curr_game_stage == 2:
                new_cards_ = "t" + str(cards[7])    #turn
            elif curr_game_stage == 3:
                new_cards_ = "r" +str(cards[8])     #river

            # TODO trenutno gleda sam za en node....more pa karte upostevat v obeh nodih --> NADALJUJ
            # TODO tut infosete posodob v obeh
            if new_cards_ not in curr_node.new_cards:
                curr_node.new_cards[new_cards_] = node(curr_node.infoSet)
            curr_node = curr_node.new_cards[new_cards_]
            #p0 začne na začetku vsake runde
            p0_nextTurn = True

        # TO DO nared neki da vid ce je zadna runda aka. nekdo pobere denar. ker sedaj naredi en nivo v drevesu preveč
        # Kreacija sinov v drevesu --> posebi node ce je player sedaj passou al pa ce je bettou
        if new_stage_bool:
            # na zacetku vsazga staga more zacet player0
            if "p" not in node_player0.betting_map:
                new_infoset = curr_node.infoSet + "p"
                node_player0.betting_map["p"] = node(new_infoset)
            if "b" not in node_player0.betting_map:
                new_infoset = curr_node.infoSet + "b"
                node_player0.betting_map["b"] = node(new_infoset)
            player = 1
        else:
            if "p" not in non_curr_node.betting_map:
                new_infoset = curr_node.infoSet + "p"
                non_curr_node.betting_map["p"] = node(new_infoset)
            if "b" not in non_curr_node.betting_map:
                new_infoset = curr_node.infoSet + "b"
                non_curr_node.betting_map["b"] = node(new_infoset)


        for i in range(self.NUM_ACTIONS):
            if (player == 0):
                # if payoff(curr_node.drevo_bet != "continue") return payoff
                util[i] = - self.cfr(cards, p0 * strategy[i], p1, node_player0, node_player1.betting_map["p"], p0_nextTurn)  if i == 0 else - self.cfr(cards, p0 * strategy[i], p1, node_player0, node_player1.betting_map["b"], p0_nextTurn)
            else:
                util[i] = - self.cfr(cards, p0, p1 * strategy[i], node_player0.betting_map["p"], node_player1, p0_nextTurn) if i == 0 else - self.cfr(cards, p0 * strategy[i], p1, node_player0.betting_map["b"], node_player1, p0_nextTurn)

            nodeUtil += strategy[i] * util[i]

        # zdj pa seštejemo counter factual regret
        for i in range(self.NUM_ACTIONS):
            regret = util[i] - nodeUtil
            if (player == 0):
                curr_node.regretSum[i] += p1 * regret
            else:
                curr_node.regretSum[i] += p0 * regret

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
            player0_info = self.poVrsti([cards[0], cards[1]])
            player1_info = self.poVrsti([cards[2], cards[3]])
            # vecina projev na zacetku ze raisa, ce nima nekega trash handa
            if player0_info not in trash_hands:
                node_player0 = self.nodeInformation(str(player0_info), 0)
                #  v temu nodu ni vazn kaj je, ker itak bomo sli ali v bet ali pass node v temu nodeu
                # lahko damo dejansko samo slovar
                node_player1 = self.nodeInformation(str(player1_info), 1)
                util += self.cfr(cards, 1, 1, node_player0, node_player1, True)


        print("Average game return: ", util / stIteracij)


# --------------------------------------------------------------------------------------------------
# PLAYING POKER GAME


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




## MAIN
if __name__ == "__main__":
    global total_isNewStage_fun_time
    total_isNewStage_fun_time = 0
    start_time = time.time()
    learner = Poker_Learner()
    learner.train(100)
    print("Čas izvajanja prigrama: ", (time.time() - start_time), " sekund. To je ", (time.time() - start_time)/60," minut.")

    # igranje igre
    #igrajIgro(learner)

"""
Zdaj razvijam osnovno obliko pokra s kartami 9-A, kjer bomo gledali samo High card, par, dva para, tris, full house,
poker.
Ta verzija bo brez dreves, da bom nato videl razliko glede časa z drevesi. Prav tako bos lahko stavil samo
1 bet na potezo. 
Čas izvajanja s slovarjem aka. brez dreves za 1000000 iteracij: 5848.5 sekund --> 97.5 minut
"""

"""
TODO:
- Če smo v newStagu pol ne rabmo cekerat "pyouta" pa dobivat strategije (prvih cca. 20 vrstic v cfrju)
- funkcijo betterCards zračuni na začetku ker jo zdj brez veze 20x racunas
- Na začetku vsazga staga more začet p0     TO DO --> TUKI NADALJUJ
-Dopiš komentarje za profesorja













Other:
- optimizacija: 
    -ce je drevo v zadnjem nodu, ne rabis it se v en node samo za payoff --> optimiziraj da ne bo treba it do zadnjega nivoja(ki je tudi največji)
    -probi se znebit infoseta --> zavzema velik časa in rama
- dodj zacetne stave oz ante
- dodj vse karte notr od 2 do A
    --> pol dodeli funkcijo self.betterCards (dodj lestvice)
- preber navodila kako je s kickerjom 
    - dodj split pr payoffu

    
- trash handi --> handi k jih iz prve foldaš ker so trash (uzemi bolj "tight" tehniko kjer velik foldaš in velik raisaš ker to bl zmede beginner playerje)
- dopoln igro da enkrat začne player enkat bot


"""