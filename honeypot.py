# -*- coding: utf-8 -*-
import logging
import subprocess
import os


def handle_commands(command):
    os.system(command)
    #print command.split(" ")
    #print subprocess.check_output([command.split(" ")])


def main():
    command = ''
    while command != 'exit':
        command = raw_input(os.getcwd() + ': ')
        handle_commands(command)


if __name__ == '__main__':
    main()