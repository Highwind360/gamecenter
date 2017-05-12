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
