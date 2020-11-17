# -*- coding: utf-8 -*-
import random

import nodes
import numpy as np
import psutil
import gc
import time

#Save files to disk
import os
from os import listdir
from os.path import isfile, join
import pickle

#Constants
BIG_BLIND = 1.0
SMALL_BLIND = 0.50
NUM_ACTIONS = 6
PLAYER_NOT_PLAY_HAND_ACTION = NUM_ACTIONS   # zaden play

##POKER_LEARNER_CFR

class Poker_Learner:
    NUM_ACTIONS = NUM_ACTIONS

    def kreiraj_sinove(self, curr_node, node_player0, node_player1, p0_nextTurn, player):

        # Če so nodi computerani, potem ne kreiramo na novo dreves
        # Še vseeno moramo kreirati drevesa v non_curr_node, saj proti drugemu playerju lahko ta player z drugačnimi kartami igra drugače --> zato njih moramo brisat
        is_not_computed = not curr_node.computed_node

        num_actions = nodes.num_actions(curr_node.infoSet, self.NUM_ACTIONS)
        for i in range(num_actions):
            oznaka_stave = "b" + str(i)
            new_infoset = curr_node.infoSet + oznaka_stave

            new_p0_nextTurn = p0_nextTurn
            if new_p0_nextTurn == False: new_p0_nextTurn = nodes.isNewStage(new_infoset)

            if player == 0:
                if isTerminalState(new_infoset):    #terminal state --> naredimo payoff node
                    if oznaka_stave not in node_player0.betting_map and is_not_computed:
                        node_player0.betting_map[oznaka_stave] = nodes.node_payoff(new_infoset)
                    if oznaka_stave not in node_player1.betting_map:
                        node_player1.betting_map[oznaka_stave] = nodes.node_payoff(new_infoset)
                elif nodes.isNewStage(new_infoset): #new stage state --> naredimo new cards infose
                    if oznaka_stave not in node_player0.betting_map and is_not_computed:
                        node_player0.betting_map[oznaka_stave] = nodes.node_new_cards(new_infoset)
                    if oznaka_stave not in node_player1.betting_map:
                        node_player1.betting_map[oznaka_stave] = nodes.node_new_cards(new_infoset)
                else:   #sicer naredimo navaden betting node
                    if oznaka_stave not in node_player0.betting_map and is_not_computed:
                        node_player0.betting_map[oznaka_stave] = nodes.node(new_infoset) if new_p0_nextTurn else nodes.node_betting_map(new_infoset)
                    if oznaka_stave not in node_player1.betting_map:
                        node_player1.betting_map[oznaka_stave] = nodes.node(new_infoset) if not new_p0_nextTurn else nodes.node_betting_map(new_infoset)
            elif player == 1:
                if isTerminalState(new_infoset):    #terminal state --> naredimo payoff node
                    if oznaka_stave not in node_player0.betting_map:
                        node_player0.betting_map[oznaka_stave] = nodes.node_payoff(new_infoset)
                    if oznaka_stave not in node_player1.betting_map and is_not_computed:
                        node_player1.betting_map[oznaka_stave] = nodes.node_payoff(new_infoset)
                elif nodes.isNewStage(new_infoset): #new stage state --> naredimo new cards infose
                    if oznaka_stave not in node_player0.betting_map:
                        node_player0.betting_map[oznaka_stave] = nodes.node_new_cards(new_infoset)
                    if oznaka_stave not in node_player1.betting_map and is_not_computed:
                        node_player1.betting_map[oznaka_stave] = nodes.node_new_cards(new_infoset)
                else:   #sicer naredimo navaden betting node
                    if oznaka_stave not in node_player0.betting_map:
                        node_player0.betting_map[oznaka_stave] = nodes.node(new_infoset) if new_p0_nextTurn else nodes.node_betting_map(new_infoset)
                    if oznaka_stave not in node_player1.betting_map and is_not_computed:
                        node_player1.betting_map[oznaka_stave] = nodes.node(new_infoset) if not new_p0_nextTurn else nodes.node_betting_map(new_infoset)


    def payoff_decide_between_nodes(self, node_player0, node_player1, i, p0_nextTurn, old_pot, curr_node_debug):
        oznaka_stave = "b" + str(i)

        # Če p1 takoj folda
        if oznaka_stave == ("b" + str(PLAYER_NOT_PLAY_HAND_ACTION)):
            return payoff(node_player1.betting_map[oznaka_stave].infoSet, 0)   # old_pot == 0, ker je p1 foldal preden je karkoli dal na mizo

        # Sicer gledamo to
        if p0_nextTurn: #p0 next turn in trenutna poteza je bila pass
            return payoff(node_player0.betting_map[oznaka_stave].infoSet, old_pot)
        else:   #p1 next turn in trenutna poteza je bila pass
            return payoff(node_player1.betting_map[oznaka_stave].infoSet, old_pot)


    # player_infoset in opp_infoset se skupi cez prenasa in se oba hkrati posodabla
    # old_pot je pot, v katerem sta vsak player dala enako
    # new_pot je pot, v katerega je nek player dodatno stavil, drug player pa se ni izenacil
    def cfr(self, cards, p0, p1, node_player0, node_player1, p0_turn, old_pot, new_pot):

        # 1. Init
        player = 0 if p0_turn else 1
        p0_nextTurn = False if player == 0 else True
        curr_node = node_player0 if player == 0 else node_player1
        infoSet = curr_node.infoSet

        # Debug
        try:
            if not (node_player0.betting_map) or not (node_player1.betting_map):
                debug = True
        except:
            pass

        # 2. posodobimo in po potrebi ustvarimo nove sinove če še niso ustvarjeni
        new_stage_bool = nodes.isNewStage(infoSet)
        if new_stage_bool:
            new_cards_ = new_stage_incoming(curr_node, node_player0, node_player1, cards)
            infoSet = curr_node.infoSet
            # update nodes
            node_player0 = node_player0.new_cards[new_cards_]
            node_player1 = node_player1.new_cards[new_cards_]
            curr_node = node_player0    #if player == 0 else node_player1               --> na začetku staga (flop, turn, river) vedno začne player0

            #p0 začne na začetku vsake runde(flop, trun, river) --> tuki je false ker js v vsaki rundi gledam za eno rundo nazaj
            player = 0
            p0_nextTurn = False


        # 3. Kreacija sinov v drevesu --> če je node computed pol ne kreiramo več novih nodov
        self.kreiraj_sinove(curr_node, node_player0, node_player1, p0_nextTurn, player)


        # 4. Pridobimo podatke o strategiji
        num_actions = nodes.num_actions(infoSet, self.NUM_ACTIONS)
        strategy = curr_node.getStrat(p0) if player == 0 else curr_node.getStrat(p1)
        #strategy = curr_node.getAvgStrat()
        util = np.zeros(num_actions)   # kolk utila mamo za bet pa kolk za pass
        nodeUtil = 0


        # 5. Tukaj pogledamo če je node že "izracunan" aka. če smo ga že tolikokrat igrali, da ga ne rabimo več igrat, ker že vemo kaj je optimalna poteza
        if curr_node.computed_node:
            strat = curr_node.getStrat(p0) if player == 0 else curr_node.getStrat(p1)
            correct_action = np.argmax(strat)
            oznaka_stave = "b" + str(correct_action)

            #payoff
            og_old_pot = old_pot
            og_new_pot = new_pot
            old_pot,new_pot = new_pot_amount(infoSet, og_old_pot, og_new_pot, correct_action)   #pogledamo kaksen je pot po trenutni stavi
            payoff = self.payoff_decide_between_nodes(node_player0, node_player1, correct_action, p0_nextTurn, old_pot, curr_node)

            if payoff != "continue":
                return - payoff  # - pred funkcijo ker se zamenja player ko gremo v funkcijo...enako kot 4 vrstice pod tem
            else:
                # strat[correct_action) je vedno 1.0, ker smo izračunal da je to najbolša opcija
                if (player == 0):
                    return - self.cfr(cards, p0 * strat[correct_action], p1, node_player0.betting_map[oznaka_stave],
                                         node_player1.betting_map[oznaka_stave], p0_nextTurn, old_pot, new_pot)
                else:
                    return - self.cfr(cards, p0, p1 * strat[correct_action], node_player0.betting_map[oznaka_stave],
                                         node_player1.betting_map[oznaka_stave], p0_nextTurn, old_pot, new_pot)


        # prvo prevermo če je v kkšnih nodih že payoff sicer gremo v rekurzijo
        alredy_played_bets = []     # sem notr spravm kere stave sem že presimuliral da ne grem 5x stavit 0
        og_old_pot = old_pot
        og_new_pot = new_pot

        # 6. Če node ni "computed" potem naredimo rekurzijo
        betting_round = nodes.is_betting_round(infoSet)
        for i in range(num_actions):
            old_pot,new_pot = new_pot_amount(infoSet, og_old_pot, og_new_pot, i)   #pogledamo kaksen je pot po trenutni stavi
            payoff = self.payoff_decide_between_nodes(node_player0, node_player1, i, p0_nextTurn, old_pot, curr_node)

            if payoff != "continue":
                util[i] = - payoff  # - pred funkcijo ker se zamenja player ko gremo v funkcijo...enako kot 4 vrstice pod tem
            else:
                oznaka_stave = "b" + str(i)

                if (player == 0):
                    util[i] = - self.cfr(cards, p0 * strategy[i], p1, node_player0.betting_map[oznaka_stave], node_player1.betting_map[oznaka_stave], p0_nextTurn, old_pot, new_pot)
                else:
                    util[i] = - self.cfr(cards, p0, p1 * strategy[i], node_player0.betting_map[oznaka_stave], node_player1.betting_map[oznaka_stave], p0_nextTurn, old_pot, new_pot)

            nodeUtil += strategy[i] * util[i]


        # 6. zdj pa seštejemo counter factual regret
        # UPDATE: namesto da dodajamo negativne vrednosti, dodamo |negativna_vrednost|/num_actions vsem ostalim nodom
        num_actions = nodes.num_actions(infoSet, self.NUM_ACTIONS)
        for i in range(num_actions):
            regret = util[i] - nodeUtil
            # calling round
            if(num_actions==2 and regret < 0 and player == 0):
                curr_node.regretSum[1-i] += p1 * -regret
            elif (num_actions==2 and regret < 0 and player == 1):
                curr_node.regretSum[1-i] += p0 * -regret

            else:
                # betting round
                if (player == 0):
                    curr_node.regretSum[i] += p1 * regret   # ORIGINAL --> p1 * regret
                else:
                    curr_node.regretSum[i] += p0 * regret   # ORIGINAL --> p0 * regret

        return nodeUtil

# ----------------------------------------------------------------------------------

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

    def train(self, stIgerNaIteracijo, st_min_izvajanja):
        max_program_time_minutes = st_min_izvajanja
        start_time = time.time()

        # prvi dve sta od playerja, drugi dve sta od opponenta, naslednjih 5 je na mizi
        cards = [2,2,2,2, 3,3,3,3, 4,4,4,4, 5,5,5,5, 6,6,6,6, 7,7,7,7, 8,8,8,8, 9,9,9,9, 10,10,10,10, 11,11,11,11, 12,12,12,12, 13,13,13,13, 14,14,14,14]
        util = 0

        continue_loop = True
        game_num = 0
        while continue_loop:
            game_num += 1

            random.shuffle(cards)
            player0_info = poVrsti([cards[0], cards[1]])
            player1_info = poVrsti([cards[2], cards[3]])

            #logs
            f = open("logs.txt", "a")
            write_str = str(game_num) + "==>    p0_cards:" + player0_info + "        p1_cards:" + player1_info + "                                     Lahko Ustavis\n"
            f.write(write_str)
            f.close()


            # ker ne moremo naloziti vseh nodov v ram, na enkrat nalozimo samo dva, enega za playerja in enega za opponenta
            # ker nalaganje porabi ogromno časa, bomo za vaskič ko nalozimo dva noda, s temi kartami opravili "stIgerNaIteracijo" iger, ampak z drugačnim kupckom (npr. 1000 iger)
            node_player0 = nodeInformation(str(player0_info), 0)
            node_player1 = nodeInformation(str(player1_info), 1)

            gc.collect()    # --> force garbage collector

            for j in range(stIgerNaIteracijo):
                if ((time.time() - start_time) / 60) > max_program_time_minutes:
                    #print("num of games simulated:" , game_num)
                    continue_loop = False
                    break

                cards = self.partly_shuffle(cards.copy())
                global better_cards_p0
                better_cards_p0 = betterCards(cards, 0)  # TODO BODI POZOREN NA TO FUNKCIJO
                a = better_cards_p0
                global better_cards_p1
                better_cards_p1 = betterCards(cards, 1)
                util += self.cfr(cards, 1, 1, node_player0, node_player1, False, BIG_BLIND, BIG_BLIND) # na poker starsu je BB 100, SM 50 pri heads up za 10k....50 obema odbijem v payoffu kot ante, p0 pa tukaj da se 50 na kup


            #logs
            process = psutil.Process(os.getpid())
            f = open("logs.txt", "a")
            write_str = "Program ob koncu simulacije porabi:" + str(process.memory_info()[0] / (1024 * 1024)) + " MB rama                                    Ne Ustavit\n"
            f.write(write_str)
            f.close()

            # zdj zapišemo v fajle posodoblene node --> če noda še ni naredi nov fajl
            f = open("logs.txt", "a")
            f.write("writing p0_info\n")
            f.close()

            with open("p0_" + player0_info + ".pkl", 'wb') as output:
                pickle.dump(node_player0, output, pickle.HIGHEST_PROTOCOL)

            f = open("logs.txt", "a")
            f.write("writing p1_info \n")
            f.close()

            with open("p1_" + player1_info + ".pkl", 'wb') as output:
                pickle.dump(node_player1, output, pickle.HIGHEST_PROTOCOL)

            del node_player0
            del node_player1
            f = open("logs.txt", "a")
            write_str = "Program po brisanju porabi porabi:" + str(process.memory_info()[0] / (1024 * 1024)) + " MB rama                                    Ne Ustavit\n\n\n"
            f.write(write_str)
            f.close()


        print("Average game return: ", util / (game_num * stIgerNaIteracijo))
# --------------------------------------------------------------------------------------------------


# dobimo node aka. stanje v katerem smo
def nodeInformation(infoSet, player):
    # v nodemapu je drevo za vsak mozni zacetni hand
    files_curr_dir = [f for f in listdir("./") if isfile(join("./", f))]    # --> treba pogledat vsakič sprot ker sproti nastajajo novi fajli...mogoce po nekaj casa lahko zbrisem to vrstico

    if player == 0:
        file_name = "p0_" + infoSet + ".pkl"
        if file_name in files_curr_dir:
            with open(file_name, 'rb') as input:
                newNode = pickle.load(input)
        else:
            newNode = nodes.node_betting_map("")    # --> tuki ne rabmo node, ker p0 avtomatsko na začetku da big blind in dejansko ne začne

    elif player == 1:
        file_name = "p1_" + infoSet + ".pkl"
        if file_name in files_curr_dir:
            with open(file_name, 'rb') as input:
                newNode = pickle.load(input)
        else:
            newNode = nodes.node("")   # --> tuki rabmo node, ker p1 prvi igra v novi igri, saj ima p0 začetno stavo aka BIG BLIND +  # --> b11 = znak za big blind

    else:
        return "error2"

    return newNode

# Po vrsti
def poVrsti(cards):
    cards.sort()
    cards_string = ""
    for i in range (len(cards)):
        cards_string += str(cards[i])
        if i != len(cards)-1: cards_string += ","

    return cards_string

#nam pove a smo zaklučl igro/rundo al ne
def isTerminalState(infoSet):
    # pregledamo mozne bete in passe
    splitHistory = infoSet.split("|")
    gameStage = len(splitHistory)
    current_stage = (splitHistory[gameStage - 1]).split("b")
    del current_stage[0]
    stg_len = len(current_stage)


    # če p1 ne igra --> folda brez da izenači big blind
    if infoSet == "b" + str(PLAYER_NOT_PLAY_HAND_ACTION):
        return "p0_win"


    # ce igrata do konca da odpreta karte
    elif (gameStage == 4 and stg_len > 0) and nodes.isNewStage(infoSet):    #smo v zadnjem stagu in current_stage ni prazen (ker pol ga isNewStage prepozna kot nov stage) + zaklucl smo zadn stage
        return "call_betterCards"   #--> sta igrala do konca kazeta karte
    # ce nekdo nekje folda
    else:
        if len(current_stage) == 2:
            if int(current_stage[0]) > 0 and int(current_stage[1]) == 0:    # bet fold
                return "p0_win" if gameStage != 0 else "p1_win"     # --> on preflop roles (who plays first) are reversed, that is why p1 wins in gamestage 0
            else:
                return False    # pass bet
        elif len(current_stage) == 3:
            if int(current_stage[0]) == 0 and int(current_stage[1]) > 0 and int(current_stage[2]) == 0:   # check bet fold
                return "p1_win" if gameStage != 0 else "p0_win"     # --> on preflop roles are reversed, that is why p1 wins in gamestage 0
            else:
                return False
        else:
            return False


def payoff(infoSet, old_pot):
    terminal_node = isTerminalState(infoSet)
    if terminal_node != False:
        current_stage = infoSet.split("|")[(infoSet.count("|") + 1) - 1]
        player = (current_stage.count("b")) % 2

        # če kdo prej folda kot obicajno, pol nasprotnik dobi 1/2 pota minus zadnjo stavo(-1), ki je player ni callou
        winnings = old_pot / 2
        if terminal_node == "p0_win":
            return winnings if player == 0 else -winnings
        elif terminal_node == "p1_win":
            return winnings if player == 1 else -winnings

        if terminal_node == "call_betterCards":
            # Vsak dobi sam pol pota ker tut v resnici staviš pol ti pol opponent in dejansko si na +/- sam za polovico pota
            # Gre ravno cez pol ker sta
            winnings = old_pot/2

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

def new_bet_amount(new_pot, old_pot, action, last_round, round_num, first_bet=False):
    stava = 0

    if round_num == 1:  # --> betting round
        # Če smo pri prvi stavi, ko se player odloča ali bo igral ali ne
        if first_bet:
            if action == PLAYER_NOT_PLAY_HAND_ACTION: return 0 # --> foldamo
            else: stava += BIG_BLIND

        if action == 0: stava += 0
        elif action == 1: stava += 1
        elif action == 2: stava += 3
        elif action == 3: stava += 8
        elif action == 4: stava += 20
        elif action == 5: stava += 50

        if old_pot + stava/2 > 100:
            return (100-old_pot) / 2    # --> allin
        else:
            return stava

    elif round_num == 2:
        if int(last_round[round_num-2]) == 0:   #če je bila akcija pred to sedajšno stavo check , potem samo normalno bettamo
            return new_bet_amount(new_pot, old_pot, action, last_round, 1)
        else:   # sicer pa lahko callamo ali foldamo
            if action == 0: return 0  # fold
            elif action == 1:
                return new_pot - old_pot    # call --> probably sploh ne pride nikol do tuki? TODO
            else: return "error"
    else:
        return "error"


# določi kolk gre v pot zdj k je nova stava
# zdj ne morm več iz infoseta dobit podatka o tem kolk je v potu zato morm to nost s sabo
def new_pot_amount(infoSet, old_pot, new_pot, action):
    if action == 6: # --> takojšen fold
        return 0, 1

    split_history = infoSet.split("|")
    last_round = split_history[len(split_history)-1].split("b")
    del last_round[0]
    last_round.append(str(action))

    if len(last_round) == 1:
        first_bet = True if infoSet == "" else False
        new_pot = old_pot + new_bet_amount(new_pot, old_pot, action, last_round, len(last_round), first_bet)
        old_pot = old_pot + BIG_BLIND if action != PLAYER_NOT_PLAY_HAND_ACTION else old_pot  # --> če player1 ni igral igre, potem ne povečamo pota
        return old_pot, new_pot

    elif len(last_round) == 2:
        #p0 check
        if int(last_round[0]) == 0 and int(last_round[1]) == 0: #check check
            return old_pot, new_pot
        elif int(last_round[0]) == 0 and int(last_round[1]) > 0:  #check bet
            new_bet = new_bet_amount(new_pot, old_pot, action, last_round, len(last_round))
            return old_pot, old_pot + new_bet
        #p0 bet
        elif int(last_round[1]) == 0:   # bet fold
            return old_pot, new_pot
        elif int(last_round[1]) == 1:   # bet call
            opponent_bet = new_pot-old_pot
            new_pot += opponent_bet # izenačimo stavo
            if new_pot > 100:
                new_pot = 100
            return new_pot, new_pot
        else: # bet re_raise --> tega ne igramo
            return "error", "error"

    elif len(last_round) == 3:  #check bet +
        if action == 0:  # check bet fold
            return old_pot, new_pot
        elif action == 1:    #check bet call
            opponent_bet = new_pot-old_pot
            new_pot += opponent_bet # izenačimo stavo
            if new_pot > 100:
                new_pot = 100
            return new_pot, new_pot
        else:   #v zadnjem handu lahko samo foldaš ali callaš
            return "error", "error"
    else:   #nekak mamo prazen infoset al pa je vecji od 3, kar ni pravilno
        return "error", "error"


def new_stage_incoming(curr_node, node_player0, node_player1, cards):
    # ob novem stagu mora začeti p0 (tudi če je ravno igral)
    if node_player0.infoSet[-1] != '|':
        node_player0.infoSet += "|"
    if node_player1.infoSet[-1] != '|':
        node_player1.infoSet += "|"

    # zdj preeidemo v nov node, ki je vezan na to kakšne karte padejo
    curr_game_stage = curr_node.infoSet.count("|")

    #preflop je stage 0
    if curr_game_stage == 1:
        new_cards_ = "f" + poVrsti([cards[4], cards[5], cards[6]])  # flop
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


def tris_to_pair(trisi, pari):
    if len(trisi) > 1:
        for i in range(len(trisi)):
            if i >= 1:
                pari.append(trisi[i])

        trisi = [trisi[0]]

    return trisi, pari

#check if a player has a straight
def get_that_straight(cards):
    cards.sort(reverse=True)
    curr_high = -1
    num_of_consecutive_cards = 0

    #ko najdemo prvo zaporedje 5ih kart, breakamo
    curr_high = cards[0]
    num_of_consecutive_cards = 1
    for i in range(len(cards)): #range je ponavad 7....2 v roki + 2 na mizi
        if i != 0:
            if cards[i] == cards[i-1] - 1:
                num_of_consecutive_cards += 1
            elif cards[i] != cards[i-1]:    #če ima kdo v lestvici dve enaki karti npr J,10,9,8,8,7,3
                curr_high = cards[i]
                num_of_consecutive_cards = 1
        if num_of_consecutive_cards == 5:
            return curr_high

    #nismo našli lestvice
    return -1




#pove če ima player high card
def isHighCard(playerCards, opponentCards):
    playerCards.sort(reverse=True)
    opponentCards.sort(reverse=True)
    for i in range(5):
        if playerCards[i] > opponentCards[i]:
            return True
        elif playerCards[i] < opponentCards[i]:
            return False
    return "split"



def betterCards(cards,player):  # --> return TRUE ce ma players bolse karte in FALSE ce ma slabse
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
                return isHighCard(playerCards, opponentCards)

    elif len(trisi_pl) > 0 and len(pari_pl) > 0 and (len(trisi_op) == 0 or len(pari_op) == 0):  #player ma full opp ne
        return True
    elif len(trisi_op) > 0 and len(pari_op) > 0 and (len(trisi_pl) == 0 or len(pari_pl) == 0):  # opp ma full player ne
        return False

    #lestvica
    player_straight = get_that_straight(playerCards)
    bot_straight = get_that_straight(opponentCards)

    if player_straight > bot_straight:
        return True
    elif player_straight < bot_straight:
        return False
    elif player_straight != -1 and bot_straight != -1 and player_straight == bot_straight:  # --> oba isti straight
        return "split"

    #tris
    if len(trisi_pl) > 0 and len(trisi_op) > 0: #oba tris
        if trisi_pl[0] > trisi_op[0]:
            return True
        elif trisi_pl[0] < trisi_op[0]:
            return False
        else:   #isti tris
            return isHighCard(playerCards, opponentCards)
    elif len(trisi_pl) > 0 and len(trisi_op) == 0:
        return True
    elif len(trisi_pl) == 0 and len(trisi_op) > 0:
        return False

    #dva para
    if len(pari_pl) > 1 and len(pari_op) > 1:   #oba mata 2 para
        if pari_pl[0] > pari_op[0]: return True
        elif pari_pl[0] < pari_op[0]: return False
        else:   #isti top pair
            if pari_pl[1] > pari_op[1]: return True
            elif pari_pl[1] < pari_op[1]: return False
            else:   # isti second pair
                return isHighCard(playerCards, opponentCards)
    elif len(pari_pl) > 1 and len(pari_op) <= 1:
        return True
    elif len(pari_pl) <= 1 and len(pari_op) > 1:
        return False

    #en par
    if len(pari_pl) == 1 and len(pari_op) == 1:
        if pari_pl[0] > pari_op[0]: return  True
        elif pari_pl[0] < pari_op[0]: return False
        else:
            return isHighCard(playerCards, opponentCards)
    elif len(pari_pl) == 1 and len(pari_op) == 0:
        return True
    elif len(pari_pl) == 0 and len(pari_op) == 1:
        return False

    return isHighCard(playerCards, opponentCards)
