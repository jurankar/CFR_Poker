# CFR_Poker
Implementation of poker machine learning algorithm.
The program is inspired by an algorithm named counterfactual regret minimization and you can read more about the 
algorithm on this link: http://modelai.gettysburg.edu/2013/cfr/cfr.pdf .
The paper is good for basic understanding of what the algorithm is doing, but for total understandig of my code you will have to take some time,
because I have evolved it a lot from the paper and the code has changed as well. The basic idea of the algorithm is the same.

The program simulates a lot of games and with time it learns. Over time it starts to understand to behave in certain situations. How to play when you know 
you have the best hand? When and how much to bluff?. In every game that the program plays, it simulates all possible outcomes of the game. After that it looks in which 
scenarios it did better and in which it did worse. In other words it sees which actions the program regrets more than others. In the future in the same situation it will than 
play actions, that performed better in the past, with greater probability(more often).



