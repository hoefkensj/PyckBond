#!/usr/bin/env python

import sys
import termios
import re
import tty
import shutil
from Clict import Clict
def info():
	def ansi(ansi,parser):
		stdin = sys.stdin.fileno()
		tattr = termios.tcgetattr(stdin)
		tty.setcbreak(stdin, termios.TCSANOW)
		try:
			sys.stdout.write(ansi)
			sys.stdout.flush()
			result=parser()
		finally:
			termios.tcsetattr(stdin, termios.TCSANOW, tattr)
		return result

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


