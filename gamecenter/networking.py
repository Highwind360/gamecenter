"""
networking.py
Grayson Sinclair

A helper library for working with and creating network connections.
"""

from socket import socket, AF_INET, SOCK_STREAM

from .settings import *


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
