



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

def pot_sum_fun(data, pot_sum):

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
            pot_sum[0][1] += total_preflop_pot + 1.5    # +1.5 because of Big and Small Blind
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



if __name__ == "__main__":
    file_name = "datasets/dataset_demo.txt"
    f = open(file_name, "r")
    line = f.readline()

    # Attributs we are looking at
    num_of_played_hands = [0, 0]        # [ num_of_folded_hands, num_of_played_hands ] --> for every player in every game summed up
    all_in_games = 0               # Games where all in happened
    total_games_num = 0             # Number of all games
    finished_games = 0              # Games where players in the end showed cards

    #Average pot size on preflop, flop, turn, river
    pot_sum = [[0, 0], [0, 0], [0, 0], [0, 0]]     # [[number_of_games, pot_sum], [],....]  :::: [[preflop], [flop],[turn],[river]]

    # We read the file until we come to an end
    while (line):

        # Players --> TODO
        # players = {}

        # We are at the beginning of a hand
        if ("Game ID:" in line) and (line.split()[3] == "0.50/1"):
            num_of_players = 0

            # First we skip data we dont need
            f.readline()  # Game ID: 808941103 0.50/1 (PRR) Karkadann (Short) (Hold'em)
            f.readline()  # Seat 9 is the button

            while f.readline().split()[0] == "Seat":     # Seat 1: Maria_Pia (40).
                num_of_players += 1

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

            #Number of played hands
            num_of_played_hands = num_of_played_hands_fun(data, num_of_played_hands, num_of_players)

            #Number of hands with allin
            if all_in_hands_fun(data):
                all_in_games += 1

            #Number of finished games
            if finished_game_fun(data):
                finished_games += 1

            #Average pot size on preflop, flop, turn, river
            pot_sum = pot_sum_fun(data, pot_sum)


        else:
            # We read lines until we come to the next game
            line = f.readline()


    #Here we print our findings
    played_hands = num_of_played_hands[1]
    total_hands = num_of_played_hands[0] + num_of_played_hands[1]
    print("Big blind: 1.0              Small blind: 0.50")
    print("Players played around: ", (played_hands / total_hands)*100, "% of games.")
    print("Games with allin: ", (all_in_games / total_games_num)*100, "% of games.")
    print("Finished games where players showed cards after river: ", (all_in_games / total_games_num)*100, "% of games.")

    print("\nAverage pot on preflop: ", pot_sum[0][1]/pot_sum[0][0])
    print("Average pot on flop: ", pot_sum[1][1]/pot_sum[1][0])
    print("Average pot on turn: ", pot_sum[2][1]/pot_sum[2][0])
    print("Average pot on river: ", pot_sum[3][1]/pot_sum[3][0])

    print("\n")