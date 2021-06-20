import random

def randombid(previous_bid, dicenum, players, personalbeliefs, quantities, players_dice, turn, sides):
    # bid higher
    prob = random.randint(1, 100)
    if prob < 50:
        # Bid would be too high for current number of dice in game
        if previous_bid[0] + 1 > dicenum * len(players) - personalbeliefs[turn][previous_bid[1] - 1]:
            print(f"Challenging because updating pips causes inconsistency")
            for i, q in enumerate(quantities):
                quantities[i] = -1
            new_dice = previous_bid[1]
            new_bid = previous_bid[0]
        # Up number of pips
        else:
            new_bid = random.randint(previous_bid[0] + 1,
                                     dicenum * len(players) -
                                     int(sum(personalbeliefs[turn])) +
                                     int(personalbeliefs[turn][previous_bid[1] - 1]))
            quantities[previous_bid[1] - 1] = new_bid
            new_dice = previous_bid[1]
            personalbeliefs[turn][previous_bid[1] - 1] = new_bid
            print(f"Updates current dice number to {new_bid}")
    # update number
    else:
        # Sides too big, challenge
        if previous_bid[1] + 1 > sides:
            print("Updating pips causes inconsistency, challenges bid instead")
            for i, q in enumerate(quantities):
                quantities[i] = -1
            new_dice = previous_bid[1]
            new_bid = previous_bid[0]
        else:

            new_dice = random.randint(previous_bid[1] + 1, sides)
            new_bid = random.randint(personalbeliefs[turn][new_dice - 1],
                                     len(players) * dicenum - sum(players_dice != new_dice))
            quantities[new_dice - 1] = new_bid
            personalbeliefs[turn][previous_bid[1] - 1] = new_bid
            print(f"Updates dice number {previous_bid[1]} to {new_dice}")
            print(f"Updates number of dice to {new_bid}")
    return quantities, personalbeliefs, new_dice, new_bid


def minbid(previous_bid, dicenum, players, personalbeliefs, quantities, players_dice, turn, sides):
    # bid higher
        # Bid would be too high for current number of dice in game
    if previous_bid[0] + 1 > dicenum * len(players) - personalbeliefs[turn][previous_bid[1] - 1]:
        # Cant bid further
        if previous_bid[1] + 1 > sides:
            print("Updating pips causes inconsistency, challenges bid instead")
            for i, q in enumerate(quantities):
                quantities[i] = -1
            new_dice = previous_bid[1]
            new_bid = previous_bid[0]
        else:
            new_dice = previous_bid[1] + 1
            new_bid = 1
            quantities[new_dice - 1] = new_bid
            personalbeliefs[turn][previous_bid[1] - 1] = new_bid
            print(f"Updates dice number {previous_bid[1]} to {new_dice}")
            print(f"Updates number of dice to {new_bid}")
    else:
        new_bid = previous_bid[0] + 1
        quantities[previous_bid[1] - 1] = new_bid
        new_dice = previous_bid[1]
        personalbeliefs[turn][previous_bid[1] - 1] = new_bid
        print(f"Updates current dice number to {new_bid}")

    return quantities, personalbeliefs, new_dice, new_bid


def aggrobid(previous_bid, dicenum, players, personalbeliefs, quantities, players_dice, turn, sides):
    # bid higher
    # Bid would be too high for current number of dice in game
    if previous_bid[1] + 1 > sides:
        print("Updating pips causes inconsistency, challenges bid instead")
        for i, q in enumerate(quantities):
            quantities[i] = -1
        new_dice = previous_bid[1]
        new_bid = previous_bid[0]
        # Cant bid further

    else:
        new_dice = random.randint(previous_bid[1] + 1, sides)
        new_bid = random.randint(personalbeliefs[turn][new_dice - 1],
                                 len(players) * dicenum - sum(players_dice != new_dice))
        quantities[new_dice - 1] = new_bid
        personalbeliefs[turn][previous_bid[1] - 1] = new_bid
        print(f"Updates dice number {previous_bid[1]} to {new_dice}")
        print(f"Updates number of dice to {new_bid}")

    return quantities, personalbeliefs, new_dice, new_bid

