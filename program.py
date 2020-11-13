import time
import cfr_poker

##GLOBAL VARIABLES

## MAIN
if __name__ == "__main__":
    start_time = time.time()
    learner = cfr_poker.Poker_Learner()
    learner.train(100)
    print("Čas izvajanja programa: ", (time.time() - start_time), " sekund. To je ", (time.time() - start_time)/60," minut.")


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
- Ko nalozis node od p0 in node od p1, potem igraj kakih 1000 handov s kartami, ki jih ima p1 in p0 in potem zamenjaj
    ker s tem bos veliko manj casa porabil z nalaganjem in zapisovanjem nazaj
    
- dodj zacetne stave poleg anteja, aka. big/small blind

"""

"""
- Regret sum on the main node after:
    -100 games cca: 6000
    -200 games cca: 10000
    -300 games cca: 15000
    -400 games cca: 18500
    -500 games cca: 25000
    
- 

"""


"""
for image comparison: https://www.pyimagesearch.com/2014/09/15/python-compare-two-images/

"""