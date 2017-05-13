#
# games.py
#
# A library of classes representing the games the server can proctor, and the
# players participating.
#
# Classes need to define the following methods:
#   over - whether the game is still being played, or someone has won.
#   gamestate - returns the game board as a string to be printed
#   try_move - attempts a move. Changes the game state if valid. Returns whether
#       the move was valid.
#


from threading import Barrier

from networking import *
from structures import DisjointSet
# TODO: you may be able to refactor most networking into the player class


class Player():
    """A way to track and store connections."""
    def __init__(self, connection):
        self._s = connection
        self._b = Barrier(2)

    def wait(self):
        """The thread that calls this will be blocked until it is called again."""
        self._b.wait()

    def socket(self):
        """Yields the socket the player is connected over."""
        return self._s

    def send(self, data):
        send(self._s, data)

    def recv(self):
        return recv(self._s)

    def interact(self, data):
        return interact(self._s, data)

class GameBase():
    """The base class for any game that runs on this server."""
    prompt = "Your move? "

    def help(self):
        """Returns a helpful message on how to play the game."""
        return "The user has not created a help menu for this game."

    def error_message(self):
        """Returns a string explaining why the last move failed.
        If the last move did not fail, behavior is undefined."""
        return "Invalid move! Please try again."

class ChatRoom(GameBase):
    """A simple example of how to program a game class.
    Again, just an example for game programming. It's actually a pretty bad
    chat room."""
    def __init__(self):
        self.history = ""
        self.connected = True

    def over(self):
        return not self.connected

    def gamestate(self):
        return self.history

    def try_move(self, move):
        if move == "quit":
            self.connected = False
        elif move == "invalid":
            return False
        self.history += move + "\n"
        return True

class TicTacToe(GameBase):
    """The game of tic-tac-toe, with adjustable size."""
    def __init__(self, edgelength=3):
        self.edgelen = edgelength
        total_spaces = self.edgelen**2
        self.state = [' '] * total_spaces
        self.boundary = '#'
        self.players = ['X', 'O']
        self.current_player = 0
        self.possible_moves = range(total_spaces)

        # a list of all possible horizontal, vertical, and diagonal win conditions
        self.vertical, self.horizontal, self.diagonal = {}, {}, {}
        for i in range(self.edgelen):
            self.vertical[i] = DisjointSet(list(range(self.edgelen)))
            self.horizontal[i] = DisjointSet(list(range(self.edgelen)))
        for i in ["downwards", "upwards"]:
            self.diagonal[i] = DisjointSet(list(range(self.edgelen)))

    def over(self):
        in_a_line = False
        for element in list(self.vertical.values()) + \
                list(self.horizontal.values()) + list(self.diagonal.values()):
            # if there's only one group, then it's a straight
            # line from one edge to the other: a win condition
            if element.size == 1:
                in_a_line = True
                break
        no_spaces_left = True
        for space in self.state:
            if space == ' ':
                no_spaces_left = False
                break
        return in_a_line or no_spaces_left

    def try_move(self, move):
        """Accepts the move as an integer between 1 and 9.
        The integer represents the space to put your mark,
        numbered from left to right, top to bottom."""
        move = int(move) - 1
        success = False
        # can't make moves outside the range, or in an occupied space
        if move in self.possible_moves and self.state[move] == ' ':
            cur_p = self.players[self.current_player]
            self.state[move] = cur_p
            self.current_player = (self.current_player + 1) % 2
            self.find_connections(move, cur_p)
            success = True
        return success

    def find_connections(self, move, cur_p):
        """Looks for moves on the board that are connected."""
        # coordinates of move
        x, y = move % 3, move // 3

        vertical = self.vertical[x]
        horizontal = self.horizontal[y]

        # TODO: can these checks be factored into a new helper for a 2D grid
        #       of disjoint sets? Could be useful for games where the win
        #       condition is "x in a row".
        # Check if we have an adjacent piece, and register them as a group
        if move - 3 in self.possible_moves and self.state[move - 3] == cur_p:
            vertical.union_find(y, y - 1)
        if move + 3 in self.possible_moves and self.state[move + 3] == cur_p:
            vertical.union_find(y, y + 1)
        if x - 1 > 0 and self.state[move - 1] == cur_p:
            horizontal.union_find(x, x - 1)
        if x + 1 < self.edgelen and self.state[move + 1] == cur_p:
            horizontal.union_find(x, x + 1)

        if x == y: # diagonal downards
            if move - 4 in self.possible_moves and self.state[move - 4] == cur_p:
                self.diagonal["downwards"].union_find(y, y - 1)
            if move + 4 in self.possible_moves and self.state[move + 4] == cur_p:
                self.diagonal["downwards"].union_find(y, y + 1)
        if x == self.edgelen - (y + 1): # self.diagonal upwards
            if move - 2 in self.possible_moves and self.state[move - 2] == cur_p:
                self.diagonal["upwards"].union_find(y, y - 1)
            if move + 2 in self.possible_moves and self.state[move + 2] == cur_p:
                self.diagonal["upwards"].union_find(y, y + 1)

    def gamestate(self):
        width = self.edgelen * 2 + 1
        board = self.boundary * width + "\n"
        for i in range(3):
            row = self.state[i*3:(i+1)*3]
            board += self.boundary + self.boundary.join(row) + self.boundary
            board += "\n" + self.boundary * width + "\n"
        return board

