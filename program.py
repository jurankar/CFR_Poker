from random import random as randDec
import random
import time
import  cfr_poker

##GLOBAL VARIABLES


# --------------------------------------------------------------------------------------------------
# PLAYING POKER GAME


def stevilkaVKarto(st):

    switcher = {
        1: "J",
        2: "Q",
        3: "K",
        4: "A",
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
    cards = [1,1,1,1, 2,2,2,2, 3,3,3,3 ,4,4,4,4]
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
    learner = cfr_poker.Poker_Learner()
    learner.train(200000, 0)
    print("Čas izvajanja programa: ", (time.time() - start_time), " sekund. To je ", (time.time() - start_time)/60," minut.")

    # igranje igre
    #igrajIgro(learner)

"""
Zdaj razvijam osnovno obliko pokra s kartami 9-A, kjer bomo gledali samo High card, par, dva para, tris, full house,
poker.

1. verzija bo brez dreves, da bom nato videl razliko glede časa z drevesi. Prav tako bos lahko stavil samo
1 bet na potezo. 
Čas izvajanja s slovarjem aka. brez dreves za 1000000 iteracij: 5848.5 sekund --> 97.5 minut.....
porabil sem okoli 1.5-1.8 GB rama, kar je že mejilo na to koliko lahko računalnik sploh porabi(ker imam trenutno notri 8gb, kmalu bom dodal na 16gb)

2. verzija z drevesi(neoptimizirana), pravila ista kot v prejšnji
 po 10k iteracijah porabi 2.8gb rama in potem se sesuje in ne deluje vec ker zmanka rama
        -največ kar gre je 8k iteracij trenutno in za to porabi cca. 55 sekund.
        
3. verzija, popravljeni bugi iz prejsnje verzije.
    Ce damo v kupcek 5 različnih kart (skupaj 20) za 10k iteracij porabimo cca 2min 10s, kar je kr ok
    Na tej točki problem postane optimizacijski problem, ker trenutno nodi zasedejo prevec rama

"""

"""
TODO:
- Če smo v newStagu pol ne rabmo cekerat "pyouta" pa dobivat strategije (prvih cca. 20 vrstic v cfrju)  --> Done
- funkcijo betterCards zračuni na začetku ker jo zdj brez veze 200x racunas --> Done
- verjetno lahkot das velik node_init_p1 namest node, ker velik mn zasede --> pri newStage nodih je treba dat node_init_1 in pa zadnji nivo nodov je treba pobrisat
- Dopiš komentarje za profesorja --> KO TOLE USPOSOBŠ MU POŠL VERZIJO DA MAL KOMENTERA
- Handi k so bli mn igrani jih vec igrej
- Nared da se infoset nosi s sabo z rekurzijo (ker prek dreves itak ves), ne da ga mas shranenga v vsakem nodu posebej
- Ko nalozis node od p0 in node od p1, potem igraj kakih 1000 handov s kartami, ki jih ima p1 in p0 in potem zamenjaj
    ker s tem bos veliko manj casa porabil z nalaganjem in zapisovanjem nazaj






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