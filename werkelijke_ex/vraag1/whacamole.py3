#!/usr/bin/env python3
__name__        = "whacamole.py3"
__author__      = "Aksh Gupta"
__copyright__   = "Copyright 2020"
__license__     = "MIT"
__version__     = "2020"
__email__       = "jan.celis@kdg.be"
__status__      = "Prototype"
__requires__    = "idle python3-easygui python3-pil.imagetk python3-tk"
__description__ = "Whac a mole game"

# https://github.com/akshgpt7/whac-a-mole

import sys
try:
    import tkinter 
except ModuleNotFoundError:
    sys.stderr.write("Please install module " + __requires__ + "\n")
    sys.exit(1)

from tkinter import *
from time import *
import threading
import random
global whacks

whacks = 0
hole = 0

screen = Tk()
screen.config(bg="blue", width=600, height=620)
screen.resizable(0, 0)
screen.attributes('-topmost', True)
#lab = Label(text="WHAC-A-MOLE!", font=("Algerian", 30), bg='blue', fg='red')
#lab.place(x=110, y=0)
scorelabel = Label(text=whacks, width=7, font=('Bahnschrift', 30), bg='yellow')
scorelabel.place(x=170, y=52)
remark = Label(text="", width=17, bg='blue', fg='yellow', font="Centaur 20")
remark.place(x=130, y=107)


def onwhack():
    global hole
    if hole == 1:
        hole1.config(state='disabled', text='*_*', bg='red', fg='black')
    elif hole == 2:
        hole2.config(state='disabled', text='*_*', bg='red', fg='black')
    elif hole == 3:
        hole3.config(state='disabled', text='*_*', bg='red', fg='black')
    elif hole == 4:
        hole4.config(state='disabled', text='*_*', bg='red', fg='black')
    elif hole == 5:
        hole5.config(state='disabled', text='*_*', bg='red', fg='black')
    elif hole == 6:
        hole6.config(state='disabled', text='*_*', bg='red', fg='black')
    elif hole == 7:
        hole7.config(state='disabled', text='*_*', bg='red', fg='black')
    elif hole == 8:
        hole8.config(state='disabled', text='*_*', bg='red', fg='black')
    elif hole == 9:
        hole9.config(state='disabled', text='*_*', bg='red', fg='black')
    global whacks
    whacks += 1
    scorelabel.config(text="* " + str(whacks) + " *")


hole1 = Button(
    width=6,
    height=3,
    bg='black',
    state='disabled',
    command=onwhack)
hole1.place(x=20, y=160)
hole2 = Button(
    width=6,
    height=3,
    bg='black',
    state='disabled',
    command=onwhack)
hole2.place(x=20, y=290)
hole3 = Button(
    width=6,
    height=3,
    bg='black',
    state='disabled',
    command=onwhack)
hole3.place(x=20, y=420)
hole4 = Button(
    width=6,
    height=3,
    bg='black',
    state='disabled',
    command=onwhack)
hole4.place(x=220, y=160)
hole5 = Button(
    width=6,
    height=3,
    bg='black',
    state='disabled',
    command=onwhack)
hole5.place(x=220, y=290)
hole6 = Button(
    width=6,
    height=3,
    bg='black',
    state='disabled',
    command=onwhack)
hole6.place(x=220, y=420)
hole7 = Button(
    width=6,
    height=3,
    bg='black',
    state='disabled',
    command=onwhack)
hole7.place(x=420, y=160)
hole8 = Button(
    width=6,
    height=3,
    bg='black',
    state='disabled',
    command=onwhack)
hole8.place(x=420, y=290)
hole9 = Button(
    width=6,
    height=3,
    bg='black',
    state='disabled',
    command=onwhack)
hole9.place(x=420, y=420)


def start():
    remark.config(text="")
    t = threading.Thread(target=whac_a_mole)
    t.start()


def whac_a_mole():
    ready_set_whack()
    global hole
    for i in range(0, 60):
        hole = random.randint(1, 9)
        if hole == 1:
            hole1.config(
                state='normal',
                text='【v】__【v】',
                bg='pink',
                fg='black')
            sleep(1)
            hole1.config(state='disabled', text='', bg='black')
        elif hole == 2:
            hole2.config(
                state='normal',
                text='【•】__【•】',
                bg='pink',
                fg='black')
            sleep(1)
            hole2.config(state='disabled', text='', bg='black')
        elif hole == 3:
            hole3.config(
                state='normal',
                text='【=】__【=】',
                bg='pink',
                fg='black')
            sleep(1)
            hole3.config(state='disabled', text='', bg='black')
        elif hole == 4:
            hole4.config(
                state='normal',
                text='【•】__【•】',
                bg='pink',
                fg='black')
            sleep(1)
            hole4.config(state='disabled', text='', bg='black')
        elif hole == 5:
            hole5.config(
                state='normal',
                text='【\】__【/】',
                bg='pink',
                fg='black')
            sleep(1)
            hole5.config(state='disabled', text='', bg='black')
        elif hole == 6:
            hole6.config(
                state='normal',
                text='【-】__【•】',
                bg='pink',
                fg='black')
            sleep(1)
            hole6.config(state='disabled', text='', bg='black')
        elif hole == 7:
            hole7.config(
                state='normal',
                text='【O】__【O】',
                bg='pink',
                fg='black')
            sleep(1)
            hole7.config(state='disabled', text='', bg='black')
        elif hole == 8:
            hole8.config(
                state='normal',
                text='【o】__【o】',
                bg='pink',
                fg='black')
            sleep(1)
            hole8.config(state='disabled', text='', bg='black')
        elif hole == 9:
            hole9.config(
                state='normal',
                text='【•】/\【•】',
                bg='pink',
                fg='black')
            sleep(1)
            hole9.config(state='disabled', text='', bg='black')
    global whacks
    if whacks < 10:
        remark.config(text="POOR")
    elif whacks >= 10 and whacks < 20:
        remark.config(text="BAD")
    elif whacks >= 20 and whacks < 30:
        remark.config(text="DO BETTER!")
    elif whacks >= 30 and whacks < 40:
        remark.config(text="GOOD")
    elif whacks >= 40 and whacks < 50:
        remark.config(text="GREAT!")
    elif whacks >= 50 and whacks < 60:
        remark.config(text="AWESOME!")
    elif whacks == 60:
        remark.config(text="WHACKED 'em ALL!", font="Centaur 18")


def ready_set_whack():
    sleep(1)
    scorelabel.config(text="Ready")
    sleep(1)
    scorelabel.config(text="Set")
    sleep(1)
    scorelabel.config(text="WHACK!!")
    sleep(1)
    scorelabel.config(text="0")


start()

screen.mainloop()
