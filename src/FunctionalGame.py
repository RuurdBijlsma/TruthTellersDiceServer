import itertools
import math
import numpy as np
from itertools import product
import random
import copy
import bids


class FunctionalGame:
    def __init__(self, players, dice, sides, sid=None):
        self.sid = sid
        self.sides = sides

        # players is a list of players [0 1 ....]
        self.players = generateplayerslist(players)

        # Strategies is a list of strategies corresponding to the player ["Random", "Random", "Highest" ... ]
        self.strategies = generatestrategylist(self.players)

        # To keep track of losing players and players in the game
        self.losingplayers = []
        self.playershistory = []
        newplist = copy.copy(self.players)
        self.playershistory.append(newplist)

        # Keep track of the dice
        self.totaldice = 0
        self.dice = dice
        self.dicehistory = []
        self.diceperplayer = diceperplayer(dice, players)

        # Keep track of logic beliefs
        self.logic_beliefs = None
        self.logic_beliefsround = None
        self.logic_beliefshistory = []
        self.logic_commonknowledge = None
        self.logic_commonknowledgeround = None
        self.logic_commonknowledgehistory = []

        self.personalbeliefs = None

        # List all possible worlds and connections between them per player
        self.world_list = None
        self.world_listhistory = []
        self.connection_mat = None
        self.allconnection_mat = None
        self.connection_matround = None
        self.connection_mathistory = []

        # Keep track of bids
        self.bidsround = None
        self.bidshistory = []

        self.dice_combos = None

    def playround(self):
        self.bidsround = []
        self.connection_matround = []

        # Initialize structures that keep track of knowledge
        self.logic_beliefs = []
        self.logic_beliefsround = []
        self.logic_commonknowledge = commonknowledge(self.sides)
        self.logic_commonknowledgeround = []
        self.personalbeliefs = personalbeliefs(self.players, self.sides)

        self.dice_combos = roll_dice(self.players, self.sides, self.diceperplayer)
        print("Dice:")
        print(self.dice_combos)
        self.totaldice = 0
        for dice in self.dice_combos:
            self.totaldice += len(dice)

        # Make initial world list and connection matrix for round
        self.world_list = get_world_list(self.totaldice, self.sides)
        tempwlist = copy.copy(self.world_list)
        self.world_listhistory.append(tempwlist)
        self.connection_mat = get_connection_mat(len(self.world_list), len(self.players))

        # Append initial states to lists that keep track of round states
        self.logic_beliefs = generatebelieflines(self.personalbeliefs, self.logic_commonknowledge)
        tempbeliefs = copy.copy(self.logic_beliefs)
        tempcommonknowledge = copy.copy(self.logic_commonknowledge)
        tempconmat = copy.copy(self.connection_mat)
        self.logic_beliefsround.append(tempbeliefs)
        self.logic_commonknowledgeround.append(tempcommonknowledge)
        self.connection_matround.append(tempconmat)
        self.bidsround.append([])

        print("Initial world list")
        print(self.world_list)
        print("Initial Connection matrix")
        print(self.connection_mat)

        tempdicecombos = copy.copy(self.dice_combos)
        self.dicehistory.append(tempdicecombos)

        # Players look at their dice and initial worlds get removed
        self.connection_mat, self.personalbeliefs = look_at_dice(self.dice_combos,
                                                                 self.players,
                                                                 self.connection_mat,
                                                                 self.world_list,
                                                                 self.sides,
                                                                 self.personalbeliefs)

        # Append states after looking at dice to lists that keep track of round states
        self.logic_beliefs = generatebelieflines(self.personalbeliefs, self.logic_commonknowledge)
        tempbeliefs = copy.copy(self.logic_beliefs)
        tempcommonknowledge = copy.copy(self.logic_commonknowledge)
        tempconmat = copy.copy(self.connection_mat)
        self.logic_beliefsround.append(tempbeliefs)
        self.logic_commonknowledgeround.append(tempcommonknowledge)
        self.connection_matround.append(tempconmat)
        self.bidsround.append([])

        print("New connection matrix")
        print(self.connection_mat)

        # Runs round of bidding, one player without players losing a die
        self.bidding()

        # Append all round history to global history
        temproundcknowledge = copy.copy(self.logic_commonknowledgeround)
        temproundbelief = copy.copy(self.logic_beliefsround)
        temproundconmat = copy.copy(self.connection_matround)
        tempbids = copy.copy(self.bidsround)
        self.logic_commonknowledgehistory.append(temproundcknowledge)
        self.logic_beliefshistory.append(temproundbelief)
        self.connection_mathistory.append(temproundconmat)
        self.bidshistory.append(tempbids)

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
            quantities, previous_bid, self.personalbeliefs = announce_or_challenge(quantities, previous_bid,
                                                                                   self.dice_combos, turn, self.sides,
                                                                                   self.players, self.dice,
                                                                                   self.personalbeliefs,
                                                                                   self.strategies,
                                                                                   self.totaldice)

            # Challenged
            if sum(quantities) < 0:
                challenged = 1
                # See whether players loses dice or not
                sumofdice = 0
                for pdice in self.dice_combos:
                    for eachdice in pdice:
                        if eachdice == previous_bid[1]:
                            sumofdice += 1
                if previous_bid[0] > sumofdice:
                    playerwon = self.players[turn]
                    playerlost = self.players[turn - 1 % len(self.players)]
                    self.losingplayers.append(playerlost)
                    print(f"Player {self.players[turn]} successfully challenged, player "
                          f"{self.players[turn - 1 % len(self.players)]} loses a die")
                    # Remove die
                    self.diceperplayer[self.players[turn - 1 % len(self.players)]] -= 1

                    # If no die, remove player
                    if self.diceperplayer[turn - 1 % len(self.players)] == 0:
                        del self.players[turn - 1 % len(self.players)]
                        del self.strategies[turn - 1 % len(self.players)]

                else:
                    playerwon = self.players[turn - 1 % len(self.players)]
                    playerlost = self.players[turn]
                    self.losingplayers.append(playerlost)
                    print(f"Player {self.players[turn]} unsuccessfully challenged, player "
                          f"{self.players[turn]} loses a die")
                    # Remove die
                    self.diceperplayer[self.players[turn]] -= 1
                    # If no die, remove player
                    if self.diceperplayer[self.players[turn]] == 0:
                        del self.players[turn]
                        del self.strategies[turn]
                newplist = copy.copy(self.players)
                self.playershistory.append(newplist)
            # Not challenged, we update connection matrix and logic lines
            else:
                self.connection_mat, self.personalbeliefs, self.logic_commonknowledge = update_connection_mat(
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
                self.logic_beliefs = generatebelieflines(self.personalbeliefs, self.logic_commonknowledge)
                tempbeliefs = copy.copy(self.logic_beliefs)
                tempcommonknowledge = copy.copy(self.logic_commonknowledge)
                tempconmat = copy.copy(self.connection_mat)
                tempbid = copy.copy(previous_bid)
                self.logic_beliefsround.append(tempbeliefs)
                self.logic_commonknowledgeround.append(tempcommonknowledge)
                self.connection_matround.append(tempconmat)
                self.bidsround.append(tempbid)

                print(f"New quantities: {quantities}")
                turn = (turn + 1) % len(self.players)


def generateplayerslist(players):
    return [x for x in range(players)]


def generatebelieflines(beliefs, cknowledge):
    lines = []
    for i, row in enumerate(beliefs):
        for j, col in enumerate(row):
            for k in range(int(col)):
                lines.append(f"~M_{i} {int(col)}*{j + 1}")
    for n, ck in enumerate(cknowledge):
        for m in range(int(ck)):
            lines.append(f"C~ {int(m)}*{n+1}")
    return lines


# Initiates personal beliefs (how many dice there are at minimum)
def personalbeliefs(players, sides):
    return np.zeros([len(players), sides])


def commonknowledge(sides):
    return np.zeros(sides)


# Players roll their dice, list of lists containing dice per player is returned
def roll_dice(players, sides, diceperplayer):
    dice_combos = []
    for player in players:
        dice_combos.append([random.randint(1, sides) for _ in range(diceperplayer[player])])
    return dice_combos


# Returns histogram of dice
def count(dicelist, sides):
    counts = np.zeros(sides)
    for dice in dicelist:
        counts[dice - 1] += 1

    return counts


def generatestrategylist(players):
    strats = ["Lowest", "Highest", "Random"]
    return [random.choice(strats) for _ in players]


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


def get_world_list(totaldice, sides):
    worlds = []
    sidelist = [x + 1 for x in range(sides)]
    for val in itertools.product(*[sidelist] * (totaldice)):
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
def announce_or_challenge(quantities, previous_bid, dice, turn, sides, players, dicenum, personalbeliefs, strategies,
                          totaldice):
    new_dice = 0
    new_bid = 0
    # Dice that the player in turn holds
    players_dice = np.array(dice[turn])
    # Bid is higher than the belief allows
    if (sum(personalbeliefs[turn]) - personalbeliefs[turn][previous_bid[1] - 1] + previous_bid[0] + 1 > totaldice)\
            or (sum(personalbeliefs[turn]) >= totaldice):
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
        topick = previous_bid[0] - personalbeliefs[turn][previous_bid[1] - 1]  # k
        diceleft = totaldice - len(dice[turn])  # x/n
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
            if strategies[turn] == "Random":
                quantities, personalbeliefs, new_dice, new_bid = \
                    bids.randombid(totaldice, previous_bid, personalbeliefs, quantities, players_dice, turn,
                                   sides)
            elif strategies[turn] == "Lowest":
                quantities, personalbeliefs, new_dice, new_bid = \
                    bids.minbid(totaldice, previous_bid, personalbeliefs, quantities, turn,
                                   sides)
            elif strategies[turn] == "Highest":
                quantities, personalbeliefs, new_dice, new_bid = \
                    bids.aggrobid(totaldice, previous_bid, personalbeliefs, quantities, players_dice, turn,
                                sides)
            else:
                print("Strategy is not in list of strategies")
                assert()
    return quantities, [new_bid, new_dice], personalbeliefs


def diceperplayer(dice, players):
    return [dice for x in range(players)]


def update_connection_mat(connection_mat, previous_bid, bid_before, turn, players, world_list, dice, cknowledge,
                          personalbeliefs, dicecombos):
    new_connection_mat = connection_mat.copy()
    # Player has this dice because he called more dice than possible for the rest
    # Everybody now knows that worlds with less dice than that are impossible
    # The next player has not challenged, meaning he also has those dice.
    if previous_bid[0] > dice * (len(players) - 1):
        excessivedice = previous_bid[0] - dice * (len(players) - 1)
        cknowledge[previous_bid[1] - 1] = excessivedice
        dice_number = previous_bid[1]

        # Update personal belief matrix
        for k, player in enumerate(players):
            if k != turn and personalbeliefs[k][dice_number - 1] < \
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
        cknowledge[previous_bid[1] - 1] = excessivedice * 2
        dice_number = bid_before[1]
        for m, player in enumerate(players):
            if m != turn and personalbeliefs[m][dice_number - 1] < \
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
    gameends = []
    game_instance = FunctionalGame(2, 3, 3)
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
    print("\nBid history:")
    print(game_instance.bidshistory)
    print("\nWorlds list history:")
    print(game_instance.world_listhistory)
    with open("run.txt", 'w') as runfile:
        runfile.write(str(game_instance.dicehistory) + "\n" +
                      str(game_instance.logic_commonknowledgehistory) + "\n" +
                      str(game_instance.playershistory) + "\n" +
                      str(game_instance.losingplayers) + "\n" +
                      str(game_instance.logic_beliefshistory))
