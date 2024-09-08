#!/usr/bin/env python

from Clict import Clict

from pynput import keyboard



# def kbev():
# 	def Nt():
# 		import msvcrt
# 		def getArrow():
# 			msvcrt.getch()  # skip 0xE0
# 			c = msvcrt.getch()
# 			vals = [72, 77, 80, 75]
# 			return vals.index(ord(c.decode('utf-8')))
#
# 		nt = Clict()
# 		nt.getch = lambda: msvcrt.getch().decode('utf-8')
# 		nt.getarrow = getArrow
# 		nt.event = lambda: msvcrt.kbhit()
# 		nt.normal_term = lambda: None
# 		return nt
#
#
# 	def Posix():
# 		import sys
# 		import termios
# 		import atexit
# 		from select import select
# 		def init(nx):
# 			nx.fd = sys.stdin.fileno()
# 			nx.term.new = termios.tcgetattr(nx.fd)
# 			nx.term.old = termios.tcgetattr(nx.fd)
# 			nx.term.new[3] = (nx.term.new[3] & ~termios.ICANON & ~termios.ECHO)
# 			atexit.register(nx.normal_term)
# 			atexit.register(nx.echo, True)
# 			update()
# 			return nx
#
# 		def listener():
# 			from pynput.keyboard import Listener as KeyboardListener
# 			def on_press(key):
# 				nonlocal nx
# 				nx.kb.current += [key]
# 				nx.kb.current = [*set(nx.current)]
# 				nx.kb.history += [(key, 1)]
# 				nx.kb.buffer += [key]
#
# 			def on_release(key):
# 				nonlocal nx
# 				nx.kb.history += [(key, 0)]
# 				if key in nx.kb.current:
# 					nx.kb.current = [*set(nx.current)]
# 					nx.kb.current.remove(key)
#
# 			kblistener =  KeyboardListener(on_press=on_press,on_release=on_release)
# 			return kblistener
#
# 		def update():
# 			nonlocal nx
# 			termios.tcsetattr(nx.fd, termios.TCSANOW, nx.term.new)
# 			termios.tcsetattr(nx.fd, termios.TCSAFLUSH, nx.term.new)
#
# 		def enable_echo(enable):
# 			nonlocal nx
# 			new = termios.tcgetattr(nx.fd)
# 			if enable:
# 				nx.term.new[3] |= termios.ECHO
# 			else:
# 				nx.term.new[3] &= ~termios.ECHO
# 			update()
#
# 		def getKey():
# 			def readkey():
# 				nonlocal nx
# 				key = nx.buffer[-1]
# 				with suppress(AttributeError):
# 					if int(str(key.value)[1:-1]) >= 65360:
# 						sys.stdin.read(3)
# 						rkey=str(key).split('.')[-1]
# 				with suppress(AttributeError):
# 					rkey=str(key.char)
# 					sys.stdin.read(1)
# 				with suppress(AttributeError):
# 					if int(str(key.value)[1:-1]) == 65293:
# 						rkey='enter'
# 						sys.stdin.read(1)
# 				return rkey
# 			nonlocal nx
# 			pkey=None
# 			while not pkey:
# 				if len(nx.buffer) > 0:
# 					pkey=readkey()
# 					break
#
# 			nx.buffer.clear()
# 			return pkey
#
# 		def getCode():
# 			def readCode():
# 				nonlocal nx
# 				val=None;Char=None
# 				key=nx.buffer[-1]
# 				with suppress(AttributeError):
# 					val=int(str(key.value)[1:-1])
# 				with suppress(AttributeError):
# 					char=ord(str(key.char))
# 				if val:
# 					sys.stdin.read(3)
# 					ret=val
# 				elif char:
# 					sys.stdin.read(1)
# 					ret=char
# 				return ret
# 			nonlocal nx
# 			keyc=None
# 			while not keyc:
# 				if len(nx.buffer)>0:
# 					keyc=readCode()
# 					break
# 			nx.buffer.clear()
# 			return keyc
#
#
# 		def loadfn(nx):
# 			nx.listener=listener()
# 			nx.echo = enable_echo
# 			nx.event = lambda: any(select([sys.stdin], [], [], 0))
# 			nx.getch = lambda: sys.stdin.read(1)
# 			nx.getkey = getKey
# 			nx.getCode = getCode
# 			nx.normal_term = lambda: termios.tcsetattr(nx.fd, termios.TCSANOW, nx.term.old)
# 			return nx
#
# 		nx = Clict()
# 		nx.buffer=[]
# 		nx.history=[]
# 		nx = loadfn(nx)
# 		nx = init(nx)
# 		nx.listener.start()
# 		return nx
#
# 	kb=Clict()
# 	kb.nt=Nt
# 	kb.posix=Posix
# 	kb=kb[os.name]()
# 	return kb
#

import sys
from select import select

from term import Term

class KB(Clict):
	def __init__(__s,*a,**k):
		super().__init__()
		__s.buffer=[]
		__s.history=[]
		__s.current=[]
	def __on_press__(__s,key):
		__s.current += [key]
		__s.current = [*set(__s.current)]
		__s.history =[*__s.history[1:] + [(key, 1)]]
		__s.buffer += [key]

	def __on_release__(__s,key):
		__s.history += [(key, 0)]
		if key in __s.current:
			__s.current.remove(key)

	def __listener__(__s):
		l=keyboard.Listener(on_press=__s.__on_press__,on_release=__s.__on_release__)
		l.start()
		__s.listener=l


class PosixKBev(Clict):
	def __init__(__s,*a,**k):
		super().__init__()
		# __s.kb.buffer=[]
		# __s.kb.history=[]
		# __s.kb.current=[]
		__s.kb=KB()
		__s.key.history=[*(None,)*64]
		__s.code.history=[]
		__s.key.last=None
		__s.code.last=None
		__s.event= lambda: any(select([sys.stdin], [], [], 0))
		__s.getch = lambda: sys.stdin.read(1)
		__s.kb.__listener__()
		__s.term= Term()

	# def __kb_on_press__(__s,key):
	# 	__s.kb.current += [key]
	# 	__s.kb.current = [*set(__s.current)]
	# 	__s.kb.history =[*__s.kb.history[1:] + [(key, 1)]]
	# 	__s.kb.buffer += [key]
	#
	# def __kb_on_release__(__s,key):
	# 	__s.kb.history += [(key, 0)]
	# 	if key in __s.kb.current:
	# 		__s.kb.current.remove(key)
	#
	# def __listener__(__s):
	# # 	l=keyboard.Listener(on_press=__s.__kb_on_press__,on_release=__s.__kb_on_release__)
	# # 	l.start()
	# 	__s.kb.listener=l

	def event(__s):
		event=any(select([sys.stdin], [], [], 0))
		return  event

	def getKey(__s):
		key = __s.__getKBKey__()
		if 'name' in dir(key):
			rkey=str(key.name).split('.')[-1]

		elif 'char' in dir(key):
					rkey = key.char
		else:
			print(f'\x1b[8;1H\x1b[K{key}')
			print(f'\x1b[9;1H\x1b[K{dir(key)}')
		return rkey

	def getCode(__s):
		key=__s.__getKBKey__()
		# sys.stdin.read(key.clr)
		if 'value' in dir(key):
			if key == keyboard.Key.space:
				code=ord(str(key.value)[1:-1])
			else:
				code=int(str(key.value)[1:-1])
		elif 'char' in dir(key):
			code = ord(key.char)
		else:
			print(f'\x1b[8;1H\x1b[K{key}')
			print(f'\x1b[9;1H\x1b[K{dir(key)}')

		return code
	def __getKBKey__(__s):
		def getkbkey():
			K=keyboard.Key
			key=__s.kb.buffer.pop(-1)
			if 'value' in dir(key):
				if key in [K.space,K.enter,K.home,K.end,K.page_down,K.page_up]:
					print('clearing 1')
					sys.stdin.read(1)
				else:
					key.clr=3
					sys.stdin.read(3)
			elif 'char' in dir(key):
					key.clr=1
					sys.stdin.read(1)
			else:
				print(f'\x1b[8;1H\x1b[K{key}')
				print(f'\x1b[9;1H\x1b[K{dir(key)}')
			return key
		keyc=None
		while not keyc:
			if len(__s.kb.buffer)>0:
				keyc=getkbkey()
				break
			else:
				__s.kb.buffer.clear()
				# time.sleep(1e-6)
		__s.kb.buffer.clear()
		return keyc

from Clict import Clict
from time import time_ns
from datetime import datetime
def timestamp(history=[0,],call=[0,]):
	def shorter(i):
		i=int(i)
		if len(str(i)) > 2 :
			return f'{shorter(str(i)[:2])}{shorter(str(i)[2:])}'
		else:
			return chr((i) + 96) if int(i) < 27 else chr((i % 26 + 48))
	s = Clict()
	s.unix_ns = time_ns()
	t = datetime.fromtimestamp(int(str(s.unix_ns)[:-9]))
	s.human.list = [t.year, t.month, t.day, t.hour, t.minute, t.second]
	s.human.strlist=[str(i) for i in s.human.list]
	s.human.string='-'.join(['.'.join(s.human.strlist[:3]),':'.join(s.human.strlist[3:])])
	s.human.hash='{}{}{}{}{}{}'.format(*[shorter(n) for n in s.human.list])
	s.last_ns=history[-1]
	s.diff=	s.unix_ns-s.last_ns
	s.call=len(call)
	call+=[len(call)]
	history+=[s.unix_ns]
	return s
from time import sleep


if __name__ == '__main__':
	events=0
	# breakpoint()
	kb=PosixKBev()
	print('\x1b[2J\x1b[1;1H')
	while True:
		if kb.event():
			events+=1
			print('\x1b[1;50H',events)
			# print(f'\x1b[2;1H\x1b[Kevent detected: {ts.diff} {ts.call}', end='',flush=True)
			# print('\x1b[5;1H\x1b[Kkey grabbed',kb.getCode())
			print('\x1b[5;1H\x1b[Kkey grabbed',kb.getKey())
		sleep(1e-9)

	# from pynput import keyboard
	# c=keyboard.Controller()
	# l = keyboard.Listener(on_press=lambda p:print(repr(p.value)))
	# l.start()
	# c.tap(keyboard.Key.space)
	# c.tap(keyboard.KeyCode(32))
