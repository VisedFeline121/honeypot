# -*- coding: utf-8 -*-
import socket
import platform
import os
from random import randint
import time
import threading
import logging
from datetime import datetime


def share(path):
    sharename = path.split('\\')[-1]
    os.system("net share " + sharename + "=" + path + " /GRANT:everyone,FULL")

FILE_DIR = 'important_files'
PATH = 0
ORIGINAL_DIR = os.getcwd() + '\\%s' % FILE_DIR
# user access
USERNAME = 0
PASSWORD = 1
USER = 0
PASS = 1
# request parsing
COMMAND = 0
ARGS = 1
DATA = 1024
# port selecting
PORT_RANGE_MAX = 254
PORT_RANGE_MIN = 192

BYTES_TO_READ = 8

#USERS = Users().get_users_pass()

def nothing_value(string1):
    x = True
    for i in string1:
        x = x and i == ' '
    return x


def send_error(error_code):
    return error_code + ' \r\n'


def passive_port():
    """
    Return port for passive connection
    """
    p1 = randint(PORT_RANGE_MIN, PORT_RANGE_MAX)
    p2 = randint(PORT_RANGE_MIN, PORT_RANGE_MAX)

    port_to_send = p1 * 256 + p2

    return str(p1), str(p2), port_to_send


# for list
def dir_files(directory):
    """
    Return list of files in
    directory with their properties
    """
    corrected_files = ''
    tab = '     '
    space = ' '
    file_add = '-rw-r--r-- 1 owner group'
    dir_add = 'drwxr-xr-x 1 owner group'

    files = os.listdir(directory)
    for i in files:
        if os.path.isfile(directory + '\\' + i):
            full_path = directory + '\\' + i
            corrected_files += file_add + tab + str(os.path.getsize(full_path)) + space + \
                str(time.strftime('%b %d %H:%M', time.localtime(os.path.getctime(full_path)))) + space + i + '\r\n'
        if os.path.isdir(directory + '\\' + i):
            full_path = directory + '\\' + i
            corrected_files += dir_add + tab + str(os.path.getsize(full_path)) + space + \
                str(time.strftime('%b %d %H:%M', time.localtime(os.path.getctime(full_path)))) + space + i + '\r\n'
    return corrected_files


class Commands(object):
    """
    Handler of commands for the ftp server
    """
    def __init__(self, my_ip):
        self.binary_flag = ''
        self.connection_type = ''
        self.ip = my_ip  # ip to send to client when transferring data
        self.port = 0  # port to send
        self.last_file_position = 0
        self.command_dict = {'USER': self.user_check,
                             #'FEAT': self.get_features, haven't implemented opts
                             'SYST': self.syst_command,
                             'CWD': self.cwd,
                             'PWD': self.pwd,
                             'DELE': self.delete,
                             'TYPE': self.set_binary_flag,
                             'PASV': self.passive_connection,
                             'LIST': self.list_command,
                             'PORT': self.active_connection,
                             'HELP': self.help_command,
                             'RETR': self.retrieve_file,
                             'CDUP': self.cwd,
                             'SIZE': self.return_size,
                             'REST': self.reset_transfer,
                             'RNFR': self.rename,
                             'STOR': self.store_something}

    @staticmethod
    def rename(client, args):
        """
        RNFR and RNTO FTP commands
        """
        #args[0] = file name to change from
        path_to_file = os.getcwd() + '\\' + args[0] # + '\\important_files\\' + args[0]# + ' '.join(args)
        print path_to_file
        wait = "waiting on file new name ("+path_to_file+ ')\r\n'
        #os.chdir(os.getcwd() + '\\important_files')
        if os.path.isfile(path_to_file):
            print wait
            client.send('350 ' + wait)
            name = client.recv(1024)
            if name.split()[0] == 'RNTO':
                print path_to_file
                new_name = name.split()[1]
                print new_name
                os.rename(path_to_file, new_name)
                client.send('250 Succesfully changed name of file\r\n')
                return 'Successfull file change'
            else:
                client.send(send_error('500 Not recieved file\'s new name'))
                #print 'Error recieving new name'
                return  'Error recieving new name'
        else:
            client.send(send_error('500 Not a file'))
            #print 'No such file exists'
            return  'No such file exists'

    def help_command(self, client, args):
        """
        HELP FTP command:
        """
        a = "supported commands: \n"
        for i in self.command_dict.keys():
            a += i + '\n'
        client.send('211' + a + '\r\n')
        return 'Sent help'

    @staticmethod
    def syst_command(client, args):
        """
        SYST FTP command:
        send to client system name
        """
        ok_code = '215'
        client.send(ok_code + " " + platform.system() + "\r\n")
        return "Returned current system"

    def user_check(self, client, args):  # user check
        """
        USER FTP command:
        Get username and password of client to check
        in pass.
        """
        request_password = '331 Please specify password\r\n'
        username = args[USERNAME]

        client.send(request_password)
        response = client.recv(DATA)
        client.send('230 Login succesful, all clear\r\n')
        return 'Client logged in with user: %s pass: %s' % (username, DATA)

    def pass_check(self, client, password, username):
        """
        PASS FTP command:
        Check username and password of client
        """
        succesful_login = '230 Login succesful, all clear\r\n'
        wrong_password = '430 Wrong password\r\n'

        if (username, password) in self.user_data:
            client.send(succesful_login)
            return 'Client logged in with user: %s pass: %s' % (username, password)
        else:
            client.send(wrong_password)
            return 'Client sent wrong username or password'

    @staticmethod
    def delete(client, args):
        """
        DELE FTP command:
        Delete file on server
        """
        print os.getcwd()
        path_to_file = ' '.join(args)
        if os.path.isfile(path_to_file):
            os.remove(path_to_file)
            client.send('250 Requested file has been deleted\r\n')
            return 'Deleted %s ' % ' '.join(args)

        else:
            client.send('550 File not found\r\n')
            return 'Could not find file to delete'

    @staticmethod
    def pwd(client, args):
        """
        PWD FTP command:
        Send to client the path
        of the working directory
        """
        succesful = '257 "%s" is working directory\r\n'
        current_dir = os.getcwd()
        if FILE_DIR not in current_dir:
            client.send(succesful % '\\')  # Files dir
        else:
            client.send(succesful % (os.getcwd().replace(ORIGINAL_DIR, '')))

        return 'Printed current working directory'

    @staticmethod
    def cwd(client, args):
        """
        CWD FTP command:
        Change working directory.
        """
        succesful_change = '250 Succesfully changed directory\r\n'
        full_args = ' '.join(args[PATH:])
        # get path from args
        if len(args) > 0:
            if ORIGINAL_DIR not in full_args:
                path = ORIGINAL_DIR + '\\' + ' '.join(args[PATH:])
            else:
                path = full_args
        else:
            path = '\\'.join(os.getcwd().split('\\')[:-1])

        # change directory
        print path
        if os.path.exists(path) and FILE_DIR in path:
            os.chdir(path)
            client.send(succesful_change)
            return "Succesfully changed directory"
        else:
            client.send('550 Directory does not exist\r\n')
            return "Falied to find directory"

    @staticmethod
    def get_features(client, args):
        """
        FEAT FTP command
        send to client list of
        extra features of the server
        """
        client.send('211-Features:\r\n')
        feat_list = ['feat']  # 'rest' command to remember
        for feature in feat_list:
            client.send(feature + '\r\n')
        client.send('211 End\r\n')

    def set_binary_flag(self, client, args):
        """
        TYPE FTP command:
        issue which type of data to transfer.
        Binary or non binary.
        """
        self.binary_flag = str(args[0])
        if self.binary_flag == 'I':
            self.binary_flag = 'b'
        else:
            self.binary_flag = ''

        client.send('200 flag changed\r\n')

        return "Binary flag changed to %s" % str(args[0])

    def passive_connection(self, client, args):
        """
        PASV FTP command:
        server sends client on
        which port to send data.
        """
        ip_to_send = ','.join(self.ip.split('.'))
        self.port = passive_port()
        port_to_send = ','.join(self.port[:2])
        self.port = self.port[2]
        try:
            to_send = '227 Entering passive mode (%s,%s)\r\n' % (ip_to_send, port_to_send)
            client.send(to_send)
            self.connection_type = 'Passive'
            return "Passive connection mode established"
        except socket.error as e:
            print e
            to_send = '421 Falied to enter passive mode\r\n'
            return "Passive connection mode falied to establish"

    def active_connection(self, client, args):
        """
        PORT FTP command:
        gets data connection
        ip and port from client
        """
        connection = args[0]
        connection = connection.split(',')
        self.ip = '.'.join(connection[:4])
        try:
            self.port = int(connection[4]) * 256 + int(connection[5])
            self.connection_type = 'Active'
            client.send('200 Connected\r\n')
            return "Active connection mode established"
        except ValueError as e:
            print e
            client.send('501 Could not establish data connection\r\n')
            return "Active connection mode falied to establish"

    def list_command(self, client, args):
        """
        LIST FTP command:
        Send to client list
  self.      of files in current directory
        """
        if FILE_DIR in os.getcwd():
            file_list = dir_files(os.getcwd())
        else:
            file_list = dir_files(os.getcwd() + '\\%s' % FILE_DIR)

        transfer_client, transfer_socket = self.transfer_connection()
        # else:
        #     client.send('425 Data connection failed to open\r\n')

        client.send('150 here comes directory listing\r\n')
        transfer_client.send(file_list)
        transfer_client.close()

        client.send('226 Directory send OK.\r\n')

        return "Sent directory listing"

    def transfer_connection(self):
        """
        Return client to use according
        to connection type. Active or passive
        """
        transfer_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if self.connection_type == 'Passive':
            transfer_server.bind((self.ip, self.port))
            transfer_server.listen(1)
            transfer_client, transfer_address = transfer_server.accept()
            return transfer_client, transfer_server
        elif self.connection_type == 'Active':
            transfer_server.connect((self.ip, self.port))
            return transfer_server, None

    def retrieve_file(self, client, args):
        """
        RETR FTP command:
        send file from server to client
        """
        print os.getcwd()
        path = os.getcwd() + "\\" + args[0] # + '\\important_files\\' + args[0]
        #print os.listdir(path)
        #print path
        if os.path.isfile(path):
            client.send('150 opening data connection\r\n')
            transfer_client, transfer_server = self.transfer_connection()
            # send data
            with open(path, 'r' + self.binary_flag) as my_file:
                if self.last_file_position:
                    my_file.seek(self.last_file_position)
                while True:
                    contents = my_file.read(BYTES_TO_READ)
                    if not contents:
                        break
                    transfer_client.send(contents)

            # close connections
            transfer_client.close()
            try:
                transfer_server.close()
            except AttributeError:
                pass
            self.last_file_position = 0
            client.send('226 Transfer complete.\r\n')
            return "File transfer of <%s> complete" % path

        else:
            client.send('550 File does not exist\r\n')
            return "File transfer of <%s> falied" % path

    def reset_transfer(self, client, args):
        try:
            self.last_file_position = int(args[0])
        except ValueError:
            client.send('501 Error in arguments\r\n')
            return
        client.send('350 File pos saved\r\n')
        request = client.recv(1024)
        if 'RETR' in request:
            self.retrieve_file(client, request.split()[ARGS:])
        elif 'STOR' in request:
            self.store_something(client, request.split()[ARGS:])
        else:
            client.send('503 Wrong order of commands\r\n')
            return "Reset. Wrong order of commands"

        return "Reset location of file transfer"

    @staticmethod
    def return_size(client, args):
        """
        SIZE FTP command:
        send to client size of argument file
        """
        path = ' '.join(args)
        client.send('213 %s\r\n' % str(os.path.getsize(path)))
        return "Returned size of file <%s>" % path

    def store_something(self, client, args):
        #os.chdir('important_files')
        transfer_client, transfer_socket = self.transfer_connection()
        with open(args[0], 'wb') as upload:
            x = transfer_client.recv(1024)
            while not nothing_value(x):
                upload.write(x)
                print x
                x = transfer_client.recv(1024)

        client.send('226 transfer complete\r\n')


def get_command_args(request):
    """
    Sort command and args from client request
    """
    if len(request.split()) > 1:
        command = request.split()[COMMAND].upper()
        args = request.split()[ARGS::]
    else:
        command = request.upper()
        args = []

    return command, args


class Server(Commands):
    def __init__(self, port, logger, path, my_ip=socket.gethostbyname(socket.gethostname())):
        super(Server, self).__init__(my_ip)
        self.path = path
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(("0.0.0.0", port))
        self.server_socket.listen(1)
        print "connected"
        self.connections = []
        # output gui
        self.logger = logger
        self.online = True

    def run(self):
        os.chdir(self.path)
        while self.online: # can also add here max number of connections
            client, address = self.server_socket.accept()
            client.send('220 welcome\r\n')

            current_thread = threading.Thread(target=self.main_loop, args=(client, address,))
            current_thread.daemon = True
            current_thread.start()

            self.connections.append(client)

    def main_loop(self, client, address):
        this_client = '%s:%d -> ' % address
        try:
            request = client.recv(DATA).replace('\r\n', '')
            logging.basicConfig(filename='..\honey_log.log', level=logging.DEBUG)
            logging.info(' ' + self.ip + ' used ' + request + ' on ' + str(datetime.now()))
            while self.online:
                print 'request = ' + request
                logging.info(' ' + self.ip + ' used ' + request + ' on ' + str(datetime.now()))
                if not request:  # or command === quit
                    self.connections.remove(client)
                    client.close()
                    self.logger.add_text('%sdisconnected' % this_client)
                    break

                command, args = get_command_args(request)
                try:
                    log = str(self.command_dict[command](client, args))
                    print log
                    #self.logger.add_text(this_client + log)
                #print self.command_dict[command](client, args)
                except KeyError as e:
                    print e
                    client.send('500 command unknown\r\n')

                request = client.recv(DATA).replace('\r\n', '')
        except socket.error:
            pass
            # could remove because gui already prints the client disconnected
            #if self.connections:
            #    self.logger.add_text("Server closed client connection")

    def close_server(self):
        for connection in self.connections:
            connection.close()

        # print threading.activeCount()
        self.online = False
        self.server_socket.close()
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((socket.gethostbyname(socket.gethostname()), 6000))
        #s.connect(('192.168.1.17', 6000))
        s.close()
        self.logger.add_text('Closed Server')


def main():
    print os.system('netstat -an')
    port = input("choose port to set up honeypot server: ")
    s = Server(port, None)
    s.run()


if __name__ == '__main__':
    main()
