import random
import nodes
import pickle


##POKER_LEARNER_CFR

class Poker_Learner:
    PASS = 0
    BET = 1
    NUM_ACTIONS = 2
    nodeMap_p0 = []   # v tem arrayu je zapisan keri handi so ze v fajlih in keri še ne
    nodeMap_p1 = []

    def betterCards(self, cards,player):  # --> return TRUE ce ma players bolse karte in FALSE ce ma slabse
        #najprej določmo karte
        cards_on_table = str(cards[4]) + str(cards[5]) + str(cards[6]) + str(cards[7]) + str(cards[8])
        if player == 0:
            playerCards = str(cards[0]) + str(cards[1]) + cards_on_table
            opponentCards = str(cards[2]) + str(cards[3]) + cards_on_table
        else:
            playerCards = str(cards[2]) + str(cards[3]) + cards_on_table
            opponentCards = str(cards[0]) + str(cards[1]) + cards_on_table


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
    def payoff(self, curr_node):

        terminal_node = curr_node.terminal
        if terminal_node != False:
            pot_size = curr_node.pot_size
            player = curr_node.player
            # če kdo prej folda kot obicajno, pol nasprotnik dobi 1/2 pota + zadnjo stavo, ki je player ni callou
            # torej dobi pot/2 + 1
            ante = 0.5  # vsota ki jo vsak player da na mizo se preden dobi karte --> kasneje lahko zamenjas za small pa big blind
            winnings = pot_size/2 + ante
            if terminal_node == "p0_win":
                return winnings+1 if player == 0 else -(winnings + 1)
            elif terminal_node == "p1_win":
                return winnings+1 if player == 1 else -(winnings + 1)

            if terminal_node == "call_betterCards":
                # Vsak dobi sam pol pota ker tut v resnici staviš pol ti pol opponent in dejansko si na +/- sam za polovico pota
                # Gre ravno cez pol ker sta
                if player == 0:
                    global better_cards_p0
                    return winnings if better_cards_p0 else -winnings # winnings = pot/2 + ante
                elif player == 1:
                    global better_cards_p1
                    return winnings if better_cards_p1 else -winnings # winnings = pot/2 + ante
                else:
                    return "error"

            return "error1"

        else:
            return "continue"


    # player_infoset in opp_infoset se skupi cez prenasa in se oba hkrati posodabla
    def cfr(self, cards, p0, p1, node_player0, node_player1, p0_turn):

        player = 0 if p0_turn else 1
        if player == 0:
            p0_nextTurn = False
        else:
            p0_nextTurn = True
        curr_node = node_player0 if player == 0 else node_player1

        # dobimo payoff ce je končno stanje
        payoff = self.payoff(curr_node)
        if payoff != "continue":
            return payoff

        # rekurzivno kličemo self.cfr za opcijo bet in opcijo pass
        strategy = curr_node.getStrat(p0) if player == 0 else curr_node.getStrat(p1)
        util = [0, 0]   # kolk utila mamo za bet pa kolk za pass
        nodeUtil = 0

        # posodobimo in po potrebi ustvarimo nove sinove če še niso ustvarjeni
        # --> !! TO DO optimiziraj da ta informacija ze v nodih ne da vedno sprot računas --> trenutno je curr_node.newStage neki sfukan in ne kaze vedno prou
        new_stage_bool = isNewStage(curr_node.infoSet)
        if new_stage_bool:
            #prilagodimo node, ker je protokol ob novem stagu malo drugačen ker mora začeti p0 (tudi če je ravno igral)
            if curr_node.infoSet[-1] != '|':
                curr_node.infoSet += "|"

            #zdj preeidemo v nov node, ki je vezan na to kakšne karte padejo
            if hasattr(curr_node, 'gameStage'):
                curr_game_stage = curr_node.gameStage
            else:
                return "error 5"

            if curr_game_stage == 1:
                new_cards_ = "f" + self.poVrsti([cards[4],cards[5],cards[6]])   #flop
            elif curr_game_stage == 2:
                new_cards_ = "t" + str(cards[7])    #turn
            elif curr_game_stage == 3:
                new_cards_ = "r" +str(cards[8])     #river
            else:
                return "error3"

            # create nodes if necessary
            if new_cards_ not in node_player0.new_cards:
                node_player0.new_cards[new_cards_] = nodes.node(node_player0.infoSet)
            if new_cards_ not in node_player1.new_cards:
                node_player1.new_cards[new_cards_] = nodes.node_betting_map(node_player1.infoSet)

            #update nodes
            node_player0 = node_player0.new_cards[new_cards_]
            node_player1 = node_player1.new_cards[new_cards_]
            curr_node = node_player0 if player == 0 else node_player1
            # non_curr_node = node_player0 if player == 1 else node_player1

            #p0 začne na začetku vsake runde(flop, trun, river) --> tuki je false ker js v vsaki rundi gledam za eno rundo nazaj
            p0_nextTurn = False

        # TO DO nared neki da vid ce je zadna runda aka. nekdo pobere denar. ker sedaj naredi en nivo v drevesu preveč
        # Kreacija sinov v drevesu --> posebi node ce je player sedaj passou al pa ce je bettou
        new_infoset = curr_node.infoSet + "p"
        if p0_nextTurn == False:
            p0_nextTurn = isNewStage(new_infoset)
        if "p" not in node_player0.betting_map:
            node_player0.betting_map["p"] = nodes.node(new_infoset) if p0_nextTurn else nodes.node_betting_map(new_infoset)
        if "p" not in node_player1.betting_map:
            node_player1.betting_map["p"] = nodes.node(new_infoset) if not p0_nextTurn else nodes.node_betting_map(new_infoset)

        new_infoset = curr_node.infoSet + "b"
        if p0_nextTurn == False:
            p0_nextTurn = isNewStage(new_infoset)
        if "b" not in node_player0.betting_map:
            node_player0.betting_map["b"] = nodes.node(new_infoset) if p0_nextTurn else nodes.node_betting_map(new_infoset)
        if "b" not in node_player1.betting_map:
            node_player1.betting_map["b"] = nodes.node(new_infoset) if not p0_nextTurn else nodes.node_betting_map(new_infoset)

        # TODO neki se ne posodabla pravilno pr strategySum pa to....lahko da je to k sm sam sešteu
        # TODO node.player se zameša če daš kje umes bet oz. "b"
        player = 1 if p0_nextTurn else 0
        for i in range(self.NUM_ACTIONS):
            if (p0_nextTurn):
                # if payoff(curr_node.drevo_bet != "continue") return payoff
                util[i] = - self.cfr(cards, p0 * strategy[i], p1, node_player0.betting_map["p"], node_player1.betting_map["p"], p0_nextTurn) if i == 0 else - self.cfr(cards, p0 * strategy[i], p1, node_player0.betting_map["b"], node_player1.betting_map["b"], p0_nextTurn)
            else:
                util[i] = - self.cfr(cards, p0, p1 * strategy[i], node_player0.betting_map["p"], node_player1.betting_map["p"], p0_nextTurn) if i == 0 else - self.cfr(cards, p0 * strategy[i], p1, node_player0.betting_map["b"], node_player1.betting_map["b"], p0_nextTurn)

            nodeUtil += strategy[i] * util[i]


        # zdj pa seštejemo counter factual regret
        for i in range(self.NUM_ACTIONS):
            regret = util[i] - nodeUtil
            if (player == 0):
                curr_node.regretSum[i] += p1 * regret
            else:
                curr_node.regretSum[i] += p0 * regret

        return nodeUtil


    # dobimo node aka. stanje v katerem smo
    def nodeInformation(self, infoSet, player):
        # v nodemapu je drevo za vsak mozni zacetni hand
        if player == 0:
            file_name = "p0_" + infoSet + ".pkl"
            if (file_name) in self.nodeMap_p0:
                with open(file_name, 'rb') as input:
                    newNode = pickle.load(input)
            else:
                newNode = nodes.node("")   # --> ko se node kreira se ze skopirajo ostale vrednosti iz drugih nodov...ne gre iz nule
                self.nodeMap_p0.append(file_name)
        elif player == 1:
            file_name = "p1_" + infoSet + ".pkl"
            if (file_name) in self.nodeMap_p1:
                with open(file_name, 'rb') as input:
                    newNode = pickle.load(input)
            else:
                newNode = nodes.node_betting_map("")   # --> tuki ne rabmbo noda ker p1 na prvi potezi ne igra --> sprejmemo samo akcijo ob p0 in nato sele igra
                self.nodeMap_p1.append(file_name)
        else:
            return "error2"

        return newNode

    def poVrsti(self, cards):
        cards.sort()
        cards_string = ""
        for i in range (len(cards)):
            cards_string += str(cards[i])

        return cards_string


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
            global better_cards_p0
            better_cards_p0 = self.betterCards(cards, 0)
            global better_cards_p1
            better_cards_p1 = self.betterCards(cards, 1)

            # vecina projev na zacetku ze raisa, ce nima nekega trash handa
            if player0_info not in trash_hands:
                #  v temu nodu ni vazn kaj je, ker itak bomo sli ali v bet ali pass node v temu nodeu
                # lahko damo dejansko samo slovar
                node_player0 = self.nodeInformation(str(player0_info), 0)
                node_player1 = self.nodeInformation(str(player1_info), 1)
                util += self.cfr(cards, 1, 1, node_player0, node_player1, True)

                #zdj zapišemo v fajle posodoblene node
                with open("p0_" + player0_info + ".pkl", 'wb') as output:
                    pickle.dump(node_player0, output, pickle.HIGHEST_PROTOCOL)
                with open("p1_" + player1_info + ".pkl", 'wb') as output:
                    pickle.dump(node_player1, output, pickle.HIGHEST_PROTOCOL)


        print("Average game return: ", util / stIteracij)
# --------------------------------------------------------------------------------------------------


##GLOBAL FUNCTIONS
def isNewStage(infoSet):  # da vemo ce je nasledna flop, turn, river
    #updajtana verzija, v nodih je stara ce kj ne bo ok
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