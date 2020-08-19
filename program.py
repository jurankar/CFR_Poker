from random import random as randDec
import random
import time
import cfr_poker
import nodes
##GLOBAL VARIABLES

#DEBUGGING
import os
import psutil


# --------------------------------------------------------------------------------------------------
# PLAYING POKER GAME


def stevilkaVKarto(st):

    switcher = {
        1: "9",
        2: "10",
        3: "J",
        4: "Q",
        5: "K",
        6: "A"
    }

    return (switcher.get(st, "Error ni te karte"))

def game_payoff(learner, stanjePlayer, botInfoSet, cards):
    payoff = learner.payoff(botInfoSet)
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


def poVrsti(cards):
    cards.sort()
    cards_string = ""
    for i in range (len(cards)):
        cards_string += str(cards[i])

    return cards_string

def igrajIgro(learner): # --> TO DO ne dela ok
    cards = [1,1,1,1, 2,2,2,2, 3,3,3,3, 4,4,4,4, 5,5,5,5, 6,6,6,6]
    input_word = "hec"

    stanjePlayer = 30

    print("\n\n\nmozne karte so od 9 do As")
    print("če želiš zaključiti igro vpiši besedo end\n\n")
    while input_word != "end":
        print("\n")
        random.shuffle(cards)
        moji_karti_str = stevilkaVKarto(cards[0]) + "," + stevilkaVKarto(cards[1])
        bot_karti_str = stevilkaVKarto(cards[2]) + "," + stevilkaVKarto(cards[3])
        botNode = learner.nodeMap_p1[poVrsti([cards[2], cards[3]])];

        print("\n\ntvoji karti sta: ", moji_karti_str)
        karte_na_mizi = ""
        for i in range(4):  #preflop, flop, turn, river
            print("\n")

            if i != 0:
                print("Na mizi so karte: ", karte_na_mizi, "      Tvoji karti sta: ", moji_karti_str)

            print("če želiš staviti napiši b, če pa želiš checkati pa vpiši p")
            actionPlayer = input("Vnesi: ")

            #zdj določm še za bota action
            botNode = botNode.betting_map[actionPlayer]

            if botNode.strategySum[0] == 0 and botNode.strategySum[1] == 0:
                print ("\nnew node --> ", botNode.infoSet + "\n")   # --> debugging

            # določimo kaj bo naredil bot
            strat = botNode.getAvgStrat()
            if(randDec() > strat[0]):
                actionBot = "b"
                print("Bot se odločil za bet   oz. B")
            else:
                actionBot = "p"
                print("Bot se odločil za pass  oz.  P")
            botNode = botNode.betting_map[actionBot]
            stanjePlayer, end_round = game_payoff(learner, stanjePlayer, botNode.infoSet, cards)
            if end_round: break

            if actionPlayer == "p" and actionBot == "b":
                print("če želiš izenačiti napiši b, če pa želiš foldati pa vpiši p")
                actionPlayer = input("Vnesi: ")
                botNode = botNode.betting_map[actionPlayer]

            if i == 0:
                new_cards = learner.poVrsti([cards[4], cards[5], cards[6]])
                karte_na_mizi += stevilkaVKarto(cards[4]) + "," + stevilkaVKarto(cards[5]) + "," + stevilkaVKarto(cards[6])
                if ("f" + new_cards) in botNode.new_cards:
                    botNode = botNode.new_cards["f" + new_cards]
                else:
                    print("missing node on flop --> ni bilo dovolj učenja zato se ta node še ni kreiral")
                    print("Sedaj bomo začeli novo rundo")
                    break;
            elif i == 1:
                new_cards = str(cards[7])
                karte_na_mizi += "," + stevilkaVKarto(cards[7])
                if ("t" + new_cards) in botNode.new_cards:
                    botNode = botNode.new_cards["t" + new_cards]
                else:
                    print("missing node on turn --> ni bilo dovolj učenja zato se ta node še ni kreiral")
                    print("Sedaj bomo začeli novo rundo")
                    break;
            elif i == 2:
                new_cards = str(cards[8])
                karte_na_mizi += "," + stevilkaVKarto(cards[8])
                if ("r" + new_cards) in botNode.new_cards:
                    botNode = botNode.new_cards["r" + new_cards]
                else:
                    print("missing node on river --> ni bilo dovolj učenja zato se ta node še ni kreiral")
                    print("Sedaj bomo začeli novo rundo")
                    break;

            stanjePlayer, end_round = game_payoff(learner, stanjePlayer, botNode.infoSet, cards)
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
    start_time = time.time()
    learner = cfr_poker.Poker_Learner()
    learner.train(10000, 10000)
    print("Čas izvajanja programa: ", (time.time() - start_time), " sekund. To je ", (time.time() - start_time)/60," minut.")


    # igranje igre
    # igrajIgro(learner)

"""
Zdaj razvijam osnovno obliko pokra s kartami 9-A, kjer bomo gledali samo High card, par, dva para, tris, full house,
poker.

1. verzija bo brez dreves, da bom nato videl razliko glede časa z drevesi. Prav tako bos lahko stavil samo
1 bet na potezo. +
Čas izvajanja s slovarjem aka. brez dreves za 1000000 iteracij: 5848.5 sekund --> 97.5 minut.....
porabil sem okoli 1.5-1.8 GB rama, kar je že mejilo na to koliko lahko računalnik sploh porabi(ker imam trenutno notri 8gb, kmalu bom dodal na 16gb)

2. verzija z drevesi(neoptimizirana), pravila ista kot v prejšnji
 po 10k iteracijah porabi 2.8gb rama in potem se sesuje in ne deluje vec ker zmanka rama
        -največ kar gre je 8k iteracij trenutno in za to porabi cca. 55 sekund.
        
3. verzija, popravljeni bugi iz prejsnje verzije.
    Ce damo v kupcek 5 različnih kart (skupaj 20) zac 10k iteracij porabimo cca 10min, kar je kr ok
    Na tej točki problem postane optimizacijski problem, ker trenutno nodi zasedejo cisto prevec rama

4. verzija, optimizirana dreves
    Trenutno porabimo za 10k iteracij 1 minuto, s tem da na zacetku porabljamo veliko rama in časa ker se 
    ustvarjajo nodi, ampak po tem pa program začne delovati precej hitreje(cca 1x hitreje kot na začetku) in 
    porablja manj rama(ker je večina nodov že narejenih in samo popravlja verjetnosti), tako da je  
    časovna zahtevnost glede na št iteracij O(log n) (se mi zdi)
    
5. VERZIJA PRED/PO SLOTIH: drevesa bolje optimizirana, uporabljamo 3 tipe stav; 0, 1/2pota, pot...in pa 4 karte(J,Q,K,A)
    ko zaženemo za 10 000 iteracij:
        -z sloti: 3500 MB RAMa, 6.9 minut
        -brez slotov: 4500 MB RAMa, 7.1 minut

6. Zapisovanje stanj na disk:
    3 možne stave:
        Laptop:
        -če delamo za vsak hand 100 iteracij, potem load/dump porabita 36% časa
        -če delamo za vsak hand 1000 iteracij, potem load/dump porabita 6.3% časa
        Kišta:
        -če delamo za vsak hand 10 iteracij, potem load/dump porabita 85% časa  (za 1000,10 porabimo 235 minut v profile program)
        -če delamo za vsak hand 100 iteracij, potem load/dump porabita 70% časa  (za 100,100 porabimo 60 minut v profile program)
        -če delamo za vsak hand 1000 iteracij, potem load/dump porabita 42% časa (za 10, 1000 porabimo 25 minut v profile program)    --> OPTIMALNO
        -če delamo za vsak hand 5000 iteracij, potem nam zmanjka rama in se stvari začnejo shranjevati na disk, kar je pa totalno prepočasno
    2 možne stave:
        Kišta:
        Ko oddigraš cca. 1,5 mio handov si na okoli 10,9GB RAMa in tam se ustavi
        -za 100,1000 porabimo 40 minut v profile program, load/dump 
        -za 10, 10000 12 minut v profile program, load/dump 

"""

"""
TODO:
- verjetno lahkot das velik node_betting_map namest node, ker velik mn zasede --> DONE
- Handi k so bli mn igrani jih vec igrej
- Nared da se infoset nosi s sabo z rekurzijo (ker prek dreves itak ves), ne da ga mas shranenga v vsakem nodu posebej
- Ko nalozis node od p0 in node od p1, potem igraj kakih 1000 handov s kartami, ki jih ima p1 in p0 in potem zamenjaj
    ker s tem bos veliko manj casa porabil z nalaganjem in zapisovanjem nazaj
- Cleaning


- optimizacija: 
    -ce je drevo v zadnjem nodu, ne rabis it se v en node samo za payoff --> optimiziraj da ne bo treba it do zadnjega nivoja(ki je tudi največji nivo) --> DONE
    -probi se znebit infoseta --> zavzema velik časa in rama
- dodj zacetne stave poleg anteja, aka. big/small blind
- dodeli igro 
    --> dodaj vse karte notr od 2 do A
    --> pol dodeli funkcijo self.betterCards (dodj lestvice, flushe)
    --> večji razpon stavljenja, ker treunto lahko samo staviš 1 ali passaš --> DONE
- preber navodila kako je s kickerjom 
    - vzem top 5 kart in poglej prvo k se razlikuje (zmaga tisti, k ma večjo)
    - če je vseh pet istih, pol splitaš

- dopoln "igrajIgro(learner)" da enkrat začne player enkat bot
    - Sedaj vedno začne player

- skupi dj nizje karte v node, recimo 2 in 3, 4 in 5, 6 in 7, 8 in 9 --> s tem bi mogu dost dobit da bo optimalno delal


"""