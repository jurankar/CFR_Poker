import tkinter as tk
import cfr_poker
import nodes
import random
from random import random as randDec
import numpy as np

import pickle

#SETTINGS
HEIGHT = 800
WIDTH = 1200
ZAČETNO_STANJE = 1000
SMALL_BLIND = 10
BIG_BLIND = SMALL_BLIND * 2

#GAME VARIABLES
global Player_stanje
Player_stanje = ZAČETNO_STANJE
global Bot_stanje
Bot_stanje = ZAČETNO_STANJE
Player = 0  #ali player začne prvi(0) ali drugi(1) --> switchamo po vsaki igri
cards = [2,2,2,2, 3,3,3,3, 4,4,4,4, 5,5,5,5, 6,6,6,6, 7,7,7,7, 8,8,8,8, 9,9,9,9, 10,10,10,10, 11,11,11,11, 12,12,12,12, 13,13,13,13, 14,14,14,14]
global infoSet
infoSet = ""
global pot_amount
pot_amount = 0
global player_start
player_start = True  # kdo začne stage --> true če player, false če bot

global bet_amount_bot
bet_amount_bot = 0
global bet_amount_player
bet_amount_player = 0

global bot_node

#-------------------------------------------------------------------------------------------

#IGRA --> vsakič ko pritisnemo gumb, igramo

def payoff(infoSet, old_pot):
    a = cards
    terminal_node = cfr_poker.isTerminalState(infoSet)
    if terminal_node != False:
        current_stage = infoSet.split("|")[(infoSet.count("|") + 1) - 1]
        player = (current_stage.count("b")) % 2

        ante = 10  # vsota ki jo vsak player da na mizo se preden dobi karte --> kasneje lahko zamenjas za small pa big blind --> je vključena ze na začetku ko nastavimo zacetni "old_pot" in "new_pot"

        # če kdo prej folda kot obicajno, pol nasprotnik dobi 1/2 pota minus zadnjo stavo(-1), ki je player ni callou
        winnings = old_pot / 2 + ante
        if terminal_node == "p0_win":
            return winnings if player == 0 else -winnings
        elif terminal_node == "p1_win":
            return winnings if player == 1 else -winnings

        if terminal_node == "call_betterCards":
            # Vsak dobi sam pol pota ker tut v resnici staviš pol ti pol opponent in dejansko si na +/- sam za polovico pota
            # Gre ravno cez pol ker sta
            winnings = old_pot / 2 + ante
            better_cards_p0 = cfr_poker.Poker_Learner.betterCards("", cards, player)
            if better_cards_p0 == "split":
                return 0

            if player == 0:
                return winnings if better_cards_p0 else -winnings  # winnings = pot/2 + ante
            elif player == 1:
                better_cards_p1 = cfr_poker.Poker_Learner.betterCards("", cards, player)
                return winnings if better_cards_p1 else -winnings  # winnings = pot/2 + ante
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

def show_cards(game_stage):
    print("show_cards")
    if game_stage == 1:
        text = num_to_card(cards[4]) + " " + num_to_card(cards[5]) + " " + num_to_card(cards[6])
    elif game_stage == 2:
        text = num_to_card(cards[4]) + " " + num_to_card(cards[5]) + " " + num_to_card(cards[6]) + " " + num_to_card(cards[7])
    elif game_stage == 3:
        text = num_to_card(cards[4]) + " " + num_to_card(cards[5]) + " " + num_to_card(cards[6]) + " " + num_to_card(cards[7]) + " " + num_to_card(cards[8])
    label_cards_table["text"] = text

def bet_type_fun(bet_amount, pot_amount):
    # v tej funkciji determiniram kateremu tipu stave (od vseh moznih tipov smo blizje)
    # mozne stave v mojem programu sta pot/2 in pa pot
    # najti moram kateremu je blizja
    half_pot = pot_amount / 2
    pot = pot_amount

    half_pot_diff = abs(half_pot - bet_amount)
    pot_diff = abs(pot - bet_amount)

    #aproksimiramo tisti tip stave, ki je blizji
    if half_pot_diff < pot_diff:
        return "b1"
    else:
        return "b2"

def player_action(action, infoSet, pot_amount):
    global bet_amount_bot
    global bet_amount_player

    if action == "fold/check":
        infoSet += "b0"

    if action == "call":    #check in call sta ista akcija in isti gumb
        infoSet += "b1"
        pot_amount += bet_amount_bot  # izenačimo stavo od bota
        bet_amount_bot = 0

    if action == "raise":
        bet_amount_player = bet_amount_player - bet_amount_bot
        bet_amount_bot = 0
        if bet_amount_player <= 0 :
            print("error bruh2")
            label_game_info["text"] = "error bruh --> ne cheatat feget" # TODO zbriš preden pošlš profesorju
        infoSet += bet_type_fun(bet_amount_player, pot_amount)
        pot_amount += bet_amount_player

    return infoSet, pot_amount


#Tukaj se uporabijo naši natrenirani nodi
#Bet nam pove ali je player pred nami bettou...če je bet false, potem je checkou
def get_bot_action(node, bet, bet_amount_player):
    strategy = getAvgStrat(node)

    action_0 = randDec() < strategy[0]  #ali igramo z action 0 v nodu
    if bet:
        action = "fold" if action_0 else "call"   #p0 je bettou --> mi lahko foldamo ali callamo
    else:
        action = "check" if action_0 else "raise" #p0 ni bettou --> mi lahko checkamo ali raisamo

    if action == "fold":
        return action, bet_amount_player
    elif action == "call":
        return action, 2*bet_amount_player
    elif action == "check":
        return action, 0
    elif action == "raise":
        return action, pot_amount*1.5   #ko raisamo, raisamo za 1/2 pota, ni vazn kolk je stavu player


#TODO tuki naprej --> zrihti zdj da se prešteje kolk je pol v potu glede na to koliko je kdo stavil


def bot_action(infoSet, pot_amount):
    global bet_amount_bot
    global bet_amount_player
    global bot_node

    if bet_amount_player > 0:  #player je bettou
        bot_node = bot_node.betting_map["b"]
        infoSet += "b1"

        pot_amount += bet_amount_player #izenačimo stavo od playeja
        bot_action = get_bot_action(bot_node, True, pot_amount)

        bet_amount_player = 0
        return "call", infoSet, pot_amount

    else:   #player je checkou
        bot_node = bot_node.betting_map["p"]
        infoSet += "b0"
        return "check", infoSet, pot_amount


#pove nam ali je naslednjo rundo na vrsti player ali bot
def next_move_player(player_start, infoSet, player_move):
    splitHistory = infoSet.split("|")
    his_len = len(splitHistory)
    last_round = splitHistory[his_len-1]

    #če je nou stage začne p0 (tisti ki začne stage, player ali bot)
    if nodes.isNewStage(infoSet):
        infoSet += "|"
        #pokazemo karte ko je nov stage
        game_stage = infoSet.count("|")
        if game_stage > 0:  # and nodes.isNewStage(infoSet)
            show_cards(game_stage)
        return player_start, infoSet
    #če ni nou stage pa samo zamenjamo igarlca
    else:
        new_player_move = not player_move
        return new_player_move, infoSet


#razdelimo denar med igralce...in pa ponastavimo parametre
def winnings_fun(winnings, infoSet, player_start):
    current_stage = infoSet.split("|")[(infoSet.count("|") + 1) - 1]
    player = (current_stage.count("b")) % 2 # --> player 0 je tisti ki začne stage
    global Player_stanje
    global Bot_stanje

    # če je p0 == player in da je trenutni player == 0   ALI p0 == bot in player == 1 --> potem playerju pristejemo winningse, botu pa odstejemo
    if (player_start and player == 0) or (not player_start and player == 1):
        Player_stanje += winnings
        Bot_stanje -= winnings
        label_game_info["text"] = "Konec igre, player je dobil: " + str(winnings) + "     in playerjevo novo stanje je:" + str(Player_stanje)
    else:
        Player_stanje -= winnings
        Bot_stanje += winnings
        label_game_info["text"] = "Konec igre, bot je dobil: " + str(-winnings) + "     in playeryevo novo stanje je:" + str(Player_stanje)

    label_ply_stanje["text"] = "Stanje player: " + str(Player_stanje)
    label_bot_stanje["text"] = "Stanje bot: " + str(Bot_stanje)
    label_bot_cards["text"] = "BOT cards: " + num_to_card(cards[2]) + " " + num_to_card(cards[3]) if player_start else "BOT cards: " + num_to_card(cards[0]) + " " + num_to_card(cards[1])


def poVrsti(cards):
    cards.sort()
    cards_string = ""
    for i in range (len(cards)):
        cards_string += str(cards[i])
        if i != len(cards)-1: cards_string += ","

    return cards_string

def getAvgStrat(node):
    num_actions = len(node.regretSum)
    avgStrat = np.zeros(num_actions)
    normalizingSum = 0
    for i in range(num_actions):
        normalizingSum += node.strategySum[i]
    for i in range(num_actions):
        if(normalizingSum > 0):
            avgStrat[i] = node.strategySum[i] / normalizingSum
        else:
            avgStrat[i] = 1.0 / num_actions

    return avgStrat

def get_bot_node(player_start):

    if player_start:    #če je player == p0
        bot_cards = poVrsti([cards[2], cards[3]])
        file_name = "../p1_" + bot_cards + ".pkl"
        with open(file_name, 'rb') as input:
            botNode = pickle.load(input)

    else:   #če je bot == p0
        bot_cards = poVrsti([cards[0], cards[1]])
        file_name = "../p0_" + bot_cards + ".pkl"
        with open(file_name, 'rb') as input:
            botNode = pickle.load(input)

    return botNode



def play(action, bet_amount):   # --> amount gledamo samo pri raisu

    #init
    global infoSet
    debug1 = infoSet
    global pot_amount
    debug2 = pot_amount
    global player_start
    player_move = True  #kdo je naslednji na potezi
    global new_player_move_need
    new_player_move_need = False    #hranimo, če smo že igrali playerja, da če smo moramo it ven in ga spet prasat za potezo
    global bet_amount_player
    bet_amount_player = bet_amount

    #zmešamo in razdelimo karte
    if label_player_cards["text"] == "PLAYER Cards:  X X":
        #nastavimo karte, premešamo karte
        random.shuffle(cards)
        global bot_node
        bot_node = get_bot_node(player_start)
        label_player_cards["text"] = "PLAYER Cards: " + num_to_card(cards[0]) + " " + num_to_card(cards[1]) if player_start else "Player cards: " + num_to_card(cards[2]) + " " + num_to_card(cards[3])

        #če ima prvo potezo bot, jo naredimo tukaj
        if player_start == False:
            # če prtisnemo na zacetku raise
            bet_amount_player = 0
            bet_amount = 0
            #naredimo potezo
            action, infoSet, pot_amount = bot_action(infoSet, pot_amount)  # vedno checkamo
            label_game_info["text"] = "Bot move action:" + action + "       pot_amount:" + str(pot_amount + 20) + "       bet_amount:" + str(bet_amount)
            print("Bot move infoset:", infoSet, "       pot_amount:", pot_amount, "                bet_amount:", bet_amount)
            print("Bot action: " + action)

        return True

    #smo v tem loopu, dokler player spet ne rabi kliknt gumba
    while(True):
        if(player_move):
            if new_player_move_need:    #če smo že enkrat igral z playerjom, potem mu mormo rect zdj za novo potezo
                new_player_move_need = False    # --> poenostavimo na default
                break
            infoSet, pot_amount = player_action(action, infoSet, pot_amount)
            print("Player move infoset:", infoSet, "       pot_amount:", pot_amount, "                bet_amount:", bet_amount)
            new_player_move_need = True
            print("Player action: ", action)
        else:
            #bot action = bot_action(action, amount, pot_amount) --> tuki pride v upostav naše strojno učenje
            action, infoSet, pot_amount = bot_action(infoSet, pot_amount)    # vedno callamo
            label_game_info["text"] = "Bot move action:" + action + "       pot_amount:" + str(pot_amount + 20) + "       bet_amount:" + str(bet_amount)
            print("Bot move infoset:", infoSet, "       pot_amount:", pot_amount, "                bet_amount:",
                  bet_amount)
            debug2 = infoSet
            print("Bot action: " + action)
        print("\n")


        #pogledamo če je smo že v terminal nodu in že izplačamo winningse
        winnings = payoff(infoSet, pot_amount)
        if winnings != "continue":
            payoff(infoSet, pot_amount)
            winnings_fun(winnings, infoSet, player_start)
            break;

        #določimo kdo bo naslednji na potezi
        player_move, infoSet = next_move_player(player_start, infoSet, player_move)

def new_game():
    global infoSet
    infoSet = ""
    global pot_amount
    pot_amount = 0
    global player_start
    player_start = not player_start # --> enkat začne bot, enkrat player

    label_bot_cards["text"] = "BOT Cards:  X X"
    label_player_cards["text"] = "PLAYER Cards:  X X"
    label_cards_table["text"] = ""
    label_game_info["text"] = "Game Info:   ante=10"










#-------------------------------------------------------------------------------------------

#RISANJE
root = tk.Tk()

canvas = tk.Canvas(root, height=HEIGHT, width=WIDTH)
canvas.pack()

background_label = tk.Label(root)
background_label.place(relwidth=1, relheight=1)

#FRAME TOP
top_frame = tk.Frame(root, bg='#80c1ff', bd=10)
top_frame.place(relx=0.5, rely=0.05, relwidth=0.75, relheight=0.1, anchor='n')

label_ply_stanje = tk.Label(top_frame, bg='#99ff99', font=40, text=("Stanje player: "+str(Player_stanje)))
label_ply_stanje.place(relx=0.05, relwidth=0.3, relheight=1)

label_bot_stanje = tk.Label(top_frame, bg='#99ff99', font=40, text=("Stanje bot: "+str(Bot_stanje)))
label_bot_stanje.place(relx=0.65, relwidth=0.3, relheight=1)


#FRAME MID
frame = tk.Frame(root, bg='#80c1ff', bd=10)
frame.place(relx=0.5, rely=0.2, relwidth=0.75, relheight=0.5, anchor='n')
label_mid = tk.Label(frame, bg='#99ff99')
label_mid.place(relwidth=1, relheight=1)

label_bot_cards = tk.Label(label_mid, font=40, bg='#ccffcc', text="BOT Cards:  X X")
label_bot_cards.place(relx=0.2, rely = 0.02, relwidth=0.6, relheight=0.12)

label_cards_table = tk.Label(label_mid, font=("Courier", 44), bg='#ccffcc')
label_cards_table.place(relx=0.1, rely = 0.19, relwidth=0.8, relheight=0.46)

label_player_cards = tk.Label(label_mid, font=40, bg='#ccffcc', text="PLAYER Cards:  X X")
label_player_cards.place(relx=0.2, rely = 0.7, relwidth=0.6, relheight=0.12)

label_game_info = tk.Label(label_mid, font=40, bg='#99c2ff', text="Game Info:   ante=10")
label_game_info.place(relx=0.05, rely = 0.85, relwidth=0.9, relheight=0.14)


#FRAME BOTTOM
lower_frame = tk.Frame(root, bg='#80c1ff', bd=5)
lower_frame.place(relx=0.5, rely=0.75, relwidth=0.75, relheight=0.1, anchor='n')

button_fold = tk.Button(lower_frame, text="Fold/Check", font=40, command=lambda: play("fold/check", 0))  # , command=lambda: get_weather(entry.get())
button_fold.place(relx=0.45, relheight=1, relwidth=0.15)

button_call = tk.Button(lower_frame, text="Call", font=40, command=lambda: play("call", 0))  # , command=lambda: get_weather(entry.get())
button_call.place(relx=0.65, relheight=1, relwidth=0.15)

entry = tk.Entry(lower_frame, font=40)
entry.place(relwidth=0.40, relheight=1)
button_raise = tk.Button(lower_frame, text="Raise", font=40, command=lambda: play("raise", int(entry.get())))  # , command=lambda: get_weather(entry.get())
button_raise.place(relx=0.85, relheight=1, relwidth=0.15)

#BOTTOM LABEL
button_fold = tk.Button(root, text="New Game", font=40, bg='#99c2ff', command=lambda: new_game())  # , command=lambda: get_weather(entry.get())
button_fold.place(relx=0.45, rely=0.87, relheight=0.05, relwidth=0.15)

root.mainloop()









"""
TODO:
    -nekje na screenu izpisuj : kaj je naredu bot, kolk denarja je v potu in na koncu povej kdo je zmagal in koliko je dobil

"""

