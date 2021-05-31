# TODO: if a player doesnt challenge a 3 bet, all players know what dice that player has. Relations can be updated!
# TODO: if a player doesnt challenge a 3 bet, the next player should be challenged
# TODO: append knowledge to list
# TODO: make more rounds

import numpy as np
from itertools import product
import random


class FunctionalGame:
    def __init__(self, players, dice, sides, sid=None):
        self.sid = sid
        self.players = players
        self.dice = dice
        self.sides = sides

        # Initialize worlds matrix
        # only works for players <= 9
        # only worlds for 1 dice per player

        self.world_list = get_world_list(players, dice, sides)
        self.connection_mat = get_connection_mat(len(self.world_list), players)

        print("Initial world list")
        print(self.world_list)
        print("Initial Connection matrix")
        print(self.connection_mat)

        # Let's play the game
        # Roll the dice
        self.dice_combos = roll_dice(players, sides)
        print("Dice:")
        print(self.dice_combos)
        # Players look at their dice and initial worlds get removed
        self.new_connection_mat = look_at_dice(self.dice_combos, players, self.connection_mat, self.world_list)
        print("New connection matrix")
        print(self.new_connection_mat)
        first_round(self.dice_combos, players, sides)


def roll_dice(players, sides):
    dice_combos = []
    for player in range(players):
        dice_combos.append(random.randint(1, sides))
    return dice_combos


def look_at_dice(dice_combos, players, connection_mat, world_list):
    new_connection_mat = np.array(connection_mat, copy=True)
    width = connection_mat.shape[0]
    for i, dice in enumerate(dice_combos):
        for j, world in enumerate(world_list):
            # if dice in index according to player does not have the value of the player.
            if world[i] != dice:
                # Update the rows
                for k, value in enumerate(new_connection_mat[j, :]):
                    if value - (i + 1) * (10 ** (players - 1 - i)) >= 0:
                        if len(str(value)) > len(str(value - (i + 1) * (10 ** (players - 1 - i)))) and \
                                (value == 0 or str(value)[1] == str(value - (i + 1) * (10 ** (players - 1 - i)))[
                                    0]):
                            new_connection_mat[j, k] -= (i + 1) * (10 ** (players - 1 - i))
                        elif len(str(value)) > len(str(value - (i + 1) * (10 ** (players - 1 - i)))) and not \
                                (value == 0 or str(value)[1] == str(value - (i + 1) * (10 ** (players - 1 - i)))[
                                    0]):
                            pass
                        elif str(value - (i + 1) * (10 ** (players - 1 - i)))[i - players + len(str(value))] == "0":
                            new_connection_mat[j, k] -= (i + 1) * (10 ** (players - 1 - i))
                # Update the columns
                for k, value in enumerate(new_connection_mat[:, j]):
                    if value - (i + 1) * (10 ** (players - 1 - i)) >= 0:
                        if len(str(value)) > len(str(value - (i + 1) * (10 ** (players - 1 - i)))) and \
                                (value == 0 or str(value)[1] == str(value - (i + 1) * (10 ** (players - 1 - i)))[
                                    0]):
                            new_connection_mat[k, j] -= (i + 1) * (10 ** (players - 1 - i))
                        elif len(str(value)) > len(str(value - (i + 1) * (10 ** (players - 1 - i)))) and not \
                                (value == 0 or str(value)[1] == str(value - (i + 1) * (10 ** (players - 1 - i)))[
                                    0]):
                            pass
                        elif str(value - (i + 1) * (10 ** (players - 1 - i)))[i - players + len(str(value))] == "0":
                            new_connection_mat[k, j] -= (i + 1) * (10 ** (players - 1 - i))
    return new_connection_mat


def first_round(dice_combos, players, sides):
    print("First round")
    challenged = 0
    turn = 0
    quantities = np.zeros(sides)
    print(f"Initial quantities: {quantities}")
    logic_lines = []

    # [Number_of_dice, DiceNumber]
    previous_bid = [0, 1]
    while not challenged:

        # Player who is in turn

        print(f"Player {turn} in turn")
        print(f"Previous bid is {previous_bid}")
        # Action the player takes
        quantities, previous_bid = announce_or_challenge(quantities, previous_bid, dice_combos, turn, sides)
        if sum(quantities) < 0:
            challenged = 1
            # See whether players loses dice or not
            total_dice = 0
            for d in dice_combos:
                if d == previous_bid[1]:
                    total_dice += 1
            if previous_bid[0] > total_dice:
                print(f"Player {turn} successfully challenged, player {(turn - 1) % 3} loses a die")
            else:
                print(f"Player {turn} unsuccessfully challenged, player {turn} loses a die")
        else:
            logic_lines.append(f"M{turn}({previous_bid[0]}*{previous_bid[1]})")
            print(f"New quantities: {quantities}")
            turn = (turn + 1) % players
            print(logic_lines)
    print(logic_lines)


def get_world_list(players, dice, sides):
    worlds = []

    i_need_this_list = []
    for i in range(sides):
        i_need_this_list.append(i + 1)

    # this one is for more than 2 sides
    # combos = list(set(list(combinations_with_replacement(i_need_this_list,dice))))

    return list(product(i_need_this_list, repeat=players))


def get_connection_mat(n_worlds, players):
    the_number = 0
    for i in range(players + 1):
        the_number += i * 10 ** (players - i)
    return np.full((n_worlds, n_worlds), the_number)


# If all quantities are -1, we challenge
def announce_or_challenge(quantities, previous_bid, dice, turn, sides):
    new_dice = 0
    new_bid = 0
    # Dice that the player in turn holds
    players_dice = dice[turn]
    # Bid is higher than the possible number according to the players dice
    if previous_bid[1] != players_dice and previous_bid[0] >= len(dice):
        print("Challenges because of impossible bid")
        for i, q in enumerate(quantities):
            quantities[i] = -1
            new_dice = previous_bid[1]
            new_bid = previous_bid[0]

    # Same dice 25/50/75 % chance of challenging
    elif previous_bid[1] == players_dice:
        prob = random.randint(1, 100)
        if prob <= 100 / (len(dice) + 1) * previous_bid[0]:
            print("Holds the same dice and challenges")
            for i, q in enumerate(quantities):
                quantities[i] = -1
            new_dice = previous_bid[1]
            new_bid = previous_bid[0]
        else:
            prob = random.randint(1, 100)
            # Update current number
            if prob <= 75:
                if previous_bid[0] + 1 > len(dice):
                    print(f"Holds the same dice and challenges because of impossible update")
                    for i, q in enumerate(quantities):
                        quantities[i] = -1
                    new_dice = previous_bid[1]
                    new_bid = previous_bid[0]
                else:
                    new_bid = random.randint(previous_bid[0] + 1, len(dice))
                    quantities[previous_bid[1] - 1] = new_bid
                    new_dice = previous_bid[1]
                    print(f"Holds the same dice and updates current dicenumber to {new_bid}")
            # Update next number
            else:
                # If number is not on dice, challenge
                if previous_bid[1] + 1 > sides:
                    print(f"Holds the same dice and challenges because of impossible update from self")
                    for i, q in enumerate(quantities):
                        quantities[i] = -1
                    new_dice = previous_bid[1]
                    new_bid = previous_bid[0]
                # Update next dice number
                else:
                    new_dice = random.randint(previous_bid[1] + 1, sides)
                    new_bid = random.randint(1, len(dice) - 1)
                    print(f"Holds the same dice and updates dice {new_dice} to {new_bid}")
                    quantities[new_dice - 1] = new_bid
    # Has a different dice than the bid 50/75/100 %
    else:
        prob = random.randint(1, 100)
        if prob <= 100 / (len(dice) + 1) * (previous_bid[0]):
            print("Holds different dice and challenges")
            for i, q in enumerate(quantities):
                quantities[i] = -1
            new_dice = previous_bid[1]
            new_bid = previous_bid[0]
        else:
            prob = random.randint(1, 100)
            # Update current number
            if prob <= 75:
                if previous_bid[0] + 1 > len(dice) - 1:
                    print(f"Holds the same dice and challenges because of impossible update")
                    for i, q in enumerate(quantities):
                        quantities[i] = -1
                else:
                    new_bid = random.randint(previous_bid[0] + 1, len(dice) - 1)
                    print(f"Holds different dice and updates current dice number to {new_bid}")
                    quantities[previous_bid[1] - 1] = new_bid
                    new_dice = previous_bid[1]
            else:
                # If number is not on dice, challenge
                if previous_bid[1] + 1 > sides:
                    print(f"Holds different dice and challenges because of impossible update from self")
                    for i, q in enumerate(quantities):
                        quantities[i] = -1
                    new_dice = previous_bid[1]
                    new_bid = previous_bid[0]
                # Update next dice number
                else:
                    new_bid = random.randint(1, len(dice))
                    new_dice = random.randint(previous_bid[1] + 1, sides)
                    print(f"Holds different dice and updates dice {new_dice} to {new_bid}")
                    quantities[new_dice - 1] = new_bid
    return quantities, [new_bid, new_dice]


if __name__ == "__main__":
    i = FunctionalGame(3, 1, 2)
