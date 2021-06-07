# TODO: if a player doesnt challenge a 3 bet, the next player should be challenged
# TODO: append knowledge to list
# TODO: make more rounds

import numpy as np
from itertools import product
import random
import copy


class FunctionalGame:
    def __init__(self, players, dice, sides):
        self.players = players
        self.dice = dice
        self.sides = sides
        self.logic_lines = []
        self.all_matrices = []
        self.world_list = get_world_list(players, dice, sides)
        self.dice_combos = roll_dice(players, sides)

        connection_mat = get_connection_mat(len(self.world_list), players)
        self.all_matrices.append(connection_mat.copy())
        # Players look at their dice and initial worlds get removed
        new_connection_mat = look_at_dice(self.dice_combos, players, connection_mat, self.world_list)
        self.all_matrices.append(new_connection_mat.copy())
        # Runs first round so without players losing a die

        print("Initial world list")
        print(self.world_list)
        print("Dice:")
        print(self.dice_combos)
        print("Initial Connection matrix")
        print(connection_mat)
        print("New connection matrix")
        print(new_connection_mat)
        newest_connection_mat, new_logic_lines = first_round(self.dice_combos, self.players, self.sides,
                                                             self.world_list, new_connection_mat)
        self.all_matrices.append(newest_connection_mat.copy())
        self.logic_lines += new_logic_lines
        print("Newest connection matrix")
        print(newest_connection_mat)


def first_round(dice_combos, players, sides, world_list, connection_mat):
    print("First round")
    challenged = 0
    turn = 0
    quantities = np.zeros(sides)
    print(f"Initial quantities: {quantities}")
    newer_mat = None
    logic_lines = []

    # [Number_of_dice, DiceNumber]
    previous_bid = [0, 1]
    while not challenged:

        # Player who is in turn
        print(f"Player {turn} in turn")
        print(f"Previous bid is {previous_bid}")

        # Action the player takes
        bid_before = copy.copy(previous_bid)
        quantities, previous_bid = announce_or_challenge(quantities, previous_bid, dice_combos, turn, sides)

        # Challenged
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
        # Not challenged, we update connection matrix and logic lines
        else:
            newer_mat = update_connection_mat(connection_mat, previous_bid, bid_before, turn, players, world_list)
            logic_lines.append(f"M_{turn}({previous_bid[0]}*{previous_bid[1]})")
            print(f"New quantities: {quantities}")
            print(logic_lines)
            turn = (turn + 1) % players
    print(logic_lines)
    return newer_mat, logic_lines


def roll_dice(players, sides):
    dice_combos = []
    for player in range(players):
        dice_combos.append(random.randint(1, sides))
    return dice_combos


def look_at_dice(dice_combos, players, connection_mat, world_list):
    new_mat = connection_mat.copy()
    for i, row in enumerate(new_mat):
        for j, value in enumerate(row):
            common_worlds = np.array(world_list[i]) == np.array(world_list[j])
            for k, boolean in enumerate(common_worlds):
                # Dice are different
                if (not boolean) and \
                        (dice_combos[k] == world_list[i][k] or dice_combos[k] == world_list[j][k]) and \
                        f"{k + 1}" in str(new_mat[i, j]):
                    new_mat[i, j] -= (k + 1) * 10 ** (players - k - 1)
                if boolean and dice_combos[k] != world_list[i][k] and f"{k + 1}" in str(new_mat[i, j]):
                    new_mat[i, j] -= (k + 1) * 10 ** (players - k - 1)
    return new_mat


def get_world_list(players, dice, sides):
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
        if prob <= 100 / (len(dice)) * (previous_bid[0]):
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


def update_for_dice_number(dice_number, new_connection_mat, world_list, turn):
    for i, row in enumerate(new_connection_mat):
        for j, value in enumerate(row):
            # Worlds at position of bidding player are different or his dice is not the same as on that position
            if world_list[i][turn] != dice_number or world_list[j][turn] != dice_number:
                new_connection_mat[i, j] = 0
    # print("Connection matrix updated because player called max number of dice")
    # print(new_connection_mat)


def update_connection_mat(connection_mat, previous_bid, bid_before, turn, dice, world_list):
    new_connection_mat = connection_mat.copy()
    # Player has this dice because he called the maximum number of dice
    if previous_bid[0] == dice:
        update_for_dice_number(previous_bid[1], new_connection_mat, world_list, turn)
    # Player has not challenged so this player also has the dice
    if bid_before[0] == dice:
        update_for_dice_number(bid_before[1], new_connection_mat, world_list, turn)
    return new_connection_mat


if __name__ == "__main__":
    game_instance = FunctionalGame(3, 1, 2)
