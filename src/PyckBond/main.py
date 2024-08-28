#!/usr/bin/env python
import time
from pathlib import Path
from Clict import Clict
import re
from contextlib import suppress
from evhid import kbev
from term import info
from textwrap import shorten

def negzero(x):
	return (1-((x<0)-(x>0)*x))


def Menu(root, lvl, X=None, Y=None):

	def Border(D,title):
		def space(B):
			B.space=''
			for i in range(D.m.h+2):
				B.space+='\n'
				D.tracked.y=D.m.h+2
			return B
		def header(B):
			nonlocal D
			conn=''
			B.head=''
			if B.lvl > 0:
				conn += '\x1b[{Y};{X}H─┼──'.format(Y=D.Y,X=D.X)
				D.X=D.X+4

			conn += ('┬' * (B.lvl > 0) + ('┌' * (B.lvl ==0)))
			br = '─' * D.b.w
			BRD=Clict()
			BRD.YX='\x1b[{Y};{X}H'.format(Y=D.Y,X=D.X)
			BRD.CB='{CB}'
			BRD.C= conn
			BRD.HL= br
			BRD.TR='┐'
			BRD.CT='{CT}'
			BRD.TITLE=title.name.capitalize()
			BRD.TL='┌'
			B.head+='{YX}{CB}{C}{HL}{TR}{CT} {TITLE} {CB}{TL}{HL}{TR}'.format(**BRD)
			return B

		def body(B):
			XA='\x1b[{Y};{X}H'
			tpl='{YXA}{CB}{VL}{XYB}{CB}{VL}'
			BRD=Clict()
			BRD.YXA='{YXA}'
			BRD.CB='{CB}'
			BRD.VL='│'
			BRD.XYB='{YXB}'
			prefill=tpl.format(**BRD)
			body=''
			y=int(D.Y)+1
			for i in range(D.m.h):
				xya='\x1b[{Y};{X}H'.format(Y=y,X=D.X)
				xyb='\x1b[{Y};{X}H'.format(Y=y,X=D.X+D.m.w+1)
				body+=prefill.format(YXA=xya,YXB=xyb,CB=BRD.CB)
				y+=1
			B.body=body
			return B

		def footer(B):
			BRD=Clict()
			foot='{YX}{CB}{BL}{HL}{BR}'
			BRD.YX='\x1b[{Y};{X}H'.format(Y=D.Y+D.m.h+1,X=D.X)
			BRD.CB='{CB}'
			BRD.BL='└'
			BRD.HL='─'*D.m.w
			BRD.BR='┘'
			foot=foot.format(**BRD)
			B.foot=foot
			return B

		B=Clict()
		B.lvl=lvl or 0
		B=space(B)
		B=header(B)
		B=body(B)
		B=footer(B)
		return ''.join([B.space,B.head,B.body,B.foot]).format(CT='\x1b[0;1m',CB='\x1b[0;2m')

	def PItems(D,menu):
		C=Clict()
		C.CIT = '\x1b[0;38;2;192;192;192m'
		C.CNR = '\x1b[0;38;2;128;128;128m'
		C.CSEL = '\x1b[0;1;38;2;255;255;255;7m'
		C.RET='\x1b[s\x1b7'

		MENU=Clict()
		MNU=Clict()
		for i, item in enumerate(menu):
			y = D.Y + 1+i
			menuitem='{YX}{CNR}{CSEL}{NR}. {CIT}{CSEL}{ITEM}{SPC}{RET}{NOC}{ORG}'
			name=shorten(item.name,D.m.w-D.n.w-2,placeholder='...')


			MNU[i].YX='\x1b[{Y};{X}H'.format(Y=y, X=D.X+2)
			MNU[i].CSEL='{CSEL}'
			MNU[i].RET='{RET}'
			MNU[i].ORG='\x1b[u\x1b8'
			MNU[i].CNR='{CNR}'.format(**C)
			MNU[i].NR= str(i+1).rjust(D.n.w)
			MNU[i].CIT='{CIT}'.format(**C)
			MNU[i].ITEM=name
			MNU[i].SPC=' '*(D.m.w-len(name)-D.n.w-4)
			MNU[i].NOC='\x1b[m'
			line=menuitem.format(**MNU[i])
			MNU[i].line=line
			MENU[i][1]= MNU[i].line.format(CSEL=C.CSEL,RET=C.RET)
			MENU[i][0]= MNU[i].line.format(CSEL='',RET='')
		return MENU

	def Dimentions(*a, **k):

		D = Clict()
		d = Clict()

		def calc(title, menu):
			nonlocal D
			lng_itemname = max([len(i.name) for i in menu])  # ]A|<-->|Z[
			lng_itemnr = len(str(len(menu)))
			lng_item = lng_itemnr + lng_itemname + 4  # +2 for nr[. ]item +2 space
			lng_title = len(title.name) + 2
			lng_head = lng_title + 4  # 4:'-┐title
			lng_menu = min(max(lng_head, lng_item), 30)
			lng_bord = lng_menu + 2
			D.Y = int(Y or 2)
			D.X = int(X or 1)
			D.i.w = lng_item
			D.n.w = lng_itemnr
			D.t.w = lng_title
			D.h.w = lng_head
			D.m.w = lng_menu
			D.B.w = lng_bord
			D.b.w = negzero(D.B.w - D.h.w) // 2  # title bridge width
			D.B.w = (D.b.w * 2) + D.h.w
			D.m.w = D.B.w - 2
			D.m.h = len(menu)
			D.B.h = D.m.h + 2
			D.Y2  = D.Y+2+D.m.w
			return D

		def read():
			return D

		d.calc = calc(*a)
		D = read()
		return D

	def Selector(n, **k):
		def selector(i):
			nonlocal selection
			selection = wrap(selection + i)
			return selection

		def setval(i):
			nonlocal selection
			selection = wrap(i)
			return selection

		selection = k.get('start', 0)
		wrap = lambda s: ~(~s * -~-n) % n
		slct = Clict()
		slct.up = lambda: selector(-1)
		slct.down = lambda: selector(1)
		slct.read = lambda: selector(0)
		slct.write = setval
		return slct

	def Moved(action,**k):
		nonlocal pM
		old = pM.Current
		new=pM.Selector[action]()
		pM.Current=new
		return old,new

	def Change(action):
		nonlocal pM
		old,new=Moved(action)
		string=''
		string+=pM.pI(old,0)
		string+=pM.pI(new,1)
		return string

	def Init():
		nonlocal pM
		pM.Current=0
		print(''.join([pM.B,pM.I[pM.Current][1],*[pM.I[i+1][0] for i in range(len(pM.M)-1)]]),end='')

	root=Path(root).resolve().absolute()
	# if not root.exists():
		
	T = info()
	# print('\x1b[20;60H',T.get_cursor(),end='')

	menu = [item for item in root.glob('*') if item.is_dir()]
	D=Dimentions(root, menu)

	pM=Clict()
	pM.R=root
	pM.T=T
	pM.XY=pM.T.get_cursor()
	pM.lvl=lvl
	pM.M=menu
	pM.D=D
	pM.B=Border(D, root)
	pM.I=PItems(D,menu)
	pM.Selector=Selector(len(menu))
	pM.Sl=lambda k : Moved(k)
	pM.pB=lambda : print(pM.B)
	pM.pI=lambda i,s: pM.I[i][s]
	pM.init=lambda :Init()
	pM.change= Change
	return pM

def main():
	# menus=[]
	lvl=0

	menus=[]
	maxlvl=2
	M=Menu('/Volumes/F2FSDATA/opt/cellar/lib/runners/', lvl)
	# M.Sl(0)
	M.init()

	loc=M.T.get_cursor()

	kb=kbev()
	print('\x1b[?25l')
	while True:
		print('\x1b[20;60H\x1b[mcursor: \x1b[20;70HX:\x1b[32m{X}\x1b[m \x1b[20;75HY:\x1b[32m{Y}\x1b[m'.format(**loc))
		if kb.event():
			key=kb.getkey()
			if key in ['up','down']:
				print(M.change(key),end='')
				loc=M.T.get_cursor()
				# print('\x1b7\x1b[20;60H{loc}\x1b8'.format(loc=loc))


			elif key in ['right', 'enter']:
				lvl+=1
				menus+=[M]
				print(M.change('read'))
				M=Menu(M.M[M.Current],lvl,**loc)
				M.init()
				loc=M.T.get_cursor()

		time.sleep(0.01)
			#
			# elif key in ['esc','left']:
			#
			# 	lvl-=1
			# 	if lvl<0:
			# 		lvl=0
			# 		continue
			# 	print(M.clr)
			# 	M=menus[lvl]
			# 	menus=menus[:-1]
			# 	s = M.slct.read()
			# 	print(M.menu(s))

		# time.sleep(0.001)

	#read contents of dir
	#parse names and versions outt of content
	#selection menu
# 	choicetree=Clict()
#
# 	CT=choicetree
# 	CT.rootdir.path=Path('/Volumes/F2FSDATA/opt/cellar/lib/runners/').resolve().absolute()
# 	CT.rootdir.name=Path('../../tests/lib/runners').name
#
# 	menu=Clict()
# 	runn=Clict()
# 	wine=Clict()
# 	prot=Clict()
# 	runn.title = 'Runners'
# 	wine.title = 'Wine'
# 	wine.sub = Clict()
# 	prot.title = 'Proton'
# 	prot.sub = Clict()
# 	w=0
# 	p=0
# 	for i,item in enumerate(CT.rootdir.path.glob('*')):
# 		if item.is_dir():
# 			nocase=item.name.casefold()
#
# 			if (('lutris' in nocase) and not ('proton' in nocase)) or ('wine' in nocase):
# 				wine.sub[w].title=item.name
# 				wine.sub[w].value=item
# 				w+=1
#
# 			if ('proton' in nocase) and not ('vkd3d' in nocase):
#
# 				prot.sub[p].title = item.name
# 				prot.sub[p].value = item
# 				p+=1
#
#
# 	T=info()
# 	yog=int(T['cursor']['pos']['Y'])
# 	rc = (0,0)
# 	kb=kbev()
# 	print('\x1b[?25l')
#
# 	menu=menu.sub[0]
# 	while True:
# 		if kb.event():
# 			key=kb.getkey()
#
# 				sln= wrapmen(sln, menu.sub)
# 			elif key == 'right':
# 				sld+=[sln]
# 				menu=menu.sub[sld[-1]]
#
# while True:
# 	if kb.event():
# 		key = kb.getkey()
# 		sel=((key == 'up')*(sel-1))+((key == 'down')*(sel+1))
# 		sel=~(~sel*-~-2)%2
# 		pmenu(sel)
# 		print('\x1b[{Y};{X}H'.format(X=25, Y=YOG), end='')
# 		print(counter)
# 		counter+=1
# 		time.sleep(0.01)

if __name__ == '__main__':
	main()
