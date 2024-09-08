#!/usr/bin/env python
import atexit
import sys
import termios
import re
import tty
import shutil
from Clict import Clict


def ansi(ansi, parser):
	stdin = sys.stdin.fileno()
	tattr = termios.tcgetattr(stdin)
	tty.setcbreak(stdin, termios.TCSANOW)
	try:
		sys.stdout.write(ansi)
		sys.stdout.flush()
		result = parser()
	finally:
		termios.tcsetattr(stdin, termios.TCSAFLUSH, tattr)
	return result


def info():

	def pos_cursor():
		def Parser():
				buf=''
				while True:
					buf += sys.stdin.read(1)
					if buf[-1] == "R":
						break
				# reading the actual values, but what if a keystroke appears while reading
				# from stdin? As dirty work around, getpos() returns if this fails: None
				try:
					rexy= re.compile(r"^.?\x1b\[(?P<Y>\d*);(?P<X>\d*)R",re.VERBOSE)
					groups=rexy.search(buf).groupdict()
					result={'X': groups['X'],'Y':groups['Y']}
				except AttributeError:
					return {'X': 0,'Y': 0}
				return result
		ansiesc='\x1b[6n'
		return ansi(ansiesc,Parser)

	def bg_color():
		def Parser():
			buf = ''
			for i in range(23):
				buf += sys.stdin.read(1)
			rgb=buf.split(':')[1].split('/')
			rgb={c:int(i,base=16) for c,i in zip([*'RGB'],rgb)}
			tot=[*rgb.values()]
			tot=sum(tot)
			rgb['avg']=(tot/3)/65535
			rgb['max']=65535
			return rgb
		ansiesc='\x1b]11;?\a'
		return ansi(ansiesc,Parser)

	def size():
		s= {'C'  :(shutil.get_terminal_size()[0]),
		 'L' : (shutil.get_terminal_size()[1])}
		return s

	term={'stdout':'not a tty'}
	if sys.stdout.isatty():
		term=Clict()
		term.size={**size()}
		term.cursor={**pos_cursor()}
		term.color.bg={**bg_color()}
		term.get_size=size
		term.get_cursor=pos_cursor
		term.get_color.bg=bg_color
	return term


class Term(Clict):
	def __init__(__s,*a,**k):
		__s.fd  = sys.stdin.fileno()
		__s.live = termios.tcgetattr(__s.fd)
		__s.save = termios.tcgetattr(__s.fd)
		__s.normal =lambda: termios.tcsetattr(__s.fd, termios.TCSAFLUSH, __s.save)
		__s.cursor.hide=__s.__cursor_hide__
		__s.cursor.show=__s.__cursor_show__
		__s.cursor.getxy=__s.__cursor_pos_get__
		atexit.register(__s.normal)
		__s.mode_Ctl()
		__s.initstate()
	def initstate(__s):
		def Parser():
			buf=''
			while True:
				buf += sys.stdin.read(1)
				if buf[-1] == "R":
					break
			# reading the actual values, but what if a keystroke appears while reading
			# from stdin? As dirty work around, getpos() returns if this fails: None
			try:
				rexy= re.compile(r"^.?\x1b\[(?P<Y>\d*);(?P<X>\d*)R",re.VERBOSE)
				groups=rexy.search(buf).groupdict()
				result={'x': groups['X'],'y':groups['Y']}
			except AttributeError:
				return {'x': 0,'x': 0}
			return result
		stdin = sys.stdin.fileno()
		tattr = termios.tcgetattr(stdin)
		tty.setcbreak(stdin, termios.TCSANOW)
		try:
			sys.stdout.write('\x1b[6n')
			sys.stdout.flush()
			result = Parser()
			__s.init.x=result['x']
			__s.init.y=result['y']
		finally:
			termios.tcsetattr(stdin, termios.TCSAFLUSH, tattr)
		return result

	def echo(__s,enable):
		__s.live[3] &= ~termios.ICANON
		if enable:
			__s.live[3] |= termios.ICANON
		__s.update()

	def canonical(__s,enable):
		__s.live[3] &= ~termios.ECHO
		if enable:
			__s.live[3] |= termios.ECHO
		__s.update()
	def mode_Ctl(__s):
		__s.__cursor_hide__()
		__s.echo(False)
		__s.canonical(False)

	def update(__s):
		termios.tcsetattr(__s.fd, termios.TCSAFLUSH, __s.live)
	def __cursor_hide__(__s):
		print('\x1b[?25l',end='',flush=True)
		atexit.register(__s.cursor.show)
	def __cursor_show__(__s):
		print('\x1b[?25h',end='',flush=True)
	def __cursor_pos_get__(__s):
		def Parser():
			buf=''
			while True:
				buf += sys.stdin.read(1)
				if buf[-1] == "R":
					break
			# reading the actual values, but what if a keystroke appears while reading
			# from stdin? As dirty work around, getpos() returns if this fails: None
			try:
				rexy= re.compile(r"^.?\x1b\[(?P<Y>\d*);(?P<X>\d*)R",re.VERBOSE)
				groups=rexy.search(buf).groupdict()
				result={'x': groups['X'],'y':groups['Y']}
			except AttributeError:
				return {'x': 0,'x': 0}
			return result
		ansiesc='\x1b[6n'
		return ansi(ansiesc,Parser)

	def __color_bg_get(__s):
		def Parser():
			buf = ''
			for i in range(23):
				buf += sys.stdin.read(1)
			rgb=buf.split(':')[1].split('/')
			rgb={c:int(i,base=16) for c,i in zip([*'RGB'],rgb)}
			tot=[*rgb.values()]
			tot=sum(tot)
			rgb['avg']=(tot/3)/65535
			rgb['max']=65535
			return rgb
		ansiesc='\x1b]11;?\a'
		return ansi(ansiesc,Parser)
