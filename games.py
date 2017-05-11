#
# games.py
#
# A library of classes representing the games the server can proctor.
#
# Classes need to define the following methods:
#   over - whether the game is still being played, or someone has won.
#   gamestate - returns the game board as a string to be printed
#   try_move - attempts a move. Changes the game state if valid. Returns whether
#       the move was valid.
# TODO: Add a method for player prompts that is customizable, comes from base class
# TODO: Make the lexical information part of the game state, rather than fixed
#       strings that are sent by the server.
#


class ChatRoom():
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
