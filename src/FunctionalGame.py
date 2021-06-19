import itertools
import math
import numpy as np
from itertools import product
import random
import copy


class FunctionalGame:
    def __init__(self, players, dice, sides, sid=None):
        self.sid = sid
        self.sides = sides
        self.players = generateplayerslist(players)
        self.losingplayers = []
        self.playershistory = []
        newplist = copy.copy(self.players)
        self.playershistory.append(newplist)
        self.dice = dice
        self.dicehistory = []

        self.logic_beliefs = None
        self.logic_beliefsround = None
        self.logic_beliefshistory = []
        self.logic_commonknowledge = None
        self.logic_commonknowledgeround = None
        self.logic_commonknowledgehistory = []

        self.personalbeliefs = None
        self.world_list = None
        self.connection_mat = None

        # Contains all connections in 1 round
        self.allconnection_mat = None
        self.connection_matround = None
        self.connection_mathistory = []

        self.dice_combos = None

    def playround(self):
        self.connection_matround = []

        # Initialize structures that keep track of knowledge
        self.logic_beliefs = []
        self.logic_beliefsround = []

        self.logic_commonknowledge = commonknowledge(self.sides)
        self.logic_commonknowledgeround = []

        self.personalbeliefs = personalbeliefs(self.players, self.sides)

        # Make initial world list and connection matrix for round
        self.world_list = get_world_list(self.players, self.dice, self.sides)
        self.connection_mat = get_connection_mat(len(self.world_list), len(self.players))

        # Append initial states to lists that keep track of round states
        self.logic_beliefs = generatebelieflines(self.personalbeliefs)
        tempbeliefs = copy.copy(self.logic_beliefs)
        tempcommonknowledge = copy.copy(self.logic_commonknowledge)
        tempconmat = copy.copy(self.connection_mat)
        self.logic_beliefsround.append(tempbeliefs)
        self.logic_commonknowledgeround.append(tempcommonknowledge)
        self.connection_matround.append(tempconmat)

        print("Initial world list")
        print(self.world_list)
        print("Initial Connection matrix")
        print(self.connection_mat)

        # Let's play the game
        # Roll the dice and append to history
        self.dice_combos = roll_dice(self.players, self.sides, self.dice)
        tempdicecombos = copy.copy(self.dice_combos)
        self.dicehistory.append(tempdicecombos)
        print("Dice:")
        print(self.dice_combos)

        # Players look at their dice and initial worlds get removed
        self.connection_mat, self.personalbeliefs = look_at_dice(self.dice_combos,
                                                                     self.players,
                                                                     self.connection_mat,
                                                                     self.world_list,
                                                                     self.sides,
                                                                     self.personalbeliefs)

        # Append states after looking at dice to lists that keep track of round states
        self.logic_beliefs = generatebelieflines(self.personalbeliefs)
        tempbeliefs = copy.copy(self.logic_beliefs)
        tempcommonknowledge = copy.copy(self.logic_commonknowledge)
        tempconmat = copy.copy(self.connection_mat)
        self.logic_beliefsround.append(tempbeliefs)
        self.logic_commonknowledgeround.append(tempcommonknowledge)
        self.connection_matround.append(tempconmat)

        print("New connection matrix")
        print(self.connection_mat)
        # Runs first round so without players losing a die
        self.bidding()

        # Append all round history to global history
        temproundcknowledge = copy.copy(self.logic_commonknowledgeround)
        temproundbelief = copy.copy(self.logic_beliefsround)
        temproundconmat = copy.copy(self.connection_matround)
        self.logic_commonknowledgehistory.append(temproundcknowledge)
        self.logic_beliefshistory.append(temproundbelief)
        self.connection_mathistory.append(temproundconmat)

    def bidding(self):
        challenged = 0
        turn = 0
        quantities = np.zeros(self.sides)
        print(f"Initial quantities: {quantities}")
        self.logic_beliefs = []

        # [Number_of_dice, DiceNumber]
        previous_bid = [0, 1]
        while not challenged:

            # Player who is in turn
            print(f"Player {turn} in turn")
            print(f"Previous bid is {previous_bid}")

            # Action the player takes
            bid_before = copy.copy(previous_bid)
            quantities, previous_bid, self.personalbeliefs= announce_or_challenge(quantities, previous_bid,
                                                                             self.dice_combos, turn, self.sides,
                                                                             self.players, self.dice,
                                                                             self.personalbeliefs)

            # Challenged
            if sum(quantities) < 0:
                challenged = 1
                # See whether players loses dice or not
                total_dice = 0
                for pdice in self.dice_combos:
                    for eachdice in pdice:
                        if eachdice == previous_bid[1]:
                            total_dice += 1
                if previous_bid[0] > total_dice:
                    playerwon = self.players[turn]
                    playerlost = self.players[turn - 1 % len(self.players)]
                    self.losingplayers.append(playerlost)
                    print(f"Player {self.players[turn]} successfully challenged, player "
                          f"{self.players[turn - 1 % len(self.players)] } loses a die")
                    del self.players[turn - 1 % len(self.players)]
                else:
                    playerwon = self.players[turn - 1 % len(self.players)]
                    playerlost = self.players[turn]
                    self.losingplayers.append(playerlost)
                    print(f"Player {self.players[turn]} unsuccessfully challenged, player "
                          f"{self.players[turn - 1 % len(self.players)] } loses a die")
                    del self.players[turn]
                newplist = copy.copy(self.players)
                self.playershistory.append(newplist)
            # Not challenged, we update connection matrix and logic lines
            else:
                self.connection_mat, self.personalbeliefs,self.logic_commonknowledge = update_connection_mat(
                                                                                    self.connection_mat,
                                                                                    previous_bid,
                                                                                    bid_before,
                                                                                    turn,
                                                                                    self.players,
                                                                                    self.world_list, self.dice,
                                                                                    self.logic_commonknowledge,
                                                                                    self.personalbeliefs,
                                                                                    self.dice_combos)

                # Append logic and connection matrices after every bidding round
                self.logic_beliefs = generatebelieflines(self.personalbeliefs)
                tempbeliefs = copy.copy(self.logic_beliefs)
                tempcommonknowledge = copy.copy(self.logic_commonknowledge)
                tempconmat = copy.copy(self.connection_mat)
                self.logic_beliefsround.append(tempbeliefs)
                self.logic_commonknowledgeround.append(tempcommonknowledge)
                self.connection_matround.append(tempconmat)

                print(f"New quantities: {quantities}")
                turn = (turn + 1) % len(self.players)


def generateplayerslist(players):
    return [x for x in range(players)]


def generatebelieflines(beliefs):
    lines = []
    for i, row in enumerate(beliefs):
        for j, col in enumerate(row):
            lines.append(f"M_{i} >= {int(col)}*{j+1}")

    return lines


# Initiates personal beliefs (how many dice there are at minimum)
def personalbeliefs(players, sides):
    return np.zeros([len(players), sides])


def commonknowledge(sides):
    return np.zeros(sides)


# Players roll their dice, list of lists containing dice per player is returned
def roll_dice(players, sides, dice):
    dice_combos = []
    for _ in players:
        dice_combos.append([random.randint(1, sides) for x in range(dice)])
    return dice_combos


# Returns histogram of dice
def count(dicelist, sides):
    counts = np.zeros(sides)
    for dice in dicelist:
        counts[dice - 1] += 1

    return counts


# Player look at their dice and connections disappear
def look_at_dice(dice_combos, players, connection_mat, world_list, sides, personalbeliefs):
    new_mat = connection_mat.copy()
    # Update personal beliefs
    for k, player in enumerate(players):
        pdice = dice_combos[k]
        for d in pdice:
            personalbeliefs[k][d - 1] += 1
    # Iterate over every connection between worlds
    for i, row in enumerate(new_mat):
        for j, colval in enumerate(row):
            # Check for every player whether all their dice are in both worlds
            for l, player in enumerate(players):
                dice = dice_combos[l]
                dicecounts = count(dice, sides)
                horworldcounts = count(world_list[i], sides)
                vertworldcounts = count(world_list[j], sides)
                hordiff = horworldcounts - dicecounts
                vertdiff = vertworldcounts - dicecounts
                for k in range(len(dicecounts)):
                    if (hordiff[k] < 0 or vertdiff[k] < 0) and f"{l + 1}" in str(new_mat[i, j]):
                        new_mat[i, j] -= (l + 1) * 10 ** (len(players) - l - 1)

    return new_mat, personalbeliefs


def get_world_list(players, dice, sides):
    worlds = []
    sidelist = [x + 1 for x in range(sides)]
    for val in itertools.product(*[sidelist] * (len(players) * dice)):
        sorted = list(val)
        sorted.sort()
        worlds.append(sorted)
    checked = []
    for world in worlds:
        if world not in checked:
            checked.append(world)
    return checked


def get_connection_mat(n_worlds, players):
    the_number = 0
    for i in range(players + 1):
        the_number += i * 10 ** (players - i)
    return np.full((n_worlds, n_worlds), the_number)


# If all quantities are -1, we challenge
def announce_or_challenge(quantities, previous_bid, dice, turn, sides, players, dicenum, personalbeliefs):
    new_dice = 0
    new_bid = 0
    # Dice that the player in turn holds
    players_dice = np.array(dice[turn])
    # Bid is higher than the belief allow
    if 0 > len(players) * dicenum - sum(personalbeliefs[turn]) + personalbeliefs[turn][previous_bid[1]-1]- previous_bid[0]:
        print("Challenges because of too high number of dice according to players belief")
        for i, q in enumerate(quantities):
            quantities[i] = -1
        new_dice = previous_bid[1]
        new_bid = previous_bid[0]

    else:
        prob = random.uniform(0, 1)
        # Challenge
        # probability (number of dice of prev bid - number of dice the player holds of that bid)/
        #               (total # of dice - dice the player holds)
        # To pick indicates how many dice need to be the same number as the bid in order to satisfy beliefs
        topick = previous_bid[0] - personalbeliefs[turn][previous_bid[1]-1]  # k
        diceleft = dicenum * (len(players) - 1)  # x/n
        thesum = 0
        if topick > 0:
            if previous_bid[0] != 0:
                # Probability of throwing at least x n's
                for x in range(int(topick), diceleft + 1):
                    thesum += math.factorial(diceleft) / (math.factorial(x) * math.factorial(diceleft - x)) * \
                              ((1 / sides) ** x) * ((1 - 1 / sides) ** (diceleft - x))
        else:
            thesum = -1
        if prob <= thesum:
            print("Challenges because of belief its not true")
            for i, q in enumerate(quantities):
                quantities[i] = -1
            new_dice = previous_bid[1]
            new_bid = previous_bid[0]
        # Does belief its true, now make a bid themselves
        else:
            prob = random.randint(1, 100)
            # 50/50 of bidding higher or bidding next number

            # bid higher
            if prob < 50:
                # Bid would be too high for current number of dice in game
                if previous_bid[0] + 1 > dicenum * len(players) - personalbeliefs[turn][previous_bid[1]-1]:
                    print(f"Challenging because updating pips causes inconsistency")
                    for i, q in enumerate(quantities):
                        quantities[i] = -1
                    new_dice = previous_bid[1]
                    new_bid = previous_bid[0]
                # Up number of pips
                else:
                    new_bid = random.randint(previous_bid[0] + 1,
                                             dicenum * len(players) - sum(players_dice == previous_bid[1]))
                    quantities[previous_bid[1] - 1] = new_bid
                    new_dice = previous_bid[1]
                    personalbeliefs[turn][previous_bid[1]-1] = new_bid
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
                    new_bid = random.randint(1, len(players) * dicenum - sum(players_dice != new_dice))
                    quantities[new_dice - 1] = new_bid
                    personalbeliefs[turn][previous_bid[1]-1] = new_bid
                    print(f"Updates dice number {previous_bid[1]} to {new_dice}")
                    print(f"Updates number of dice to {new_bid}")

    return quantities, [new_bid, new_dice], personalbeliefs


def update_connection_mat(connection_mat, previous_bid, bid_before, turn, players, world_list, dice, cknowledge,
                          personalbeliefs, dicecombos):
    new_connection_mat = connection_mat.copy()
    # Player has this dice because he called more dice than possible for the rest
    # Everybody now knows that worlds with less dice than that are impossible
    # The next player has not challenged, meaning he also has those dice.
    if previous_bid[0] > dice * (len(players) - 1):
        excessivedice = previous_bid[0] - dice * (len(players) - 1)
        cknowledge[previous_bid[1]-1] = excessivedice
        dice_number = previous_bid[1]

        # Update personal belief matrix
        for k, player in enumerate(players):
            if k != turn and personalbeliefs[k][dice_number - 1] <\
                    excessivedice + sum(np.array(dicecombos[k]) == previous_bid[1]):
                personalbeliefs[k][dice_number - 1] = excessivedice + sum(np.array(dicecombos[k]) == previous_bid[1])
        for i, row in enumerate(new_connection_mat):
            for j, value in enumerate(row):
                # Remove connections where # of dice <= number of dice the other player has for sure
                for l, player in enumerate(players):
                    if ((sum(np.array(world_list[i]) == previous_bid[1])) < personalbeliefs[l][dice_number - 1] or
                        (sum(np.array(world_list[j]) == previous_bid[1])) < personalbeliefs[l][
                            dice_number - 1]) and \
                            f"{l + 1}" in str(new_connection_mat[i, j]):
                        new_connection_mat[i, j] -= (l + 1) * 10 ** (len(players) - l - 1)

    # Player didnt challenge, so this player also has excessive dice
    if bid_before[0] > dice * (len(players) - 1) and (previous_bid[1] != bid_before[1]):
        excessivedice = bid_before[0] - dice * (len(players) - 1)
        cknowledge[previous_bid[1]-1] = excessivedice*2
        dice_number = bid_before[1]
        for m, player in enumerate(players):
            if m != turn and personalbeliefs[m][dice_number - 1] <\
                    excessivedice + sum(np.array(dicecombos[m]) == bid_before[1]):
                personalbeliefs[m][dice_number - 1] = excessivedice + sum(np.array(dicecombos[m]) == bid_before[1])
        # current player also has excessive dice
        for i, row in enumerate(new_connection_mat):
            for j, value in enumerate(row):
                for n, player in enumerate(players):
                    if ((sum(np.array(world_list[i]) == bid_before[1])) < personalbeliefs[n][dice_number - 1] or
                        (sum(np.array(world_list[j]) == bid_before[1])) < personalbeliefs[n][dice_number - 1]) and \
                            f"{n + 1}" in str(new_connection_mat[i, j]):
                        new_connection_mat[i, j] -= (n + 1) * 10 ** (len(players) - n - 1)
    return new_connection_mat, personalbeliefs, cknowledge


if __name__ == "__main__":
    # players dice sides\
    game_instance = FunctionalGame(3, 2, 2)
    while len(game_instance.players) > 1:
        game_instance.playround()

    print("\nHistory of the game:")
    print(game_instance.connection_mathistory)

    print("\nDice history:")
    print(game_instance.dicehistory)
    print("\nCommon knowledge history:")
    print(game_instance.logic_commonknowledgehistory)
    print("\nPlayer history:")
    print(game_instance.playershistory)
    print("\nLosing player history:")
    print(game_instance.losingplayers)
    print("\nBelief history:")
    print(game_instance.logic_beliefshistory)
    with open("run.txt", 'w') as runfile:
        runfile.write(str(game_instance.dicehistory) + "\n" +
                      str(game_instance.logic_commonknowledgehistory) + "\n" +
                      str(game_instance.playershistory) + "\n" +
                      str(game_instance.losingplayers) + "\n" +
                      str(game_instance.logic_beliefshistory))
