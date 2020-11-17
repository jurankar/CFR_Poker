# -*- coding: utf-8 -*-
import random
from random import random as randDec
import numpy as np
import pickle
import datetime
import time

import nodes
import cfr_poker

global game_infoset
ZAČETNO_STANJE = 50
SMALL_BLIND = 0.50
BIG_BLIND = SMALL_BLIND * 2


# COPY PASTE FUNCTIONS

def payoff(infoSet, old_pot):
    terminal_node = cfr_poker.isTerminalState(infoSet)
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

def num_to_card(number):
    if number <= 10:
        return str(number)
    elif number == 11:
        return "J"
    elif number == 12:
        return "Q"
    elif number == 13:
        return "K"
    elif number == 14:
        return "A"
    else:
        return "err"


# -------------------------------------------------------------------------------------------------------------------------



def bet_amount_fun(action):
    stava = 0
    global game_infoset
    if game_infoset == "":
        stava += BIG_BLIND  # začetek

    if action == 0: stava += 0
    elif action == 1: stava += 1
    elif action == 2: stava += 3
    elif action == 3: stava += 8
    elif action == 4: stava += 20
    elif action == 5: stava += 50
    elif action == 6: return 0

    return stava




# Get bot action
#Tukaj se uporabijo naši natrenirani nodi
#Bet nam pove ali je player pred nami bettou...če je bet false, potem je checkou
def get_bot_action(node, pot_amount, opponent_bet):

    if opponent_bet == 0:
        bet = False
    else:
        bet = True

    strategy = node.getAvgStrat()
    action_num = "unset"

    rand_num = randDec()  #ali igramo z action 0 v nodu
    sum_rand_num = 0
    for index, strat_prob  in enumerate(strategy):
        sum_rand_num += strat_prob
        if sum_rand_num >= rand_num:
            action_num = index
            break;

    action_info = "b" + str(action_num)

    if bet:
        action = "fold" if action_num == 0 else "call"   #p0 je bettou --> mi lahko foldamo ali callamo
    else:
        action = "check" if action_num == 0 else "raise" #p0 ni bettou --> mi lahko checkamo ali raisamo
        if action_num == 6:
            action = "fold"     # ko p1 folda takoj na zacetku

    if action == "fold":
        return action,action_info, 0
    elif action == "call":
        return action, action_info, opponent_bet

    elif action == "check":
        return action, action_info, 0
    elif action == "raise":
        return action, action_info, bet_amount_fun(action_num)
    else:
        return "error"


def bot_action_fun(node, pot_amount, opponent_bet):
    if opponent_bet > 0:  #opponent je bettou
        action, action_info, bot_bet = get_bot_action(node, pot_amount, opponent_bet)
    else:   #opponent je checkou
        action, action_info, bot_bet = get_bot_action(node, pot_amount, 0)

    pot_amount += bot_bet

    return action, action_info, bot_bet




def generate(num_of_games=100000):

    file_path = "Analysis/Bot/datasets/dataset.txt"

    cards = [2, 2, 2, 2, 3, 3, 3, 3, 4, 4, 4, 4, 5, 5, 5, 5, 6, 6, 6, 6, 7, 7, 7, 7, 8, 8, 8, 8, 9, 9, 9, 9, 10, 10, 10,
             10, 11, 11, 11, 11, 12, 12, 12, 12, 13, 13, 13, 13, 14, 14, 14, 14]

    # Ta node uporabimo ko naš node ni naučen --> z več učenja tega ne bomo več potrebovali
    node_random = nodes.node("b1")
    for i in range(len(node_random.strategySum)):
        node_random.strategySum[i] = 1 / len(node_random.strategySum)

    #print("How many games do we generate?")
    counter = 0

    start_time = time.time()
    while counter < int(num_of_games):
        counter += 1
        print(counter)

        # ponastavimo infoset
        max_pot = 2 * ZAČETNO_STANJE    # več od tega ne more biti, ker sta oba bota porabila svoj denar

        #zmešamo in razdelimo karte
        random.shuffle(cards)
        old_pot = BIG_BLIND  # p0 big blind
        new_pot = BIG_BLIND

        # Write to file
        f = open(file_path, "a")
        f.write("Game started at: " + str(datetime.datetime.now()) + "\n")
        f.write("Game ID: " + str(counter) + " " + str(SMALL_BLIND) + "/" + str(BIG_BLIND) + "   Hold'em\n")
        f.write("Seat 1: Bot1 (50).\n")
        f.write("Seat 2: Bot2 (50).\n")
        f.write("Player Bot1 has big blind (1)\n")
        f.write("Player Bot1 received a card " + num_to_card(cards[0]) + ".\n")
        f.write("Player Bot1 received a card " + num_to_card(cards[1]) + ".\n")
        f.write("Player Bot2 received a card " + num_to_card(cards[2]) + ".\n")
        f.write("Player Bot2 received a card " + num_to_card(cards[3]) + ".\n")


        #init the bots
        bot_0_cards = cfr_poker.poVrsti([cards[0], cards[1]])
        bot_1_cards = cfr_poker.poVrsti([cards[2], cards[3]])
        bot_0_node = cfr_poker.nodeInformation(bot_0_cards, 0)
        bot_1_node = cfr_poker.nodeInformation(bot_1_cards, 1)
        bot_in_action = 1   # ker ima p0 big blind

        # Init the variables
        global game_infoset
        game_infoset = ""
        opponent_bet = 0
        isRiver = False
        game_ended = False
        winner = "none"

        global better_cards_p0
        better_cards_p0 = cfr_poker.betterCards(cards, 0)
        a = better_cards_p0
        global better_cards_p1
        better_cards_p1 = cfr_poker.betterCards(cards, 1)



        #smo v tem loopu, dokler player spet ni konec igre
        while(not game_ended):
            debug = game_infoset

            if payoff(game_infoset, old_pot) != "continue":
                payoff_value = payoff(game_infoset, old_pot)
                winner = bot_in_action if payoff_value > 0 else (1-bot_in_action)
                #f.write("Bot" + str(winner) + " won")
                # glede na playerja veš kdo je zmagu
                game_ended = True
                break

            elif nodes.isNewStage(game_infoset):
                # Dodamo '|' v novem stagu
                game_infoset += "|"
                # Pokazemo nove karte
                curr_node = bot_0_node if bot_in_action == 0 else bot_1_node
                try:
                    new_cards_ = cfr_poker.new_stage_incoming(curr_node, bot_0_node, bot_1_node, cards)
                except: new_cards_ = "err"
                try:
                    bot_0_node = bot_0_node.new_cards[new_cards_]
                except: bot_0_node = node_random
                try:
                    bot_1_node = bot_1_node.new_cards[new_cards_]
                except: bot_1_node = node_random


                # Ponastavimo variable
                bot_in_action = 0
                opponent_bet = 0
                bot_bet = 0
                # Zapišemo v file
                game_stage = game_infoset.count("|")
                if game_stage == 1: f.write("*** FLOP ***: [" + num_to_card(cards[4]) + " " + num_to_card(cards[5]) + " " + num_to_card(cards[6]) + "]\n")
                if game_stage == 2: f.write("*** TURN ***: [" + num_to_card(cards[7]) + "]\n")
                if game_stage == 3:
                    f.write("*** RIVER ***: [" + num_to_card(cards[8]) + "]\n")
                    isRiver = True

            # Tukaj sedaj zamenjamo node
            node = bot_0_node if bot_in_action == 0 else bot_1_node
            bot_action, action_info, bot_bet = bot_action_fun(node, old_pot, opponent_bet)
            action_num = int(action_info[-1])
            old_pot, new_pot = cfr_poker.new_pot_amount(game_infoset, old_pot, new_pot, action_num)
            if new_pot*2 >= 100:
                bot_action = "allin"

            f.write("Player Bot" + str(bot_in_action) + " " + bot_action + "s")
            f.write(" (" + str(bot_bet) + ")\n") if (bot_action != "fold" and bot_action != "check") else f.write("\n")
            game_infoset += action_info

            # Posodobimo node
            debug = game_infoset
            try:
                bot_0_node = bot_0_node.betting_map[action_info]
            except: bot_0_node = node_random

            try:
                bot_1_node = bot_1_node.betting_map[action_info]
            except: bot_1_node = node_random

            opponent_bet = bot_bet
            bot_bet = 0
            bot_in_action = 1 - bot_in_action

        # Zaključena igra, sedaj napišemo summary
        f.write("------ Summary ------\n")
        f.write("Board: [" + num_to_card(cards[4]) + " " + num_to_card(cards[5]) + " " + num_to_card(cards[6]) + " " + num_to_card(cards[7]) + " " + num_to_card(cards[8]) + "]\n")
        if isRiver:
            winner_cards = num_to_card(cards[0]) + ", " + num_to_card(cards[1]) if winner==0 else num_to_card(cards[2]) + ", " + num_to_card(cards[3])
            f.write("Player Bot" + str(winner) + " shows cards: " + winner_cards + "\n")
            f.write("Player Bot" + str(1-winner) + " does not show cards\n")
        else:
            f.write("Player Bot" + str(winner) + " does not show cards\n")
            f.write("Player Bot" + str(1-winner) + " does not show cards\n")
        f.write("Game ended at: " + str(datetime.datetime.now()) + "\n\n")
        f.close()

    print("Čas izvajanja programa: ", (time.time() - start_time), " sekund. To je ", (time.time() - start_time)/60," minut, kar je ", (time.time() - start_time)/60/int(num_of_games), "minut na igro")
