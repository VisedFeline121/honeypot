# -*- coding: utf-8 -*-
from Tkinter import *
import monitor
import start_server
#import moni


def main():
#    def get_info():
#        project_new.get_info(ip.get())

    def ftp():
        start_server.main()

    def monitor_folder():
        monitor.monitor(path.get())

    #def stop():
     #   honeypot_script.stop()

    def share():
        monitor.share(share_path.get())

    def cw():
        root.destroy()
        exit()

    root = Tk()  # creates interface

    # root.iconbitmap('honeypot.ico')  # creates logo

    root.title("Office Honeypot")  # creates title

    root.configure(background='black')  # creates background

    Label(root, text="WELCOME TO OUR HONEYPOT!", bg="black", fg="white", font="none 12 bold")\
        .grid(row=0,
              column=0,
              sticky=W)  # creates page title

    Label(root, text="Enter path and user's password:", bg="black", fg="white", font="none 12 bold").grid(row=1, column=0, sticky=W)  # creates label

    share_path = Entry(root, width=10, bg="white")
    share_path.grid(row=2, column=0, sticky=W)  # stores folder path
    password = Entry(root, width=10, bg="white")
    password.grid(row=3, column=0, sticky=W)

    Button(root, text="SHARE FOLDER", width=12, command=share).grid(row=4, column=0, sticky=W)  # button for tunneling

    Label(root, text="Enter path:", bg="black", fg="white", font="none 12 bold").grid(row=5, column=0, sticky=W)  # creates label

    path = Entry(root, width=20, bg="white")
    path.grid(row=6, column=0, sticky=W)  # stores folder path

    Button(root, text="MONITOR FOLDER", width=22, command=monitor_folder).grid(row=7, column=0, sticky=W)

    Button(root, text="STOP MONITORING FOLDER", width=22).grid(row=8, column=0, sticky=W)

    Button(root, text="FTP HONEYPOT", width=22, command=cw).grid(row=9, column=0, sticky=W)  # creates exit button

    Button(root, text="EXIT", width=22, command=cw).grid(row=10, column=0, sticky=W)  # creates exit button

    root.mainloop()


if __name__ == '__main__':
    main()
