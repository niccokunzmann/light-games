#!/usr/bin/env python3
from tkinter import *

t = Tk()
t.bind("<KeyRelease-Left>", lambda e: print("left-up"))
t.bind("<KeyPress-Left>", lambda e: print("left-down"))
t.bind("<Left>", lambda e: print("left"))

t.mainloop()
