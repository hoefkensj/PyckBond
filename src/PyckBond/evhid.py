#!/usr/bin/env python

import os
import time
from Clict import Clict

from pynput.keyboard import Listener as KeyboardListener
from pynput.mouse import Listener as MouseListener
from contextlib import suppress


def kbev():
	def Nt():
		import msvcrt
		def getArrow():
			msvcrt.getch()  # skip 0xE0
			c = msvcrt.getch()
			vals = [72, 77, 80, 75]
			return vals.index(ord(c.decode('utf-8')))

		nt = Clict()
		nt.getch = lambda: msvcrt.getch().decode('utf-8')
		nt.getarrow = getArrow
		nt.event = lambda: msvcrt.kbhit()
		nt.normal_term = lambda: None
		return nt

	def Posix():
		import sys
		import termios
		import atexit
		from select import select
		def init(nx):
			nx.fd = sys.stdin.fileno()
			nx.term.new = termios.tcgetattr(nx.fd)
			nx.term.old = termios.tcgetattr(nx.fd)
			nx.term.new[3] = (nx.term.new[3] & ~termios.ICANON & ~termios.ECHO)
			atexit.register(nx.normal_term)
			atexit.register(nx.echo, True)
			update()
			return nx

		def listener():
			nonlocal nx
			def on_press(key):
				nonlocal nx
				nx.buffer+=[key]

			listener =  KeyboardListener(on_press=on_press)
			return listener

		def loadfn(nx):
			nx.listener=listener()
			nx.echo = enable_echo
			nx.event = lambda: any(select([sys.stdin], [], [], 0))
			nx.getch = lambda: sys.stdin.read(1)
			nx.getkey = getKey
			nx.normal_term = lambda: termios.tcsetattr(nx.fd, termios.TCSAFLUSH, nx.term.old)

			return nx

		def update():
			nonlocal nx
			termios.tcsetattr(nx.fd, termios.TCSANOW, nx.term.new)
			termios.tcsetattr(nx.fd, termios.TCSAFLUSH, nx.term.new)

		def enable_echo(enable):
			nonlocal nx
			new = termios.tcgetattr(nx.fd)
			if enable:
				nx.term.new[3] |= termios.ECHO
			else:
				nx.term.new[3] &= ~termios.ECHO
			update()




		def getKey():
			def readkey():
				nonlocal nx
				key = nx.buffer[-1]
				with suppress(AttributeError):
					if int(str(key.value)[1:-1]) >= 65360:
						sys.stdin.read(3)
						rkey=str(key).split('.')[-1]
				with suppress(AttributeError):
					rkey=str(key.char)
					sys.stdin.read(1)
				with suppress(AttributeError):
					if int(str(key.value)[1:-1]) == 65293:
						rkey='enter'
						sys.stdin.read(1)
				return rkey
			nonlocal nx
			pkey=None
			while not pkey:
				if len(nx.buffer) > 0:
					pkey=readkey()
					break

			nx.buffer.clear()
			return pkey


		nx = Clict()
		nx.buffer=[]
		nx = loadfn(nx)
		nx = init(nx)
		nx.listener.start()
		return nx

	kb=Clict()
	kb.nt=Nt
	kb.posix=Posix
	kb=kb[os.name]()
	return kb

if __name__ == '__main__':
	from time import sleep
	kb=kbev()

	while True:
		if kb.event():
			print('\x1b[5;5H',kb.getkey(),end='')
		sleep(1e-5)
