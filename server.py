#!/usr/bin/env python3
"""
server.py
Grayson Sinclair

A server for hosting python games that AI can compete over.

TODO: allow the server to be killed while users are logged on: gracefully shut down
TODO: allow users to ungracefully disconnect without throwing errors

TODO: require user:pass login
    TODO: make connection use TLS
    TODO: track user's scores at the various games
    TODO: add a scoreboard

TODO: Add some games
    TODO: tic-tac-toe of any edge length
    TODO: three-dimensional tic-tac-toe
    TODO: add support for games that require more than two players
        TODO: add queue support for making a single player control multiple
                'players' in a game where the queue isn't full enough
"""

from time import sleep
from itertools import count
from threading import Thread, Lock

import games
from settings import *
from networking import *


def play_game(game, *players):
    playing = not game.over()
    while playing:
        state = game.gamestate()
        for player in players:
            player.send(state)
        players[1].send("Waiting for other player to move...")
        response = players[0].interact(game.prompt)
        while response in ["help", "quit"]:
            if response == "help":
                players[0].send(game.help())
            else:
                players[0].send("Abandoning match.")
                players[1].send("The other player has quit.")
                playing = False
            response = players[0].interact(game.prompt)
        while playing and not game.try_move(response):
            players[0].send(game.gamestate())
            players[0].send(game.error_message())
            response = players[0].interact(game.prompt)
        players = players[::-1]
        playing = playing and not game.over()
    state = game.gamestate()
    for player in players:
        player.send(state)
        player.send("Game Over")
        player.wait() # tell the connection handler we're done with this socket

def handle_user_connection(conn):
    is_connected = True
    print("A user has connected.")
    while is_connected:
        send(conn, greeting_string)
        response = recv(conn)
        if response == "0":
            is_connected = False
            send(conn, "Goodbye.")
            conn.close()
            print("A user has disconnected.")
        elif response in GAMES.keys():
            print("Player queued up for " + GAMES[response]["name"] + "!")
            send(conn, "Searching for game...")
            player = games.Player(conn)
            with waitlist_lock:
                waitlist[response].append(player)
            player.wait()
        else:
            send(conn, "I did not understand your choice. Please try again.")

def pair_off_queued_users():
    while running:
        with waitlist_lock:
            for identifier in waitlist.keys():
                wl = waitlist[identifier]
                if len(wl) > 1:
                    # fetches the game class named in the "class" game settings
                    new_game = games.__getattribute__(GAMES[identifier]["class"])()
                    user1, user2 = wl.pop(0), wl.pop(0)
                    create_thread(play_game, new_game, user1, user2)
        sleep(1)

def create_thread(thread_target, *args):
    t = Thread(target=thread_target, args=(args))
    t.start()
    threads.append(t)

def main():
    listener = create_listener(
        NETWORK['ADDRESS'],
        NETWORK['PORT'],
        NETWORK['LISTENER_COUNT']
    )
    create_thread(pair_off_queued_users)
    try:
        while True:
            (socket, addr) = listener.accept()
            create_thread(handle_user_connection, socket)
    except KeyboardInterrupt:
        print("Shutting down.")
        listener.close()


if __name__ == "__main__":
    # initialize global variables
    running = True
    threads = []
    waitlist, gamelist = {}, {}
    greeting_string = "Welcome to the GameCenter! Please pick a queue.\n"
    for identifier in list(set(GAMES.keys())): # sort games by ID
        waitlist[identifier] = []
        game = GAMES[identifier]
        greeting_string += identifier + ". " + game["name"] + "\n"
        gamelist[identifier] = games.__getattribute__(game["class"])
    greeting_string += "\n0. Quit"
    waitlist_lock = Lock()

    main()

    # Wait to exist until all workers have exited
    running = False
    print("Waiting for workers to exit...")
    for t in threads:
        t.join()
