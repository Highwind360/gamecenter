#
# This is where your configuration variables go.
#

# The most important option! List of games to make available to users.
GAMES = {
    "1": {
        "name": "Chat Room",
        "class": "ChatRoom"
    },
    "2": {
        "name": "Tic Tac Toe (Naughts and Crosses)",
        "class": "TicTacToe"
    }
}

# The address/hostname and port to listen on, and the number of handlers for a
# connection.
NETWORK = {
    'ADDRESS': 'localhost', 
    'PORT': 3001,
    'LISTENER_COUNT': 5
}

ENCODING = 'utf-8'
