#!/usr/bin/env python3
"""
server.py
Grayson Sinclair

A server for hosting python games that AI can compete over.

TODO: Add a "routing" list of games so that users can modularly add games into
        the framework.

TODO: require user:pass login
    TODO: make connection use TLS
    TODO: track user's scores at the various games
    TODO: add a scoreboard

TODO: Add some games
    TODO: three-dimensional tic-tac-toe
"""

from time import sleep
from threading import Thread, Lock

from games import *
from settings import *
from networking import *


def play_game(*players):
    game = ChatRoom()
    while not game.over():
        state = game.gamestate()
        for player in players:
            player.send(state)
        players[1].send("Waiting for other player to move...")
        response = players[0].interact("Your move? ")
        while not game.try_move(response):
            players[0].send(game.gamestate())
            players[0].send("Invalid move! Please try again.")
            response = players[0].interact("Move? ")
        players = players[::-1]
    state = game.gamestate()
    for player in players:
        player.send(state)
        player.send("Game Over")
        player.wait() # tell the connection handler we're done with this socket

def handle_user_connection(conn):
    is_connected = True
    print("A user has connected.")
    while is_connected:
        send(conn, "Pick an option:\n1: Chat Room\n2: Quit")
        response = recv(conn)
        # TODO: build out all the cases for games (can this be done automatically?)
        if response == "1":
            print("Player queued up for the chat room.")
            send(conn, "Entering chat room...")
            player = Player(conn)
            with waitlist_lock:
                waitlist.append(player)
            player.wait()
        elif response == "2":
            is_connected = False
            send(conn, "Goodbye.")
            conn.close()
            print("A user has disconnected.")
        else:
            send(conn, "I did not understand your choice. Please try again.")

def pair_off_queued_users():
    while running:
        with waitlist_lock:
            if len(waitlist) > 1:
                user1, user2 = waitlist.pop(0), waitlist.pop(0)
                create_thread(play_game, user1, user2)
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
    waitlist = [] # An array of clients waiting to be paired off
                  # TODO: make a dict of games with arrays for each game chosen
    waitlist_lock = Lock()

    main()

    # Wait to exist until all workers have exited
    running = False
    print("Waiting for workers to exit...")
    for t in threads:
        t.join()
