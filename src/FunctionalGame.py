# TODO: if a player doesnt challenge a 3 bet, the next player should be challenged
# TODO: append knowledge to list
# TODO: make more rounds
import itertools
import math
import numpy as np
from itertools import product
import random
import copy


class FunctionalGame:
    def __init__(self, players, dice, sides, sid=None):
        self.sid = sid
        self.players = players
        self.dice = dice
        self.sides = sides
        self.personalbeliefs = personalbeliefs(players, dice)

        # Initialize worlds matrix
        self.world_list = get_world_list(players, dice, sides)
        self.connection_mat = get_connection_mat(len(self.world_list), players)
        self.allconnection_mat = np.array([copy.copy(self.connection_mat)])

        print("Initial world list")
        print(self.world_list)
        print("Initial Connection matrix")
        print(self.connection_mat)

        # Let's play the game
        # Roll the dice
        self.dice_combos = roll_dice(self.players, self.sides, self.dice)
        print("Dice:")
        print(self.dice_combos)
        # Players look at their dice and initial worlds get removed
        self.new_connection_mat, self.personalbeliefs = look_at_dice(self.dice_combos,
                                                                     players,
                                                                     self.connection_mat,
                                                                     self.world_list,
                                                                     self.sides,
                                                                     self.personalbeliefs)
        print("New connection matrix")
        print(self.new_connection_mat)
        # Runs first round so without players losing a die
        self.newest_connection_mat, self.logic_lines = self.first_round(self.dice_combos,
                                                                        self.players,
                                                                        self.sides,
                                                                        self.dice)
        print(self.newest_connection_mat)

    def first_round(self, dice_combos, players, sides, dice):
        print("First round")
        challenged = 0
        turn = 0
        quantities = np.zeros(sides)
        print(f"Initial quantities: {quantities}")
        logic_lines = []
        newer_mat = None

        # [Number_of_dice, DiceNumber]
        previous_bid = [0, 1]
        while not challenged:

            # Player who is in turn
            print(f"Player {turn} in turn")
            print(f"Previous bid is {previous_bid}")

            # Action the player takes
            bid_before = copy.copy(previous_bid)
            quantities, previous_bid = announce_or_challenge(quantities, previous_bid, dice_combos, turn, sides,
                                                             self.players, self.dice)

            # Challenged
            if sum(quantities) < 0:
                challenged = 1
                # See whether players loses dice or not
                total_dice = 0
                for pdice in dice_combos:
                    for eachdice in pdice:
                        if eachdice == previous_bid[1]:
                            total_dice += 1
                if previous_bid[0] > total_dice:
                    print(f"Player {turn} successfully challenged, player {(turn - 1) % 3} loses a die")
                else:
                    print(f"Player {turn} unsuccessfully challenged, player {turn % 3} loses a die")
            # Not challenged, we update connection matrix and logic lines
            else:
                newer_mat, self.personalbeliefs = update_connection_mat(self.new_connection_mat, previous_bid,
                                                                        bid_before,
                                                                        turn, self.players, self.world_list, self.dice,
                                                                        self.dice_combos,
                                                                        self.personalbeliefs)
                self.allconnection_mat = np.concatenate((self.allconnection_mat, np.array([newer_mat])), axis=0)
                print(self.allconnection_mat)
                logic_lines.append(f"M_{turn}({previous_bid[0]}*{previous_bid[1]})")
                print(f"New quantities: {quantities}")
                turn = (turn + 1) % players
        #         print(logic_lines)
        # print(logic_lines)

        return newer_mat, logic_lines


# Initiates personal beliefs (how many dice there are at minimum)
def personalbeliefs(players, dice):
    return np.zeros([players, dice])


# Players roll their dice, list of lists containing dice per player is returned
def roll_dice(players, sides, dice):
    dice_combos = []
    for player in range(players):
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
    for player in range(players):
        pdice = dice_combos[player]
        for d in pdice:
            personalbeliefs[player][d - 1] += 1
    # Iterate over every connection between worlds
    for i, row in enumerate(new_mat):
        for j, colval in enumerate(row):
            # Check for every player whether all their dice are in both worlds
            for player in range(players):
                dice = dice_combos[player]
                dicecounts = count(dice, sides)
                horworldcounts = count(world_list[i], sides)
                vertworldcounts = count(world_list[j], sides)
                hordiff = horworldcounts - dicecounts
                vertdiff = vertworldcounts - dicecounts
                for k in range(len(dicecounts)):
                    if (hordiff[k] < 0 or vertdiff[k] < 0) and f"{player + 1}" in str(new_mat[i, j]):
                        new_mat[i, j] -= (player + 1) * 10 ** (players - player - 1)

    return new_mat, personalbeliefs


def get_world_list(players, dice, sides):
    worlds = []
    sidelist = [x + 1 for x in range(sides)]
    for val in itertools.product(*[sidelist] * (players * dice)):
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
def announce_or_challenge(quantities, previous_bid, dice, turn, sides, players, dicenum):
    new_dice = 0
    new_bid = 0
    # Dice that the player in turn holds
    players_dice = np.array(dice[turn])
    # Bid is higher than the possible number according to the players dice
    if previous_bid[0] > players * (dicenum - 1) + sum(players_dice == np.array(previous_bid[1])):
        print("Challenges because of too high number of dice")
        for i, q in enumerate(quantities):
            quantities[i] = -1
        new_dice = previous_bid[1]
        new_bid = previous_bid[0]
    elif previous_bid[0] < sum(players_dice == np.array(previous_bid[1])) and previous_bid[0] != 0:
        print("Challenges because of too low number of dice")
        for i, q in enumerate(quantities):
            quantities[i] = -1
        new_dice = previous_bid[1]
        new_bid = previous_bid[0]

    else:
        prob = random.uniform(0, 1)
        # Challenge
        # probability (number of dice of prev bid - number of dice the player holds of that bid)/
        #               (total # of dice - dice the player holds)
        topick = previous_bid[0] - sum(players_dice == previous_bid[1])  # k
        diceleft = dicenum * (players - 1)  # x/n
        thesum = 0
        if previous_bid[0] != 0:
            # Probability of throwing at least x n's
            for x in range(topick, diceleft + 1):
                thesum += math.factorial(diceleft) / (math.factorial(x) * math.factorial(diceleft - x)) * \
                          ((1 / sides) ** x) * ((1 - 1 / sides) ** (diceleft - x))
        if prob <= thesum:
            print("Challenges because of belief its not true")
            for i, q in enumerate(quantities):
                quantities[i] = -1
            new_dice = previous_bid[1]
            new_bid = previous_bid[0]
        else:
            prob = random.randint(1, 100)
            # 50/50 of bidding higher or bidding next number
            # bid higher
            if prob < 50:
                if previous_bid[0] + 1 > dicenum * players - sum(players_dice == previous_bid[1]):
                    print(f"Challenging because updating pips causes inconsistency")
                    for i, q in enumerate(quantities):
                        quantities[i] = -1
                    new_dice = previous_bid[1]
                    new_bid = previous_bid[0]
                else:
                    print(sum(players_dice == previous_bid[1]))
                    new_bid = random.randint(previous_bid[0] + 1,
                                             dicenum * players + sum(players_dice != previous_bid[1]))
                    quantities[previous_bid[1] - 1] = new_bid
                    new_dice = previous_bid[1]
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
                    new_bid = random.randint(1, players * dicenum - sum(players_dice != new_dice))
                    quantities[new_dice - 1] = new_bid
                    print(f"Updates dice number {previous_bid[1]} to {new_dice}")
                    print(f"Updates number of dice to {new_bid}")

    return quantities, [new_bid, new_dice]


def update_connection_mat(connection_mat, previous_bid, bid_before, turn, players, world_list, dice, playersdice,
                          personalbeliefs):
    new_connection_mat = connection_mat.copy()
    # Player has this dice because he called more dice than possible for the rest
    # Everybody now knows that worlds with less dice than that are impossible
    # The next player has not challenged, meaning he also has those dice.
    if previous_bid[0] > dice * (players - 1):
        excessivedice = previous_bid[0] - dice * (players - 1)
        dice_number = previous_bid[1]

        # Update personal belief matrix
        for player in range(players):
            if player != turn:
                personalbeliefs[player][dice_number - 1] += excessivedice
        for i, row in enumerate(new_connection_mat):
            for j, value in enumerate(row):
                # Remove connections where # of dice <= number of dice the other player has for sure
                for player in range(players):
                    if ((sum(np.array(world_list[i]) == previous_bid[1])) < personalbeliefs[player][dice_number - 1] or
                        (sum(np.array(world_list[j]) == previous_bid[1])) < personalbeliefs[player][
                            dice_number - 1]) and \
                            f"{player + 1}" in str(new_connection_mat[i, j]):
                        new_connection_mat[i, j] -= (player + 1) * 10 ** (players - player - 1)

    if bid_before[0] > dice * (players - 1) and (previous_bid[1] != bid_before[1]):
        excessivedice = bid_before[0] - dice * (players - 1)
        dice_number = bid_before[1]
        for player in range(players):
            if player != turn:
                personalbeliefs[player][dice_number - 1] += excessivedice
        # current player also has excessive dice
        for i, row in enumerate(new_connection_mat):
            for j, value in enumerate(row):
                for player in range(players):
                    if ((sum(np.array(world_list[i]) == bid_before[1])) < personalbeliefs[player][dice_number - 1] or
                        (sum(np.array(world_list[j]) == bid_before[1])) < personalbeliefs[player][dice_number - 1]) and \
                            f"{player + 1}" in str(new_connection_mat[i, j]):
                        new_connection_mat[i, j] -= (player + 1) * 10 ** (players - player - 1)
    return new_connection_mat, personalbeliefs


if __name__ == "__main__":
    # players dice sides
    game_instance = FunctionalGame(3, 1, 2)
    # game_instance = FunctionalGame(3, 2, 2)
