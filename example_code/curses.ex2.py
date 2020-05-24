import time
import curses



def readline(self, x, y):
        buffer = str()
        curses.echo()
        try:
            i = 0
            while True:
                ch = self.win.getch(x, y + i)
                if ch != -1:
                    if ch in (10, curses.KEY_ENTER):            # enter
                        break
                    if ch in (27, ):
                        buffer = str()
                        break
                    buffer += chr(ch)
                    i += 1
        finally:
            curses.noecho()
        return buffer 



def main(scr):
	curses.curs_set(0)
	curses.init_pair(1,curses.COLOR_BLACK,curses.COLOR_YELLOW)

	h,w=scr.getmaxyx()

	scr.addstr(1,1,'hola')
	scr.addstr(2,2,'hola\n')
	scr.addstr('mundo')
	# print('mundo')
	scr.refresh()
	value=''
	allowed_chars='ABCDEFGHIJKLMNOPQRSTUVWXYZ '
	while 1:
		key = scr.getch()
		if key in (10,curses.KEY_ENTER):
			break
		if key==curses.KEY_LEFT or key==curses.KEY_BACKSPACE:
			value=value[0:-1]
		else:
			if chr(key).upper() in allowed_chars:
				value+=chr(key)
		scr.addstr(10,10,'pulsó la tecla → {}        '.format(chr(key)))
		scr.addstr(12,10,'valor escrito → {}      '.format(value))
		scr.refresh()
	scr.addstr(14,10,'valor entrado → {}'.format(value))
	scr.refresh()

	scr.addstr(15,10,'saliendo...')
	scr.refresh()

	anim='\\|/-'
	anim=anim*8
	for i in anim:
		scr.addstr(18,10,i)
		scr.refresh()
		time.sleep(0.1)


	# scr.attron(curses.color_pair(1))
	# scr.addstr(h//2,w//2-len('Hello'),"Hello")
	# scr.attroff(curses.color_pair(1))
	# scr.refresh()
	# input('Test')

curses.wrapper(main)
