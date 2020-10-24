



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



if __name__ == "__main__":
    file_name = "datasets/dataset_demo.txt"
    f = open(file_name, "r")
    line = f.readline()

    # Attributs we are looking at
    num_of_played_hands = [0, 0]        # [ num_of_folded_hands, num_of_played_hands ] --> for every player in every game summed up
    all_in_games = 0               # Games where all in happened
    total_games_num = 0             # Number of all games

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


        else:
            # We read lines until we come to the next game
            line = f.readline()


    #Here we print the % of played hands
    played_hands = num_of_played_hands[1]
    total_hands = num_of_played_hands[0] + num_of_played_hands[1]
    print("Players played around ", (played_hands / total_hands)*100, "% of games.")
    print("Games with all in ", (all_in_games / total_games_num)*100, "% of games.")