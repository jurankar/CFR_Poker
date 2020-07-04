import random
import nodes
import numpy as np

#Save files to disk
import os
from os import listdir
from os.path import isfile, join
import pickle


##POKER_LEARNER_CFR

class Poker_Learner:
    NUM_ACTIONS = 3

    """
    nodeMap_p0 = []   # v tem arrayu je zapisan keri handi so ze v fajlih in keri še ne
    nodeMap_p1 = []
    """

    nodeMap_p0 = {}   # v tem arrayu je dictionary vseh nodov
    nodeMap_p1 = {}

    #pove če ima player high card
    def isHighCard(self, playerCards, opponentCards):
        playerCards.sort(reverse=True)
        opponentCards.sort(reverse=True)
        for i in range(5):
            if playerCards[i] > opponentCards[i]:
                return True
            elif playerCards[i] < opponentCards[i]:
                return False
        return "split"


    def betterCards(self, cards,player):  # --> return TRUE ce ma players bolse karte in FALSE ce ma slabse
        #najprej določmo karte
        cards_on_table = [cards[4], cards[5], cards[6], cards[7], cards[8]]
        if player == 0:
            playerCards = [cards[0], cards[1]] + cards_on_table
            opponentCards = [cards[2], cards[3]] + cards_on_table
        else:
            playerCards = [cards[2], cards[3]] + cards_on_table
            opponentCards = [cards[0], cards[1]] + cards_on_table


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
        for i in range(14, 0, -1):

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

        #če imamo več kot en tris, potem ostale trise dodamo k parom (ker več kot 1 tris ne upostevamo v igri)
        trisi_pl, pari_pl = tris_to_pair(trisi_pl, pari_pl)
        trisi_op, pari_op = tris_to_pair(trisi_op, pari_op)
        pari_op.sort(reverse=True)
        pari_pl.sort(reverse=True)



        # če ma nekdo poker pol vemo iz prve da je zmagu ker je to najbolsa kombinacija
        if len(poker_pl) == 1 and len(poker_op) == 1:
            return True if poker_pl[0] > poker_op[0] else False
        elif len(poker_pl) == 1 and len(poker_op) == 0:
            return True
        elif len(poker_pl) == 0 and len(poker_op) == 1:
            return False

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
                    return self.isHighCard(playerCards, opponentCards)

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
                return self.isHighCard(playerCards, opponentCards)
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
                    return self.isHighCard(playerCards, opponentCards)
        elif len(pari_pl) > 1 and len(pari_op) <= 1:
            return True
        elif len(pari_pl) <= 1 and len(pari_op) > 1:
            return False

        #en par
        if len(pari_pl) == 1 and len(pari_op) == 1:
            if pari_pl[0] > pari_op[0]: return  True
            elif pari_pl[0] < pari_op[0]: return False
            else:
                return self.isHighCard(playerCards, opponentCards)
        elif len(pari_pl) == 1 and len(pari_op) == 0:
            return True
        elif len(pari_pl) == 0 and len(pari_op) == 1:
            return False

        return self.isHighCard(playerCards, opponentCards)



    def payoff(self, infoSet, old_pot):
        terminal_node = isTerminalState(infoSet)
        if terminal_node != False:
            current_stage = infoSet.split("|")[(infoSet.count("|") + 1) - 1]
            player = (current_stage.count("b")) % 2

            ante = 0  # vsota ki jo vsak player da na mizo se preden dobi karte --> kasneje lahko zamenjas za small pa big blind --> je vključena ze na začetku ko nastavimo zacetni "old_pot" in "new_pot"

            # če kdo prej folda kot obicajno, pol nasprotnik dobi 1/2 pota minus zadnjo stavo(-1), ki je player ni callou
            winnings = old_pot / 2 + ante
            if terminal_node == "p0_win":
                return winnings if player == 0 else -winnings
            elif terminal_node == "p1_win":
                return winnings if player == 1 else -winnings

            if terminal_node == "call_betterCards":
                # Vsak dobi sam pol pota ker tut v resnici staviš pol ti pol opponent in dejansko si na +/- sam za polovico pota
                # Gre ravno cez pol ker sta
                winnings = old_pot/2 + ante

                global better_cards_p0
                a = better_cards_p0
                global better_cards_p1
                b = better_cards_p1
                if better_cards_p0 == "split":
                    return 0

                if player == 0:
                    return winnings if better_cards_p0 else -winnings # winnings = pot/2 + ante
                elif player == 1:
                    return winnings if better_cards_p1 else -winnings # winnings = pot/2 + ante
                else:
                    return "error"

            return "error1"

        else:
            return "continue"


    def kreiraj_sinove(self, curr_node, node_player0, node_player1, p0_nextTurn):
        # TODO mogoče je p0_nextTurn drugacen odvisno kaj stavimo...recmo bp(p0) ali pa pbp(p0 still) --> vseeno lahko je drugace se mi zdi
        # TODO mogoče zdj še ni bug in se slučajno poklapa ampak v prihodnosti ko bo current_round pbbbbb pol ne bo to slo
        # TODO reraise lahko označiš kukr samo "bb" na koncu dneva tut če je 16 rerasiov

        num_actions = nodes.num_actions(curr_node.infoSet, self.NUM_ACTIONS)
        for i in range(num_actions):
            oznaka_stave = "b" + str(i)
            new_infoset = curr_node.infoSet + oznaka_stave
            if p0_nextTurn == False:        # TODO a to pa nasledno vrstico sploh rabm?
                p0_nextTurn = nodes.isNewStage(new_infoset)

            if isTerminalState(new_infoset):    #terminal state --> naredimo payoff node
                if oznaka_stave not in node_player0.betting_map:
                    node_player0.betting_map[oznaka_stave] = nodes.node_payoff(new_infoset)
                if oznaka_stave not in node_player1.betting_map:
                    node_player1.betting_map[oznaka_stave] = nodes.node_payoff(new_infoset)
            elif nodes.isNewStage(new_infoset): #new stage state --> naredimo new cards infose
                if oznaka_stave not in node_player0.betting_map:
                    node_player0.betting_map[oznaka_stave] = nodes.node_new_cards(new_infoset)
                if oznaka_stave not in node_player1.betting_map:
                    node_player1.betting_map[oznaka_stave] = nodes.node_new_cards(new_infoset)
            else:   #sicer naredimo navaden betting node
                if oznaka_stave not in node_player0.betting_map:
                    node_player0.betting_map[oznaka_stave] = nodes.node(new_infoset) if p0_nextTurn else nodes.node_betting_map(new_infoset)
                if oznaka_stave not in node_player1.betting_map:
                    node_player1.betting_map[oznaka_stave] = nodes.node(new_infoset) if not p0_nextTurn else nodes.node_betting_map(new_infoset)


        return p0_nextTurn

    def new_stage_incoming(self, curr_node, node_player0, node_player1, cards):
        # prilagodimo node, ker je protokol ob novem stagu malo drugačen ker mora začeti p0 (tudi če je ravno igral)
        if curr_node.infoSet[-1] != '|':
            curr_node.infoSet += "|"

        # zdj preeidemo v nov node, ki je vezan na to kakšne karte padejo
        curr_game_stage = curr_node.infoSet.count("|")

        #preflop je stage 0
        if curr_game_stage == 1:
            new_cards_ = "f" + self.poVrsti([cards[4], cards[5], cards[6]])  # flop
        elif curr_game_stage == 2:
            new_cards_ = "t" + str(cards[7])  # turn
        elif curr_game_stage == 3:
            new_cards_ = "r" + str(cards[8])  # river
        else:
            return "error3"

        # create nodes if necessary --> vedno kreiramo node v p0 in node_betting_map v p1 ker na začetku staga vedno začne p0
        if new_cards_ not in node_player0.new_cards:
            node_player0.new_cards[new_cards_] = nodes.node(node_player0.infoSet)
        if new_cards_ not in node_player1.new_cards:
            node_player1.new_cards[new_cards_] = nodes.node_betting_map(node_player1.infoSet)

        return new_cards_

    def payoff_decide_between_nodes(self, node_player0, node_player1, i, p0_nextTurn, old_pot, curr_node_debug):
        oznaka_stave = "b" + str(i)
        if p0_nextTurn: #p0 next turn in trenutna poteza je bila pass
            return self.payoff(node_player0.betting_map[oznaka_stave].infoSet, old_pot)
        else:   #p1 next turn in trenutna poteza je bila pass
            return self.payoff(node_player1.betting_map[oznaka_stave].infoSet, old_pot)


    def round_on_5(self, number):
        ostanek = number % 5
        if ostanek <= 2:
            number -= ostanek
        else:
            number += (number-ostanek)

        return number

    def new_bet_amount(self, new_pot, old_pot, i, last_round, round_num):
        big_blind = 10
        stava = 0
        if round_num == 1:
            if i == 0: stava = 0
            if i == 1: stava = self.round_on_5(new_pot/4)
            if i == 2: stava = self.round_on_5(new_pot/2)

            if stava >= big_blind:
                return stava
            else:
                return big_blind

        elif round_num == 2:
            if int(last_round[round_num-2]) == 0:   #če je bila akcija pred to sedajšno stavo check , potem samo normalno bettamo
                return self.new_bet_amount(new_pot, old_pot, i, last_round, 1)
            else:   # sicer pa lahko callamo ali foldamo
                if i == 0:  # fold
                    return 0
                elif i == 1:  # call
                    return new_pot - old_pot    # --> probably sploh ne pride nikol do tuki? TODO
                else:
                    return "error"
        else:
            return "error"


    # določi kolk gre v pot zdj k je nova stava
    # zdj ne morm več iz infoseta dobit podatka o tem kolk je v potu zato morm to nost s sabo
    def new_pot_amount(self, infoSet, old_pot, new_pot, i):
        split_history = infoSet.split("|")
        last_round = split_history[len(split_history)-1].split("b")
        del last_round[0]
        last_round.append(str(i))

        if len(last_round) == 1:
            return old_pot, old_pot + self.new_bet_amount(new_pot, old_pot, i, last_round, len(last_round))
        elif len(last_round) == 2:
            #p0 check
            if int(last_round[0]) == 0 and int(last_round[1]) == 0: #check check
                return old_pot, new_pot
            elif int(last_round[0]) == 0 and int(last_round[1]) > 0:  #check bet
                new_bet = self.new_bet_amount(new_pot, old_pot, i, last_round, len(last_round))
                return old_pot, old_pot + new_bet
            #p0 bet
            elif int(last_round[1]) == 0:   # bet fold
                return old_pot, new_pot
            elif int(last_round[1]) == 1:   # bet call
                return new_pot, new_pot
            else: # bet re_raise --> tega ne igramo
                return "error", "error"

        elif len(last_round) == 3:  #check bet +
            if i == 0:  # check bet fold
                return old_pot, new_pot
            elif i == 1:    #check bet call
                return new_pot, new_pot
            else:   #v zadnjem handu lahko samo foldaš ali callaš
                return "error", "error"
        else:   #nekak mamo prazen infoset al pa je vecji od 3, kar ni pravilno
            return "error", "error"


    # player_infoset in opp_infoset se skupi cez prenasa in se oba hkrati posodabla
    # old_pot je pot, v katerem sta vsak player dala enako
    # new_pot je pot, v katerega je nek player dodatno stavil, drug player pa se ni izenacil
    def cfr(self, cards, p0, p1, node_player0, node_player1, p0_turn, old_pot, new_pot, debug):

        player = 0 if p0_turn else 1
        p0_nextTurn = False if player == 0 else True
        curr_node = node_player0 if player == 0 else node_player1
        infoSet = curr_node.infoSet

        # posodobimo in po potrebi ustvarimo nove sinove če še niso ustvarjeni
        # --> !! TO DO optimiziraj da ta informacija ze v nodih ne da vedno sprot računas --> trenutno je curr_node.newStage neki sfukan in ne kaze vedno prou
        new_stage_bool = nodes.isNewStage(infoSet)
        if new_stage_bool:
            new_cards_ = self.new_stage_incoming(curr_node, node_player0, node_player1, cards)
            infoSet = curr_node.infoSet
            # update nodes
            node_player0 = node_player0.new_cards[new_cards_]
            node_player1 = node_player1.new_cards[new_cards_]
            curr_node = node_player0 if player == 0 else node_player1
            #p0 začne na začetku vsake runde(flop, trun, river) --> tuki je false ker js v vsaki rundi gledam za eno rundo nazaj
            p0_nextTurn = False


        # Pridobimo podatke o strategiji
        num_actions = nodes.num_actions(infoSet, self.NUM_ACTIONS)
        curr_node.getStrat(p0) if player == 0 else curr_node.getStrat(p1)
        strategy = curr_node.getAvgStrat()
        util = np.zeros(num_actions)   # kolk utila mamo za bet pa kolk za pass
        nodeUtil = 0

        # Kreacija sinov v drevesu --> posebi node ce je player sedaj passou al pa ce je bettou
        p0_nextTurn = self.kreiraj_sinove(curr_node, node_player0, node_player1, p0_nextTurn)

        # prvo prevermo če je v kkšnih nodih že payoff sicer gremo v rekurzijo
        alredy_played_bets = []     # sem notr spravm kere stave sem že presimuliral da ne grem 5x stavit 0
        og_old_pot = old_pot
        og_new_pot = new_pot

        betting_round = nodes.is_betting_round(infoSet)
        for i in range(num_actions):
            old_pot,new_pot = self.new_pot_amount(infoSet, og_old_pot, og_new_pot, i)   #pogledamo kaksen je pot po trenutni stavi
            payoff = self.payoff_decide_between_nodes(node_player0, node_player1, i, p0_nextTurn, old_pot, curr_node)

            if payoff != "continue":
                util[i] = - payoff  # - pred funkcijo ker se zamenja player ko gremo v funkcijo...enako kot 4 vrstice pod tem
            else:
                oznaka_stave = "b" + str(i)
                #da ne igramo veckrat iste stave --> to delamo samo v betting round
                if betting_round:
                    nova_stava = new_pot - old_pot

                if (not betting_round) or (nova_stava not in alredy_played_bets and betting_round):  #drugi del preverja da ze nismo igrali stave s to velikostjo (npr pot/2 in pot/4 gresta na stavo 10 ker je to minimalna stava) in da smo v stanju ko stavimo --> ce smo v stanju ko ne stavimo ne gledamo ce smo neko stavo ze igrali ker imamo samo call/fold
                    if betting_round: alredy_played_bets.append(nova_stava)

                    if (player == 0):
                        util[i] = - self.cfr(cards, p0 * strategy[i], p1, node_player0.betting_map[oznaka_stave], node_player1.betting_map[oznaka_stave], p0_nextTurn, old_pot, new_pot, False)
                    else:
                        util[i] = - self.cfr(cards, p0, p1 * strategy[i], node_player0.betting_map[oznaka_stave], node_player1.betting_map[oznaka_stave], p0_nextTurn, old_pot, new_pot, False)

            nodeUtil += strategy[i] * util[i]


        # zdj pa seštejemo counter factual regret
        num_actions = nodes.num_actions(infoSet, self.NUM_ACTIONS)
        for i in range(num_actions):
            regret = util[i] - nodeUtil
            if (player == 0):
                curr_node.regretSum[i] += p1 * regret   # ORIGINAL --> p1 * regret
            else:
                curr_node.regretSum[i] += p0 * regret   # ORIGINAL --> p0 * regret

        return nodeUtil

# ----------------------------------------------------------------------------------

    # dobimo node aka. stanje v katerem smo
    def nodeInformation(self, infoSet, player):
        # v nodemapu je drevo za vsak mozni zacetni hand
        files_curr_dir = [f for f in listdir("./") if isfile(join("./", f))]    # --> treba pogledat vsakič sprot ker sproti nastajajo novi fajli...mogoce po nekaj casa lahko zbrisem to vrstico

        if player == 0:
            file_name = "p0_" + infoSet + ".pkl"
            if file_name in files_curr_dir:
                with open(file_name, 'rb') as input:
                    newNode = pickle.load(input)
            else:
                newNode = nodes.node("")   # --> ko se node kreira se ze skopirajo ostale vrednosti iz drugih nodov...ne gre iz nule
            """
            if infoSet in self.nodeMap_p0:
                newNode = self.nodeMap_p0[infoSet]
            else:
                newNode = nodes.node("")
                self.nodeMap_p0[infoSet] = newNode
            """
        elif player == 1:
            file_name = "p1_" + infoSet + ".pkl"
            if file_name in files_curr_dir:
                with open(file_name, 'rb') as input:
                    newNode = pickle.load(input)
            else:
                newNode = nodes.node_betting_map("")   # --> tuki ne rabmbo noda ker p1 na prvi potezi ne igra --> sprejmemo samo akcijo ob p0 in nato sele igra
            """
            if infoSet in self.nodeMap_p1:
                newNode = self.nodeMap_p1[infoSet]
            else:
                newNode = nodes.node_betting_map("")
                self.nodeMap_p1[infoSet] = newNode
            """
        else:
            return "error2"

        return newNode

    def poVrsti(self, cards):
        cards.sort()
        cards_string = ""
        for i in range (len(cards)):
            cards_string += str(cards[i])
            if i != len(cards)-1: cards_string += ","

        return cards_string

    def partly_shuffle(self, cards):
        # shranimo hande od playerjev
        new_deck = [cards[0], cards[1], cards[2], cards[3]]
        #pobrisemo te karte iz kupcka in nato kupcek zmesamo
        cards = cards[4:]
        #premesamo preostal del kupcka
        random.shuffle(cards)
        #zdruzimo hande in nov premesan kupcek
        new_deck += cards
        return new_deck

    def train(self, stIteracij, stIgerNaIteracijo):
        # prvi dve sta od playerja, drugi dve sta od opponenta, naslednjih 5 je na mizi
        cards = [2,2,2,2, 3,3,3,3, 4,4,4,4, 5,5,5,5, 6,6,6,6, 7,7,7,7, 8,8,8,8, 9,9,9,9, 10,10,10,10, 11,11,11,11, 12,12,12,12, 13,13,13,13, 14,14,14,14]
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
                #  v temu nodu ni vazn kaj je, ker itak bomo sli ali v bet ali pass node v temu nodeu
                # lahko damo dejansko samo slovar

                # ker ne moremo naloziti vseh nodov v ram, na enkrat nalozimo samo dva, enega za playerja in enega za opponenta
                # ker nalaganje porabi ogromno časa, bomo za vaskič ko nalozimo dva noda, s temi kartami opravili "stIgerNaIteracijo" iger, ampak z drugačnim kupckom (npr. 1000 iger)
                node_player0 = self.nodeInformation(str(player0_info), 0)
                node_player1 = self.nodeInformation(str(player1_info), 1)
                for i in range(stIgerNaIteracijo):
                    #if i % (stIgerNaIteracijo / 100) == 0:
                    #    print(i / (stIgerNaIteracijo / 100), " %")

                    cards = self.partly_shuffle(cards.copy())
                    global better_cards_p0
                    better_cards_p0 = self.betterCards(cards, 0)  # TODO BODI POZOREN NA TO FUNKCIJO
                    a = better_cards_p0
                    global better_cards_p1
                    better_cards_p1 = self.betterCards(cards, 1)
                    util += self.cfr(cards, 1, 1, node_player0, node_player1, True, 100, 100, True) # --> vsak da po 5 ante zato je začetni pot 10


                # zdj zapišemo v fajle posodoblene node --> če noda še ni naredi nov fajl
                with open("p0_" + player0_info + ".pkl", 'wb') as output:
                    pickle.dump(node_player0, output, pickle.HIGHEST_PROTOCOL)
                with open("p1_" + player1_info + ".pkl", 'wb') as output:
                    pickle.dump(node_player1, output, pickle.HIGHEST_PROTOCOL)


        print("Average game return: ", util / stIteracij)
# --------------------------------------------------------------------------------------------------



#nam pove a smo zaklučl igro/rundo al ne
def isTerminalState(infoSet):
    # pregledamo mozne bete in passe
    splitHistory = infoSet.split("|")
    gameStage = len(splitHistory)
    current_stage = (splitHistory[gameStage - 1]).split("b")
    del current_stage[0]
    stg_len = len(current_stage)

    # ce igrata do konca da odpreta karte
    if (gameStage == 4 and stg_len > 0) and nodes.isNewStage(infoSet):    #smo v zadnjem stagu in current_stage ni prazen (ker pol ga isNewStage prepozna kot nov stage) + zaklucl smo zadn stage
        return "call_betterCards"   #--> sta igrala do konca kazeta karte
    # ce nekdo nekje folda
    else:
        if len(current_stage) == 2:
            if int(current_stage[0]) > 0 and int(current_stage[1]) == 0:    # bet fold
                return "p0_win"
            else:
                return False    # pass bet
        elif len(current_stage) == 3:
            if int(current_stage[0]) == 0 and int(current_stage[1]) > 0 and int(current_stage[2]) == 0:   # check bet fold
                return "p1_win"
            else:
                return False
        else:
            return False


def tris_to_pair(trisi, pari):
    if len(trisi) > 1:
        for i in range(len(trisi)):
            if i >= 1:
                pari.append(trisi[i])

        trisi = [trisi[0]]

    return trisi, pari