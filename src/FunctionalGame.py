# TODO: if a player doesnt challenge a 3 bet, all players know what dice that player has. Relations can be updated!
# TODO: if a player doesnt challenge a 3 bet, the next player should be challenged
# TODO: append knowledge to list
# TODO: make more rounds

import numpy as np
from itertools import combinations_with_replacement
from itertools import product
import random


def wlist(players, dice, sides):
    worlds = []

    ineedthislist = []
    for i in range(sides):
        ineedthislist.append(i+1)

    # this one is for more than 2 sides
    # combis = list(set(list(combinations_with_replacement(ineedthislist,dice))))

    return list(product(ineedthislist, repeat=players))


def cmat(nworlds, players):
    thenumber = 0
    for i in range(players+1):
        thenumber += i*10**(players-i)
    return np.full((nworlds, nworlds), thenumber)


# If all quantities are -1, we challenge
def announceorchallenge(quantities, previousbid, dice, turn, sides):
    newdice = 0
    newbid = 0
    # Dice that the player in turn holds
    playersdice = dice[turn]
    # Bid is higher than the possible number according to the players dice
    if previousbid[1] != playersdice and previousbid[0] >= len(dice):
        print("Challenges because of impossible bid")
        for i,q in enumerate(quantities):
            quantities[i] = -1
            newdice = previousbid[1]
            newbid = previousbid[0]

    # Same dice 25/50/75 % chance of challenging
    elif previousbid[1] == playersdice:
        prob = random.randint(1, 100)
        if prob <= 100/(len(dice)+1)*previousbid[0]:
            print("Holds the same dice and challenges")
            for i, q in enumerate(quantities):
                quantities[i] = -1
            newdice = previousbid[1]
            newbid = previousbid[0]
        else:
            prob = random.randint(1, 100)
            # Update current number
            if prob <= 75:
                if previousbid[0]+1 > len(dice):
                    print(f"Holds the same dice and challenges because of impossible update")
                    for i, q in enumerate(quantities):
                        quantities[i] = -1
                    newdice = previousbid[1]
                    newbid = previousbid[0]
                else:
                    newbid = random.randint(previousbid[0]+1, len(dice))
                    quantities[previousbid[1]-1] = newbid
                    newdice = previousbid[1]
                    print(f"Holds the same dice and updates current dicenumber to {newbid}")
            # Update next number
            else:
                # If number is not on dice, challenge
                if previousbid[1]+1 > sides:
                    print(f"Holds the same dice and challenges because of impossible update from self")
                    for i, q in enumerate(quantities):
                        quantities[i] = -1
                    newdice = previousbid[1]
                    newbid = previousbid[0]
                # Update next dicenumber
                else:
                    newdice = random.randint(previousbid[1]+1, sides)
                    newbid = random.randint(1, len(dice)-1)
                    print(f"Holds the same dice and updates dice {newdice} to {newbid}")
                    quantities[newdice-1] = newbid
    # Has a different dice than the bid 50/75/100 %
    else:
        prob = random.randint(1, 100)
        if prob <= 100/(len(dice)+1)*(previousbid[0]):
            print("Holds different dice and challenges")
            for i, q in enumerate(quantities):
                quantities[i] = -1
            newdice = previousbid[1]
            newbid = previousbid[0]
        else:
            prob = random.randint(1, 100)
            # Update current number
            if prob <= 75:
                if previousbid[0]+1 > len(dice)-1:
                    print(f"Holds the same dice and challenges because of impossible update")
                    for i, q in enumerate(quantities):
                        quantities[i] = -1
                else:
                    newbid = random.randint(previousbid[0] + 1, len(dice)-1)
                    print(f"Holds different dice and updates current dicenumber to {newbid}")
                    quantities[previousbid[1]-1] = newbid
                    newdice = previousbid[1]
            else:
                # If number is not on dice, challenge
                if previousbid[1] + 1 > sides:
                    print(f"Holds different dice and challenges because of impossible update from self")
                    for i, q in enumerate(quantities):
                        quantities[i] = -1
                    newdice = previousbid[1]
                    newbid = previousbid[0]
                # Update next dicenumber
                else:
                    newbid = random.randint(1, len(dice))
                    newdice = random.randint(previousbid[1] + 1, sides)
                    print(f"Holds different dice and updates dice {newdice} to {newbid}")
                    quantities[newdice-1] = newbid
    return quantities, [newbid, newdice]


# Initialize worlds matrix
# only works for players <= 9
# only worlds for 1 dice per player
players = 3
dice = 1
sides = 2

worldlist = wlist(players, dice, sides)
connectmat = cmat(len(worldlist), players)
newconnectedmat = np.array(connectmat, copy=True)


# Let's play the game
# Roll the dice
dicecombi = []
for player in range(players):
    dicecombi.append(random.randint(1, sides))

print("Initial world list")
print(worldlist)
print("Dice:")
print(dicecombi)
# print("Connection matrix")
# print(connectmat)
# Players look at their dice and initial worlds get removed
width = connectmat.shape[0]
for i, dice in enumerate(dicecombi):
    for j, world in enumerate(worldlist):
        # if dice in index according to player does not have the value of the player.
        if world[i] != dice:
            # Update the rows
            for k, value in enumerate(newconnectedmat[j, :]):
                if value - (i+1)*(10**(players-1-i)) >= 0:
                    if len(str(value)) > len(str(value - (i+1)*(10**(players-1-i)))) and \
                        (value == 0 or str(value)[1] == str(value - (i+1)*(10**(players-1-i)))[0]):
                        newconnectedmat[j, k] -= (i+1)*(10**(players-1-i))
                    elif len(str(value)) > len(str(value - (i+1)*(10**(players-1-i)))) and not \
                        (value == 0 or str(value)[1] == str(value - (i+1)*(10**(players-1-i)))[0]):
                        pass
                    elif str(value - (i+1)*(10**(players-1-i)))[i - players + len(str(value))] == "0":
                        newconnectedmat[j, k] -= (i+1)*(10**(players-1-i))
            # Update the columns
            for k, value in enumerate(newconnectedmat[:,j]):
                if value - (i+1)*(10**(players-1-i)) >= 0:
                    if len(str(value)) > len(str(value - (i+1)*(10**(players-1-i)))) and \
                        (value == 0 or str(value)[1] == str(value - (i+1)*(10**(players-1-i)))[0]):
                        newconnectedmat[k,j] -= (i+1)*(10**(players-1-i))
                    elif len(str(value)) > len(str(value - (i+1)*(10**(players-1-i)))) and not \
                        (value == 0 or str(value)[1] == str(value - (i+1)*(10**(players-1-i)))[0]):
                        pass
                    elif str(value - (i+1)*(10**(players-1-i)))[i - players + len(str(value))] == "0":
                        newconnectedmat[k,j] -= (i+1)*(10**(players-1-i))
print("New connection matrix")
print(newconnectedmat)

print("First round")
challenged = 0
turn = 0
quantities = np.zeros(sides)
print(f"Initial quantities: {quantities}")
logiclines = []

#[Numberofdice, DiceNumber]
previousbid = [0, 1]
while not challenged:

    # Player who is in turn

    print(f"Player {turn} in turn")
    print(f"Previous bid is {previousbid}")
    # Action the player takes
    quantities, previousbid = announceorchallenge(quantities, previousbid, dicecombi, turn, sides)
    if sum(quantities) < 0:
        challenged = 1
        # See whether players loses dice or not
        totaldice = 0
        for d in dicecombi:
            if d == previousbid[1]:
                totaldice += 1
        if previousbid[0] > totaldice:
            print(f"Player {turn} successfully challenged, player {(turn-1)%3} loses a die")
        else:
            print(f"Player {turn} unsuccessfully challenged, player {turn} loses a die")
    else:
        logiclines.append(f"M{turn}({previousbid[0]}*{previousbid[1]})")
        print(f"New quantities: {quantities}")
        turn = (turn+1) % players
        print(logiclines)
print(logiclines)