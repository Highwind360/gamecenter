#
# This is where your configuration variables go.
#

# The most important option! List of games to make available to users.
GAMES = {
    "1": {
        "name": "Chat Room",
        "class": "ChatRoom",
        "arguments": []
    },
    "2": {
        "name": "Tic Tac Toe (3x3)",
        "class": "TicTacToe",
        "arguments": []
    },
    "3": {
        "name": "Tic Tac Toe (5x5)",
        "class": "TicTacToe",
        "arguments": [5]
    },
    "4": {
        "name": "Tic Tac Toe (10x10)",
        "class": "TicTacToe",
        "arguments": [10]
    }
}

# The address/hostname and port to listen on, and the number of handlers for a
# connection.
NETWORK = {
    'ADDRESS': 'localhost', 
    'PORT': 1337,
    'LISTENER_COUNT': 5
}

ENCODING = 'utf-8'
