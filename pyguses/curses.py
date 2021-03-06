# Special ALT Characters
# http://www.tedmontgomery.com/tutorial/altchrc-a.html

import os
import configparser
import pygame
import numpy as np
from .color import colornames
from .util import check_divisibility

class Curses():
    
    def __init__(self, screen_width, screen_height, color):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.color = color
        self.initializaton()

    # Initialization
    def initializaton(self):
        # Game config settings
        config = configparser.ConfigParser()
        config.read(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.ini'))
        
        self.cell_width = int(config['DISPLAY']['width'])
        self.cell_height = int(config['DISPLAY']['height'])
        
        original_width = int(config['ASSETS']['width'])
        original_height = int(config['ASSETS']['height'])
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), config['ASSETS']['path'])
        
        # Generate curses image array
        self.image_array = self.get_image_array(original_width, original_height, path)
        self.default_background = self.image_array[0, 0].get_at((0, 0))
        self.default_foreground = self.image_array[-3, -5].get_at((0, 0))
        
        # Generate empty curses window
        self.win_width = check_divisibility(self.cell_width, self.screen_width)
        self.win_height = check_divisibility(self.cell_height, self.screen_height)
        self.clear_window()
        
        # Generate character array
        self.char_array = self.get_char_array()
        
        # Generate color dictionary
        self.colored_char_dict={}
        
        # Generate background surface
        self.background = pygame.Surface((self.screen_width, self.screen_height)).convert_alpha() 
        self.background.fill(colornames[self.color])
        self.foreground = pygame.Surface([self.screen_width, self.screen_height], pygame.SRCALPHA, 32).convert_alpha()        
    
    # Clear window
    def clear_window(self):
        self.window = np.empty([self.win_height, self.win_width], dtype=dict)
        for i in range(self.win_height):
            for j in range(self.win_width):
                self.put_char(j, i)
    
    # Load curses images
    def get_image_array(self, width, height, path):
        surface = pygame.image.load(path).convert_alpha()
        width_count = check_divisibility(width, surface.get_width())
        height_count = check_divisibility(height, surface.get_height())
        
        image_array = np.empty([height_count, width_count], dtype=pygame.Surface)
        for i in range(height_count):
            for j in range(width_count):
                image_array[i ,j] = surface.subsurface(j*width, i*height, width, height).convert_alpha() 
                image_array[i ,j] = pygame.transform.scale(image_array[i ,j], (self.cell_width, self.cell_height))
        return image_array
    
    def put_char(self, x, y, char=' ', foreground='white', background='transparent'):
            self.window[y, x] = {'char' : char, 'foreground' : foreground, 'background' : background}
    
    def put_message(self, x, y , message, foreground='white', background='transparent', auto=True, align='left', box_x=0, box_y=0, box_width=None, box_height=None):
        if box_width == None:
            box_width = self.win_width
        if box_height == None:
            box_height = self.win_height
        
        char_list = self.get_char_list(message)
        # Set alignment
        if align == 'left':
            cur_x = x
        elif align == 'mid':
            cur_x = x - int(len(char_list)/2)
        elif align == 'right':
            cur_x = x - len(char_list) + 1
            
        # check initial cursor position
        cur_y = y
        if cur_x < box_x:
            cur_y -= int(np.ceil( (box_x - cur_x) / box_width))
            cur_x = box_x + box_width - (box_x - cur_x) % box_width
        
        if cur_y < box_y:
            char_list = char_list[(box_y - cur_y ) * box_width - (cur_x - box_x):]
            cur_x = box_x
            cur_y = box_y
            
        ind = 0
        x_ = 0
        while ind < len(char_list):
            if auto :
                if cur_x + x_ < box_width + box_x:
                    self.put_char(cur_x + x_, cur_y, char_list[ind], foreground, background)
                else:
                    x_ -= box_width
                    cur_y += 1
                    if cur_y < box_height + box_y:
                        self.put_char(cur_x + x_, cur_y, char_list[ind], foreground, background)
                    else:
                        break
            else:
                if cur_x + x_ < box_width + box_x and cur_y < box_height + box_y - 1:
                    self.put_char(cur_x + x_, cur_y, char_list[ind], foreground, background)
            x_ += 1
            ind += 1
    
    def get_cell(self, x, y):
        return self.window[y, x]
    
    def set_cell(self, x, y, cell):
        self.window[y, x] = cell    
    
    def get_window_surface(self):
        surface = pygame.Surface((int(self.cell_width*self.window.shape[1]), int(self.cell_height*self.window.shape[0])), pygame.SRCALPHA, 32).convert_alpha()
        for i in range(self.window.shape[0]):
            for j in range(self.window.shape[1]):
                subsurface = self.get_cell_surface(j, i)
                surface.blit(subsurface, (int(j*self.cell_width), int(i*self.cell_height)))        
        return surface
    
    def get_cell_surface(self, x, y):
        char = self.window[y, x]['char']
        foreground = self.window[y, x]['foreground']
        background = self.window[y, x]['background']        
        key = char+'-'+foreground+'-'+background
        
        if key in self.colored_char_dict.keys():
            colored_image = self.colored_char_dict[key]
        else:
            original_image = self.get_image_by_char(char)            
            colored_image = self.get_colored_image(original_image, foreground, background)
            self.colored_char_dict[key] = colored_image
        return colored_image
            
    def get_colored_image(self, image, foreground, background):
        surface = image.copy()
        pixel_array = pygame.PixelArray(surface)
        if colornames[foreground] != self.default_background:
            pixel_array.replace(self.default_foreground, colornames[foreground])
            pixel_array.replace(self.default_background, colornames[background]) 
        else:
            pixel_array.replace(self.default_background, colornames[background])
            pixel_array.replace(self.default_foreground, colornames[foreground])               
        surface = pixel_array.surface
        return surface
        
    def get_image_by_char(self, char):
        # Check unique characters
        ind = np.argwhere(self.char_array == char)
        if len(ind) != 0:
            original_image = self.image_array[ind[0][0], ind[0][1]]        
        else:
            # No maching character -> generate surface from font
            original_image = pygame.font.Font(None, 50).render(char, 0, self.default_foreground, self.default_background).convert_alpha() 
            original_image = pygame.transform.scale(original_image, (self.cell_width, self.cell_height))
            
        return original_image
    
    def get_char_array(self):
        # Character to image mapping
        char_list_0 = ['', '☺', '☻', '♥', '♦', '♣', '♠', '●', '◘', '○', '◙', '♂', '♀', '♪', '♫', '☼']
        char_list_1 = ['▶', '◀', '↕', '‼', '¶', '§', '▬', '↨', '↑', '↓', '→', '←', '∟', '↔', '▲', '▼']
        char_list_2 = [' ', '!', '"', '#', '$', '%', '&', '\'', '(', ')', '*', '+', ',', '-', '.', '/']
        char_list_3 = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', ':', ';', '<', '=', '>', '?']
        char_list_4 = ['@', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O']
        char_list_5 = ['P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', '[', '\\', ']', '^', '_']
        char_list_6 = ['`', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o']
        char_list_7 = ['p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '{', '¦', '}', '~', '⌂']
        char_list_8 = ['Ç', 'ü', 'é', 'â', 'ä', 'à', 'å', 'ç', 'ê', 'ë', 'è', 'ï', 'î', 'ì', 'Ä', 'Å']
        char_list_9 = ['É', 'æ', 'Æ', 'ô', 'ö', 'ò', 'û', 'ù', 'ÿ', 'Ö', 'Ü', '¢', '£', '¥', '₧', 'ƒ']
        char_list_10 = ['á', 'í', 'ó', 'ú', 'ñ', 'Ñ', 'ª', 'º', '¿', '⌐', '¬', '½', '¼', '¡', '«', '»']
        char_list_11 = ['░', '▒', '▓', '│', '┤', '╡', '╢', '╖', '╕', '╣', '║', '╗', '╝', '╜', '╛', '┐']
        char_list_12 = ['└', '┴', '┬', '├', '─', '┼', '╞', '╟', '╚', '╔', '╩', '╦', '╠', '═', '╬', '╧']
        char_list_13 = ['╨', '╤', '╥', '╙', '╘', '╒', '╓', '╪', '╫', '┘', '┌', '█', '▄', '▌', '▐', '▀']
        char_list_14 = ['α', 'β', 'Γ', 'Π', 'Σ', 'σ', 'μ', 'τ', 'Φ', 'Θ', 'Ω', 'δ', '∞', 'φ', 'ε', '∩']
        char_list_15 = ['≡', '±', '≥', '≤', '⌠', '⌡', '÷', '≈', '˚', '•', '·', '√', 'ⁿ', '²', '■', ' ']
                
        char_array = np.array([char_list_0, char_list_1, char_list_2, char_list_3, char_list_4, char_list_5, char_list_6, char_list_7, \
                               char_list_8, char_list_9, char_list_10, char_list_11, char_list_12, char_list_13, char_list_14, char_list_15])
        return char_array
    
    def get_char_list(self, message):
#        char_list = []
#        if '/' not in message:
#            char_list.extend(message)
#        else:
#            count = 0
#            while( count<len(message)):
#                if message[count] != '/':
#                    char_list.append(message[count])
#                    count += 1
#                else:
#                    search = True
#                    for i in range(self.char_array.shape[0]):
#                        for j in range(self.char_array.shape[1]):
#                            
#                            if self.char_array[i, j] in message[count:] and self.char_array[i, j] != '/' and '/' in self.char_array[i, j]:
#                                if message[count:].index(self.char_array[i, j]) == 0:                                
#                                    char_list.append(self.char_array[i, j])
#                                    count += len(self.char_array[i, j])
#                                    search = False
#                                    break
#                    if search:
#                        char_list.append('/')
#                        count += 1
        char_list = list(message)             
        return char_list

    def get_cell_section(self, x, y, width, height):
        section = np.empty([height, width], dtype=dict)
        for i in range(height):
            for j in range(width):
                section[i, j] = self.get_cell(x + j, y + i).copy()
        return section
    
    def set_cell_section(self, x, y, sec):
        height = sec.shape[0]
        width = sec.shape[1]
        for i in range(height):
            for j in range(width):
                self.set_cell(x + j, y + i, sec[i, j])
    
class Flicker():
    def __init__(self, curses, flick_type=0, interval=1000):
        self.curses = curses
        self.flick_type = flick_type
        self.interval = interval
        self.initialization()
        
    def initialization(self):
        # Game config settings
        config = configparser.ConfigParser()
        config.read('config.ini')
        self.fps = int(config['WINDOW']['fps'])
        # Generate tick handler
        self.flick_states = 2
        self.sel_ind = 0
        self.tick = 0
    
    def load_cell(self, x, y):
        # Generate flick dictionary
        if self.flick_type == 0:
            flick = {'char' : ' ', 'foreground' : 'transparent', 'background' : 'transparent'}
        elif self.flick_type == 1:
            flick = self.curses.get_cell(x, y).copy()
            foreground = flick['foreground']
            background = flick['background']
            flick['foreground'] = background
            flick['background'] = foreground
        else:
            raise ValueError('No flicker type.')            
        self.flick_dict = {0 : self.curses.get_cell(x, y).copy(), 1 : flick}
    
    def update(self):
        self.tick += 1
        if self.tick >= self.fps*(self.interval/1000):
            self.sel_ind += 1
            self.sel_ind %= self.flick_states
            self.tick = 0
    
    def refresh(self , x, y):
        self.load_cell(x, y)
        self.curses.set_cell(x, y, self.flick_dict[self.sel_ind])