from enum import Enum
from random import randint
from os import system
from time import sleep
from getpass import getpass
from termcolor import colored


class Color(Enum):
    RED = 1
    BLUE = 2
    GREEN = 3
    YELLOW = 4

    def __str__(self):
        return colored(self.name, self.name.lower())


class Value(Enum):
    SKIP = 10
    REVERSE = 11
    DRAW = 12


class Wild(Enum):
    WILD = 13
    WILD_DRAW = 14


class NormalCard:
    def __init__(self, value, color):
        self.value = value
        self.color = color

    def __str__(self):
        s = self.value.name if type(self.value) == Value else str(self.value)
        return f"{s} {self.color}"


class WildCard:
    def __init__(self, wild):
        self.wild = wild

    def __str__(self):
        return self.wild.name


class Game:
    def randomize(self, xs):
        for i in range(len(xs) - 1, -1, -1):
            j = randint(0, i)
            xs[j], xs[i] = xs[i], xs[j]

    def repile(self, pile, stack):
        for _ in range(len(stack) - 1):
            pile.append(stack.pop(0))
        self.randomize(pile)

    def match(self, top, throw, curr_color):
        return (
            type(throw) == WildCard
            or throw.color == curr_color
            or type(top) == NormalCard
            and throw.value == top.value
        )

    def turnpossible(self, hand, top, curr_color):
        for card in hand:
            if self.match(top, card, curr_color):
                return True
        return False

    def next_turn(self, turn, reverse):
        return (
            (turn + 1) % self.num_players
            if not reverse
            else (turn - 1) % self.num_players
        )

    def display_cards(self, hands, turn):
        for i in range(len(hands[turn])):
            print(f"{i + 1}) {hands[turn][i]}")

    def __init__(self):
        print("UNO!")
        self.num_players = int(input("Enter number of players: "))
        print("Enter names of players:")
        names = []
        passcodes = []
        for _ in range(self.num_players):
            names.append(input("Enter name: "))
            passcodes_match = True
            while True:
                if not passcodes_match:
                    print("Passcodes don't match. Try again.")
                else:
                    print("Enter passcode to lock the view of your cards.")
                passcode1 = getpass()
                print("Confirm passcode.")
                passcode2 = getpass()
                if passcode1 == passcode2:
                    passcodes.append(passcode1)
                    print("Done!")
                    break
                else:
                    passcodes_match = False
        pile = []
        for color in Color:
            for value in range(10):
                pile.append(NormalCard(value, color))
                if value:
                    pile.append(NormalCard(value, color))
            for value in Value:
                for _ in range(2):
                    pile.append(NormalCard(value, color))
        for wild in Wild:
            for _ in range(4):
                pile.append(WildCard(wild))
        self.randomize(pile)
        hands = [[] for _ in range(self.num_players)]
        print("Distruting hands...")
        for i in range(self.num_players):
            for _ in range(7):
                hands[i].append(pile.pop())
        sleep(2)
        print("Distributed hands!")
        sleep(1)
        _ = input("Press Enter to begin.")
        while type(pile[-1]) == WildCard:
            top = pile.pop()
            pile = [top] + pile
        stack = [pile.pop()]
        curr_color = stack[-1].color
        turn = 0
        reverse = False
        while True:
            system("clear")
            game_over = False
            for i in range(self.num_players):
                if len(hands[i]) == 0:
                    print(names[i], "has won!")
                    game_over = True
                    break
            if game_over:
                break
            print(stack[-1])
            if type(stack[-1]) == WildCard:
                print("Current color:", curr_color.name)
            print("Number of cards in each player's hand:")
            for i in range(self.num_players):
                print(names[i], ":", len(hands[i]), end=" ")
            print()
            print("Turn:", names[turn])
            print("Enter passcode to view cards.")
            while getpass() != passcodes[turn]:
                pass
            print("Your cards:")
            self.display_cards(hands, turn)
            turn_possible = True
            if not self.turnpossible(hands[turn], stack[-1], curr_color):
                if len(pile) == 0:
                    self.repile(pile, stack)
                _ = input("Turn not possible, press Enter to take card from pile.")
                hands[turn].append(pile.pop())
                print(f"Card taken: {str(hands[turn][-1])}")
                sleep(2)
                if not self.turnpossible(hands[turn], stack[-1], curr_color):
                    turn_possible = False
                    print("Turn still not possible.")
                    _ = input("Press Enter to continue.")
                    turn = self.next_turn(turn, reverse)
                else:
                    self.display_cards(hands, turn)
            if turn_possible:
                while True:
                    throw_number = int(input("Enter valid card number to play.\n"))
                    throw_valid = False
                    if 1 <= throw_number <= len(hands[turn]) and self.match(
                        stack[-1], hands[turn][throw_number - 1], curr_color
                    ):
                        throw_valid = True
                    if throw_valid:
                        card = hands[turn][throw_number - 1]
                        hands[turn].remove(card)
                        stack.append(card)
                        if type(card) == WildCard:
                            while True:
                                color_set = input("Enter valid color to set.\n")
                                valid_color = False
                                for color in Color:
                                    if color_set == color.name:
                                        valid_color = True
                                        break
                                if valid_color:
                                    curr_color = color
                                    break
                            turn = self.next_turn(turn, reverse)
                            if card.wild == Wild.WILD_DRAW:
                                if len(pile) < 4:
                                    self.repile(pile, stack)
                                for _ in range(4):
                                    hands[turn].append(pile.pop())
                                turn = self.next_turn(turn, reverse)
                        else:
                            curr_color = card.color
                            if type(card.value) == Value:
                                if card.value == Value.SKIP:
                                    turn = self.next_turn(turn, reverse)
                                elif card.value == Value.REVERSE:
                                    reverse = not reverse
                                else:
                                    turn = self.next_turn(turn, reverse)
                                    if len(pile) < 2:
                                        self.repile(pile, stack)
                                    for _ in range(2):
                                        hands[turn].append(pile.pop())
                            turn = self.next_turn(turn, reverse)
                        break
            system("clear")


if __name__ == "__main__":
    Game()
