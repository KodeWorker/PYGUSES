class base():
    def __init__(self, curses):
        self.curses = curses
    
    def initialization(self):
        self.draw()
    
    def draw(self):
        pass
    
    def draw_hline(self, xmin, xmax, y, char, foreground, background):
        for i in range(xmin, xmax + 1):
            self.curses.put_char(i , y, char, foreground, background)
    
    def draw_vline(self, x, ymin, ymax, char, foreground, background):
        for i in range(ymin, ymax + 1):
            self.curses.put_char(x , i, char, foreground, background)

class Hline(base):
    def __init__(self, xmin, xmax, y, curses, char=' ', foreground='white', background='trans'):
        super(Hline, self).__init__(curses)
        self.xmin = xmin
        self.xmax = xmax
        self.y = y
        self.char = char
        self.foreground = foreground
        self.background = background
        self.initialization()
    
    def draw(self):
        self.draw_hline(self.xmin, self.xmax, self.y, self.char, self.foreground, self.background)
        
class Vline(base):
    def __init__(self, x, ymin, ymax, curses, char=' ', foreground='white', background='trans'):
        super(Vline, self).__init__(curses)
        self.x = x
        self.ymin = ymin
        self.ymax = ymax
        self.char = char
        self.foreground = foreground
        self.background = background
        self.initialization()
            
    def draw(self):
        self.draw_vline(self.x, self.ymin, self.ymax, self.char, self.foreground, self.background)

class Rect(base):
    def __init__(self, x, y, width, height, curses, is_filled=True, char=' ', foreground='white', background='trans'):
        super(Rect, self).__init__(curses)
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.is_filled = is_filled
        self.char = char
        self.foreground = foreground
        self.background = background
        self.initialization()
    
    def draw(self):
        if self.is_filled :
            for i in range(self.height):
                self.draw_hline(self.x, self.x + self.width-1, self.y + i, self.char, self.foreground, self.background)
        else:
            self.draw_hline(self.x, self.x + self.width - 1, self.y, self.char, self.foreground, self.background)
            self.draw_hline(self.x, self.x + self.width - 1, self.y + self.height - 1, self.char, self.foreground, self.background)
            self.draw_vline(self.x, self.y + 1, self.y + self.height - 2, self.char, self.foreground, self.background)
            self.draw_vline(self.x + self.width - 1, self.y + 1, self.y + self.height - 2, self.char, self.foreground, self.background)

class Frame(Rect):
    def __init__(self, x, y, width, height, curses, style=0, is_filled=True, char=' ', foreground='white', background='trans', frame_foreground='white', frame_background='trans'):
        self.style = style
        self.frame_foreground = frame_foreground
        self.frame_background = frame_background
        self.load_style()
        super(Frame, self).__init__(x, y, width, height, curses, is_filled, char, foreground, background)
    
    def load_style(self):
        if self.style == 0:
            self.UR = '/URcorner'
            self.UL = '/ULcorner'
            self.DR = '/DRcorner'
            self.DL = '/DLcorner'
            self.HL = '/Hbar'
            self.VL = '/Vbar'
        elif self.style == 1:
            self.UR = '/2U2Rcorner'
            self.UL = '/2U2Lcorner'
            self.DR = '/2D2Rcorner'
            self.DL = '/2D2Lcorner'
            self.HL = '/2Hbar'
            self.VL = '/2Vbar'
        else:
            raise ValueError('No corresponding style.')
    
    def draw(self):
        self.draw_hline(self.x + 1, self.x + self.width - 2, self.y, self.HL, self.frame_foreground, self.frame_background)
        self.draw_hline(self.x + 1, self.x + self.width - 2, self.y + self.height - 1, self.HL, self.frame_foreground, self.frame_background)
        self.draw_vline(self.x, self.y + 1, self.y + self.height - 2, self.VL, self.frame_foreground, self.frame_background)
        self.draw_vline(self.x + self.width - 1, self.y + 1, self.y + self.height - 2, self.VL, self.frame_foreground, self.frame_background)
        self.curses.put_char(self.x, self.y, self.UL, self.frame_foreground, self.frame_background)
        self.curses.put_char(self.x, self.y + self.height - 1, self.DL, self.frame_foreground, self.frame_background)
        self.curses.put_char(self.x + self.width - 1, self.y, self.UR, self.frame_foreground, self.frame_background)
        self.curses.put_char(self.x + self.width - 1, self.y + self.height - 1, self.DR, self.frame_foreground, self.frame_background)
        if self.is_filled:
            for i in range(1, self.height-1):
                self.draw_hline(self.x + 1, self.x + self.width - 2, self.y + i, self.char, self.foreground, self.background)
        