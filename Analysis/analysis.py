# -*- coding: utf-8 -*-
BIG_BLIND = 1.0
SMALL_BLIND = 0.50



def num_of_played_hands_fun(data, num_of_played_hands, num_of_players):
    ''' We check weather player folded hand pre-flop or not --> if he "played a hand"
        The we edit the "num_of_played_hands" variable '''

    for i in range(num_of_players):
        line = data[i]

        if "folds" in line:
            num_of_played_hands[0] += 1
        else:
            num_of_played_hands[1] += 1

        return num_of_played_hands

def all_in_hands_fun(data):
    """
    We check how many rounds had an all in
    """

    for i in data:
        if "allin" in i:
            return True

        # We came to the end of dataset
        if i == "------ Summary ------":
            return False

def finished_game_fun(data):
    """
    We check if the game came to an "end" meaning the players played to the river and showed cards
    """
    river = False
    for line in data:
        if line.split()[1] == "RIVER": #--> *** RIVER ***: [Kh 9s 8s 3s] [7h]
            river = True

        if line.split()[1] == "Summary":
            if not river:   # if we didnt come to river, game finished before showing the hand
                return False

        # Here we see if players showed the cards; 2 if conditions above this one are for optimization perpuses
        if river and ("shows" in line): # if the line contains word "shows", it means that players showed cards in the end --> *Player Portly23 shows: One pair of 9s [10c 9c]....
            return True

def raise_sum_fun(data, pot_sum):

    game_stage = 0 # 0:preflop, 1:flop, 2:turn, 3:river
    total_preflop_pot = 0
    total_flop_pot = 0
    total_turn_pot = 0
    total_river_pot = 0

    for line in data:

        split_line = line.split()
        # First we check if we move to another stage: preflop -> flop; flop -> turn;...
        # The reason we add pot_sum when the stage (flop, river,...) ends is that we get better and more accurate data
        if split_line[1] == "FLOP":
            pot_sum[0][0] += 1
            pot_sum[0][1] += total_preflop_pot + (BIG_BLIND + SMALL_BLIND)    # +1.5 because of Big and Small Blind
            game_stage += 1

        elif split_line[1] == "TURN":
            pot_sum[1][0] += 1
            pot_sum[1][1] += total_flop_pot
            game_stage += 1

        elif split_line[1] == "RIVER":
            pot_sum[2][0] += 1
            pot_sum[2][1] += total_turn_pot
            game_stage += 1

        elif "shows" in line:
            pot_sum[3][0] += 1
            pot_sum[3][1] += total_river_pot
            return pot_sum

        else:

            # We assign bets to according gamestages
            if line[-1] == ')': # "raises (4.0)", "calls (2.5)"
                bet_amount = split_line[-1]
                bet_amount_float = float(bet_amount[1:-1])   # we remove "()"
                if game_stage == 0: total_preflop_pot += bet_amount_float
                elif game_stage == 1: total_flop_pot += bet_amount_float
                elif game_stage == 2: total_turn_pot += bet_amount_float
                elif game_stage == 3: total_river_pot += bet_amount_float
                else: return "error 1"

    return pot_sum

def raise_increase_percentage_fun(data, raise_increase_percentage):

    current_pot = BIG_BLIND + SMALL_BLIND
    for line in data:
        line_split = line.split()

        if line[-1] == ')': # If anybody raises or calls
            bet_amount = line_split[-1]
            bet_amount_float = float(bet_amount[1:-1])

            if line_split[-2] == "raises" or line_split[-2] == "bets":  # If anybody raises
                raise_increase_percentage[0] += 1
                raise_increase_percentage[1] += (bet_amount_float/current_pot) * 100     # How many % did we raise relative to the pot

            current_pot += bet_amount_float

    return raise_increase_percentage

def reraise_percentage_fun(data, reraise_percentage):

    first_raise = True  # We set this to FALSE, when we have bet for the first time in one stage (flop, turn,...). Second time it is a reraise. At the beginning of each stage we reset to TRUE
    for line in data:
        line_split = line.split()

        if line_split[1] == "FLOP" or line_split[1] == "TURN" or line_split[1] == "RIVER":
            first_raise = True
        else:
            if line_split[-2] == "raises" or line_split[-2] == "bets":  # If anybody raises
                if not first_raise:
                    reraise_percentage[1] += 1
                else:
                    first_raise = False

                reraise_percentage[0] += 1

    return reraise_percentage


if __name__ == "__main__":
    file_name = "Humans/datasets/dataset.txt"
    f = open(file_name, "r")
    line = f.readline()

    # Attributs we are looking at
    num_of_played_hands = [0, 0]        # [ num_of_folded_hands, num_of_played_hands ] --> for every player in every game summed up
    all_in_games = 0               # Games where all in happened
    total_games_num = 0             # Number of all games
    finished_games = 0              # Games where players in the end showed cards
    player_stack_size = [0, 0]      # [ num_of_all_players, sum_of_stack_sizes ]

    #Average pot size on preflop, flop, turn, river
    raise_sum = [[0, 0], [0, 0], [0, 0], [0, 0]]     # [[number_of_games, pot_sum], [],....]  :::: [[preflop], [flop],[turn],[river]]

    #Average raise sum
    raise_increase_percentage = [0, 0]                  # [number of raises, raise_percenage_sum ]

    #How many of the raises are reraises
    reraise_percentage = [0, 0]                         # [ number of raises, number of reraises ]

    # DEBUGING
    #counter = 0

    # We read the file until we come to an end
    while (line):

        """
        #DEBUGING
        counter += 1
        if counter%1000 == 0:
            print(counter/1000)
        """

        # We are at the beginning of a hand
        if ("Game ID:" in line) and (line.split()[3] == "0.50/1" or line.split()[3] == "0.5/1.0"):
            num_of_players = 0
            stack_size_sum = 0

            f.readline()    # --> skip "player x is the button"
            line = f.readline().split()
            while line[0] == "Seat":     # Seat 1: Maria_Pia (40).
                bet_amount = line[-1]
                bet_amount_float = float(bet_amount[1:-2])

                num_of_players += 1
                stack_size_sum += bet_amount_float
                line = f.readline().split()

            f.readline() # Player RunnerLucker has big blind (1)

            line = f.readline()
            while "received" in line:
                line = f.readline()

            # Collect useful data
            data = []
            while(line.split()[1] != "ended"):
                data.append(line[:-1])
                line = f.readline()

            # ANALYSIS
            total_games_num += 1

            # For average player stack
            player_stack_size[0] += num_of_players
            player_stack_size[1] += stack_size_sum

            #Number of played hands
            num_of_played_hands = num_of_played_hands_fun(data, num_of_played_hands, num_of_players)

            #Number of hands with allin
            if all_in_hands_fun(data):
                all_in_games += 1

            #Number of finished games
            if finished_game_fun(data):
                finished_games += 1

            #Average pot size on preflop, flop, turn, river
            raise_sum = raise_sum_fun(data, raise_sum)

            # What % of raises are reraises
            reraise_percentage = reraise_percentage_fun(data, reraise_percentage)

            #Average bet/raise increase in % (by how much do players raise)
            raise_increase_percentage = raise_increase_percentage_fun(data, raise_increase_percentage)

            #TODO
            #Defending blinds?




        else:
            # We read lines until we come to the next game
            line = f.readline()


    #Here we print our findings
    played_hands = num_of_played_hands[1]
    total_hands = num_of_played_hands[0] + num_of_played_hands[1]
    print("Big blind: ", BIG_BLIND,"              Small blind: ", SMALL_BLIND)

    print("\nTotal number of games: ", total_games_num)
    print("Average player stack/balance: ", player_stack_size[1]/player_stack_size[0], "which is equal to ", (player_stack_size[1]/player_stack_size[0])/BIG_BLIND, " big blinds")
    print("Players played: ", (played_hands / total_hands)*100, "% of games.")

    print("\nGames with allin: ", (all_in_games / total_games_num)*100, "% of games.")
    print("Finished games where players showed cards after river: ", (finished_games / total_games_num)*100, "% of games.")

    print("\nAverage betting sum on preflop: ", raise_sum[0][1]/raise_sum[0][0])    # Betting sum means total money put on the tabel (calls + raises)
    print("Average betting sum on flop: ", raise_sum[1][1]/raise_sum[1][0])
    print("Average betting sum on turn: ", raise_sum[2][1]/raise_sum[2][0])
    print("Average betting sum on river: ", raise_sum[3][1]/raise_sum[3][0])

    print("\nWhat % of raises are reraises: ", (reraise_percentage[1]/reraise_percentage[0])*100, " %" )
    print("Average raise increase in percentages: ",  raise_increase_percentage[1]/raise_increase_percentage[0], "%")





"""
INFO:
    -0.10/0.25 --> 12796 iger
    -0.25/0.50 --> 16395 iger    
    -0.50/1    --> 9977 iger




TODO:
- Add big blind? da ves kolk % handov igra bot?....p0 ima BB, p1 vedno potem ima potezo

"""