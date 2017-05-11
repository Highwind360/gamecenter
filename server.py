#!/usr/bin/env python3
"""
server.py
Grayson Sinclair

A server for hosting python games that AI can compete over.

TODO: create a lobby so that users can connect, pick a game, then wait to be
    matched up with another player

TODO: require user:pass login
    TODO: make connection use TLS
    TODO: track user's scores at the various games
    TODO: add a scoreboard

TODO: Add some games
    TODO: three-dimensional tic-tac-toe
"""

from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread, Lock, Barrier
from time import sleep

from games import *
from settings import *


def create_listener(addr, port, listener_count):
    s = socket(AF_INET, SOCK_STREAM)
    s.bind((addr, port))
    s.listen(listener_count)
    return s

def send(conn, data, no_newline=False):
    data = bytes(data, ENCODING)
    if not no_newline:
        data += b'\n'
    conn.send(data)

def recv(conn):
    return conn.recv(1024).decode(ENCODING).strip()

def interact(conn, mesg):
    send(conn, mesg, no_newline=True)
    return recv(conn)

def play_game(*players):
    game = ChatRoom()
    while not game.over():
        state = game.gamestate()
        for player in players:
            send(player, state)
        send(players[1], "Waiting for other player to move...")
        response = interact(players[0], "Your move? ")
        while not game.try_move(response):
            send(players[0], game.gamestate())
            send(players[0], "Invalid move! Please try again.")
            response = interact(players[0], "Move? ")
        players = players[::-1]
    state = game.gamestate()
    for player in players:
        send(player, state)
        send(player, "Game Over")
        player.close()# TODO: allow the handler to close these connections

def handle_user_connection(conn):
    is_connected = True
    print("A user has connected.")
    while is_connected:
        send(conn, "Pick an option:\n1: Chat Room\n2: Quit")
        response = recv(conn)
        if response == "1":
            print("Player queued up for the chat room.")
            send(conn, "Entering chat room...")
            with waitlist_lock:
                waitlist.append(conn)
            # TODO: wait for the chat room to say you've exited
            # for now we'll just exit and close the connection in the chat room
            return
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
