#!/usr/bin/env python3
"""
server.py
Grayson Sinclair

A server for hosting python games that AI can compete over.

TODO: require user:pass login
    TODO: make connection use TLS
    TODO: track user's scores at the various games
    TODO: add a scoreboard

TODO: when a user abruptly disconnects from a game, tell the other users
    why they were kicked from the game.

TODO: Add some games
    TODO: tic-tac-toe of any edge length
    TODO: three-dimensional tic-tac-toe
    TODO: add support for games that require more than two players
        TODO: add queue support for making a single player control multiple
            players' in a game where the queue isn't full enough
"""

from time import sleep
from itertools import count
from threading import Thread, Lock
from traceback import format_exc

from . import games
from .settings import *
from .networking import *


def play_game(game, *players):
    playing = not game.over()
    try:
        while playing:
            state = game.gamestate()
            for player in players:
                player.send(state)
            players[1].send("Waiting for other player to move...")
            response = players[0].interact(game.prompt)
            # process all commands that do not end a user's turn
            while response in ["help"]:
                players[0].send(game.help())
                response = players[0].interact(game.prompt)
            # allow a user to exit the game early, if necessary
            if response == "quit":
                players[0].send("Abandoning match.")
                players[1].send("The other player has quit.")
                playing = False
            # if the engine cannot interpret the input, it leaves it to the game
            try:
                while playing and not game.try_move(response):
                    players[0].send(game.gamestate())
                    players[0].send(game.error_message())
                    response = players[0].interact(game.prompt)
            except BrokenPipeError:
                raise BrokenPipeError
            except Exception as err:
                error_message = "There was an error making a move. Exiting the game, now."
                for player in players:
                    player.send("\n" + error_message + "\n")
                print(error_message, format_exc())
                playing = False
            players = players[::-1]
            playing = playing and not game.over()
        state = game.gamestate()
        for player in players:
            player.send(state)
            player.send("Game Over")
            # tell the connection handler we're done with this socket
    except BrokenPipeError:
        print("A player unexpectedly disconnected from a game.")
        # TODO: how do you determine which players to message about the disconnect?
    # free all players to resume choosing a game to play
    for player in players:
        player.toggle_wait()

def handle_user_connection(conn):
    is_connected = True
    print("A user has connected.")
    while is_connected:
        try:
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
                player.toggle_wait()
            else:
                send(conn, "I did not understand your choice. Please try again.")
        except BrokenPipeError:
            print("Connection to a user has been lost.")
            is_connected = False

def pair_off_queued_users():
    while running:
        with waitlist_lock:
            for identifier in waitlist.keys():
                wl = waitlist[identifier]
                if len(wl) > 1:
                    # fetches the game class named in the "class" game settings
                    game_class = GAMES[identifier]["class"]
                    game_args = GAMES[identifier]["arguments"]
                    new_game = games.__getattribute__(game_class)(*game_args)
                    user1, user2 = wl.pop(0), wl.pop(0)
                    create_thread(play_game, new_game, user1, user2)
        sleep(1)
    # clean out occupied queues
    for wl in waitlist.values():
        for player in wl:
            player.toggle_wait()

def create_thread(thread_target, *args):
    t = Thread(target=thread_target, args=(args))
    t.start()
    threads.append(t)

def main():
    global running, threads, waitlist, gamelist, greeting_string, waitlist_lock

    # initialize global variables
    running = True
    threads = []
    waitlist, gamelist = {}, {}
    greeting_string = "Welcome to the GameCenter! Please pick a queue.\n"
    for identifier in map(str, list(set(map(int, GAMES.keys())))): # sort games by ID
        waitlist[identifier] = []
        game = GAMES[identifier]
        greeting_string += identifier + ". " + game["name"] + "\n"
        gamelist[identifier] = games.__getattribute__(game["class"])
    greeting_string += "\n0. Quit"
    waitlist_lock = Lock()

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
        print("Shutting down!")
        listener.close()

        # Wait to exit until all workers have exited
        running = False
        print("Waiting for workers to exit...")
        for t in threads:
            t.join()
