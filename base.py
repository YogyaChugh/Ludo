import random
import flet as ft
import flet_lottie as fl
import copy
import math
import os
import base64
import asyncio
from exceptions import GameOver, DiceReachedEnd
try:
    from yaml import CLoader as Loader, CDumper as Dumper, load, dump
except ImportError:
    from yaml import Loader, Dumper, load, dump

class token:
    def __init__(self,player):
        if not isinstance(player, Player):
            raise GameOver("Bugs in the game guyz !")
        self.player = player
        self.home_block = None
        self.current_block = None
        self.gesture_cont = None

        self.hover_cont = None

        self.move_permitted = False
        self.reached_end = False

        self.page = None
    
    def __repr__(self):
        return str(self.player) + "\t" + str(hash(self)) + "\t" + str(self.home_block)

    async def move(self,e=None):
        disabled = False
        animation_allowed = True

        num = eval(os.environ.get('dice_num'))
        dimensions = eval(os.environ.get('dimensions'))
        if not self.move_permitted:
            print('Move not permitted !')
            return
        if self.home_block == self.current_block:
            num = 1
            animation_allowed = False
        a = self.current_block
        for i in range(0,num):
            if not a.next_block:
                disabled = True
            a = a.next_block
        if not disabled:
            for i in range(0,num):
                if self.current_block == self.player.color.last_path_block:
                    self.current_block = self.player.color.end_entry_block
                elif self.current_block.next_block == None:
                    raise DiceReachedEnd(self)
                else:
                    print('Moveed')
                    self.current_block = self.current_block.next_block
                    if not animation_allowed:
                        break
                    gesture_cont_top = dimensions[1] + self.current_block.location[1] + math.fabs(self.current_block.dimension[1] - self.image.height)//2
                    gesture_cont_left = dimensions[0] + self.current_block.location[0] + math.fabs(self.current_block.dimension[0] - self.image.width)//2
                    hover_cont_top = dimensions[1] + self.current_block.location[1] - (self.image.height*9)//10 + math.fabs(self.current_block.dimension[1] - self.image.height)//2
                    hover_cont_left = dimensions[0] + self.current_block.location[0] + math.fabs(self.current_block.dimension[0] - self.image.width)//2

                    vary_top_g = (gesture_cont_top - self.gesture_cont.top)/24
                    vary_left_g = (gesture_cont_left - self.gesture_cont.left)/24

                    vary_top_h = (hover_cont_top - self.hover_cont.top)/24
                    vary_left_h = (hover_cont_left - self.hover_cont.left)/24

                    temp_width_g = self.gesture_cont.content.width
                    temp_height_g = self.gesture_cont.content.height

                    temp_width_h = self.hover_cont.content.width
                    temp_height_h = self.hover_cont.content.height

                    for i in range(24):
                        self.gesture_cont.top = self.gesture_cont.top + vary_top_g
                        self.gesture_cont.left = self.gesture_cont.left + vary_left_g
                        self.hover_cont.top = self.hover_cont.top + vary_top_h
                        self.hover_cont.left = self.hover_cont.left + vary_left_h
                        if i%2!=0:
                            if i<12:
                                self.gesture_cont.top -= 1
                                self.gesture_cont.left -=1
                                self.hover_cont.top -=1
                                self.hover_cont.left -=1

                                self.gesture_cont.content.width +=1
                                self.gesture_cont.content.height +=1
                                self.hover_cont.content.width +=1
                                self.hover_cont.content.height +=1

                            else:
                                self.gesture_cont.top += 1
                                self.gesture_cont.left +=1
                                self.hover_cont.top +=1
                                self.hover_cont.left +=1

                                self.gesture_cont.content.width -=1
                                self.gesture_cont.content.height -=1
                                self.hover_cont.content.width -=1
                                self.hover_cont.content.height -=1

                        self.page.update()
                        await asyncio.sleep(0.005)
                await asyncio.sleep(0.1)

        self.gesture_cont.top = dimensions[1] + self.current_block.location[1] + math.fabs(self.current_block.dimension[1] - self.image.height)//2
        self.gesture_cont.left = dimensions[0] + self.current_block.location[0] + math.fabs(self.current_block.dimension[0] - self.image.width)//2

        self.hover_cont.top = dimensions[1] + self.current_block.location[1] - (self.image.height*9)//10 + math.fabs(self.current_block.dimension[1] - self.image.height)//2
        self.hover_cont.left = dimensions[0] + self.current_block.location[0] + math.fabs(self.current_block.dimension[0] - self.image.width)//2

        self.player.disable_movement_for_tokens()

        self.page.update()

    def nothing(self,e=None):
        return

    def create_token(self,image,image2,page):
        self.page = page

        if not self.current_block:
            raise GameOver("Token Image created before setting actual position on board !")
        self.image = copy.deepcopy(image)
        self.hover_image = copy.deepcopy(image2)

        dimensions = eval(os.environ.get('dimensions'))

        self.gesture_cont = ft.GestureDetector(
            mouse_cursor = ft.MouseCursor.CLICK,
            on_tap = self.nothing,
            content = self.image,
            top = dimensions[1] + self.current_block.location[1] + math.fabs(self.current_block.dimension[1] - self.image.height)//2,
            left = dimensions[0] + self.current_block.location[0] + math.fabs(self.current_block.dimension[0] - self.image.width)//2,
        )

        self.hover_cont = ft.GestureDetector(
            mouse_cursor = ft.MouseCursor.CLICK,
            on_tap = self.nothing,
            content = self.hover_image,
            top = dimensions[1] + self.current_block.location[1] - (self.image.height*9)//10 + math.fabs(self.current_block.dimension[1] - self.image.height)//2,
            left = dimensions[0] + self.current_block.location[0] + math.fabs(self.current_block.dimension[0] - self.image.width)//2,
        )

        return (self.gesture_cont,self.hover_cont)
class Player:
    num = 0
    dice = None
    def __init__(self,**kwargs):
        if not kwargs.get('name'):
            self.name = f"Player {Player.num+1}"
            Player.num += 1
        else:
            self.name = kwargs.get('name')

        if not kwargs.get('num_tokens'):
            self.num_tokens = 4
        else:
            self.num_tokens = kwargs.get('num_tokens')

        self.tokens = []
        self.color = None
        for i in range(0,self.num_tokens):
            str(i)
            temp = token(self)
            self.tokens.append(temp)
    
    def associate_color(self,color):
        self.color = color
        num = 0
        for i in self.tokens:
            i.home_block = color.home_blocks[num]
            i.current_block = color.home_blocks[num]
            num += 1

    def disable_movement_for_tokens(self):
        if not self.dice:
            raise GameOver('Bugs in the game guyz !')
        self.dice.cont.on_tap = self.dice.roll
        for i in self.tokens:
            i.move_permitted = False
            i.gesture_cont.on_tap = i.nothing
            i.hover_cont.on_tap = i.nothing
        
        self.dice.page.update()
    
    def __str__(self):
        return self.name

class Color:
    color = None
    home_blocks = []
    start_block = None
    last_path_block = None
    end_entry_block = None

    def __init__(self,color):
        self.color = color
    
    def __repr__(self):
        str1 = f"------- Color: {self.color} -------\nHome Blocks: \n"
        for i in self.home_blocks:
            str1 += " - " + str(i) + "\n"
        str1 += f"Start Block: {self.start_block}\n"
        str1 += f"Last Path Block: {self.last_path_block}\n"
        str1 += f"End Entry Block: {self.end_entry_block}\n"
        return str1
    
    def __str__(self):
        str1 = f"------- Color: {self.color} -------\nHome Blocks: \n"
        for i in self.home_blocks:
            str1 += " - " + str(i) + "\n"
        str1 += f"Start Block: {self.start_block}\n"
        str1 += f"Last Path Block: {self.last_path_block}\n"
        str1 += f"End Entry Block: {self.end_entry_block}\n"
        return str1

class Block:
    def __init__(self,location=[None,None],dimension=[None,None],prev_block=None,next_block=None,safe=False,colors_allowed=[]):
        self.location = location
        self.dimension = dimension
        self.prev_block = prev_block
        self.next_block = next_block
        self.safe = safe
        self.colors_allowed = colors_allowed
    
    def __repr__(self):
        return f"Hash: {hash(self)} | Loc: {self.location} | Dims: {self.dimension} | Safe: {self.safe} | Colors: {self.colors_allowed}"
    
    def __str__(self):
        return f"Hash: {hash(self)} | Loc: {self.location} | Dims: {self.dimension} | Safe: {self.safe} | Colors: {self.colors_allowed}"


class Board:
    ## Every player got 18 recs
    def __init__(self,file_loc):
        with open(file_loc) as file:
            data = load(file,Loader=Loader)

        self.data = data

        if not self.data:
            raise GameOver("Bugs in the game guyz !")

        self.max_players = data.get('max_players')
        self.min_players = data.get('min_players')
        self.width = data.get('board_width')
        self.height = data.get('board_height')
        self.block_width = data.get('block_width')
        self.block_height = data.get('block_height')
        self.dice_base_width = data.get('dice_base_width')
        self.dice_base_height = data.get('dice_base_height')

        self.colors = {}

        for i in data.get('colors'):
            self.colors[i] = Color(i)

        start_locs = {}
        for i in data.get('start_positions'):
            start_locs[i] = [data.get('start_positions').get(i).get('x'), data.get('start_positions').get(i).get('y')]
        
        end_locs = {}
        for i in data.get('end_positions'):
            end_locs[i] = [data.get('end_positions').get(i).get('x'), data.get('end_positions').get(i).get('y')]

        safe_locs = []
        for i in data.get('other_safe_positions'):
            safe_locs.append([i.get('x'),i.get('y')])
                
        total = len(data.get('rest_paths'))
        count = 1
        beg_block = None
        temp_prev = None
        for i in data.get('rest_paths'):
            start = i.get('start')
            advance = i.get('advance')
            b_count = 1
            for p in range(0,i.get('num_continue')):
                x_pos = start.get('x') + advance.get('x')*p
                y_pos = start.get('y') + advance.get('y')*p
                tb = Block([x_pos, y_pos], [data.get('block_width'),data.get('block_height')], temp_prev, None, True if ([x_pos,y_pos] in list(start_locs.values()) or [x_pos,y_pos] in safe_locs) else False, list(self.colors.keys()))
                if temp_prev:
                    temp_prev.next_block = tb
                if not beg_block:
                    beg_block = tb
                if count==total and b_count==i.get('num_continue'):
                    beg_block.prev_block = tb
                    tb.next_block = beg_block
                for i in self.colors:
                    if [x_pos,y_pos] == end_locs.get(i):
                        self.colors[i].last_path_block = tb
                    if [x_pos,y_pos] == start_locs.get(i):
                        self.colors[i].start_block = tb
                b_count +=1
                temp_prev = tb
            count +=1

        for i in data.get('win_positions'):
            temp_prev = None
            start = data.get('win_positions').get(i).get('start')
            advance = data.get('win_positions').get(i).get('advance')
            b_count = 1
            for p in range(0,data.get('win_positions').get(i).get('num_continue')):
                x_pos = start.get('x') + advance.get('x')*p
                y_pos = start.get('y') + advance.get('y')*p
                tb = Block([x_pos, y_pos], [data.get('block_width'),data.get('block_height')], temp_prev, None, True, i)
                if temp_prev:
                    temp_prev.next_block = tb
                if b_count==1:
                    self.colors[i].end_entry_block = tb
                b_count += 1
                temp_prev = tb

        for i in data.get('base_positions'):
            if i in self.colors:
                temp = data.get('base_positions').get(i)
                temp_home_locs = []
                for k in temp:
                    tb = Block([k.get('x'), k.get('y')], [data.get('block_width'),data.get('block_height')], None, self.colors.get(i).start_block, True, i)
                    temp_home_locs.append(tb)
                self.colors[i].home_blocks = temp_home_locs

class Dice:
    player_associated = None
    number = None

    def __init__(self,position,dimension,page):
        self.page = page
        with open('assets/dice_1.json','r',encoding='utf-8') as file:
            data = file.read()
        based = base64.b64encode(data.encode('utf-8')).decode('utf-8')
        self.lottie = ft.Lottie(src_base64=based,repeat = False)
        self.cont = ft.GestureDetector(
            content = self.lottie,
            mouse_cursor=ft.MouseCursor.CLICK,
            on_tap = self.nothing,
            left = position[0],
            top = position[1],
            width = dimension[0],
            height = dimension[1]
        )
        self.page.update()

    def nothing(self,e=None):
        return

    def roll(self,e=None):
        print('ROLL CALLED ! ')
        if not self.player_associated:
            raise GameOver("Bugs in the game guyz !")
        self.number = random.randint(1,6)
        with open(f"assets/dice_{self.number}.json",'r',encoding='utf-8') as file:
            data = file.read()
        based = base64.b64encode(data.encode('utf-8')).decode('utf-8')
        self.lottie.src_base64 = based 
        self.cont.content = self.lottie
        self.page.update()
        os.environ['dice_num'] = str(self.number)
        for i in self.player_associated.tokens:
            if self.number == 6:
                if not i.reached_end:
                    i.move_permitted = True
                    i.gesture_cont.on_tap = i.move
                    i.hover_cont.on_tap = i.move
                    self.cont.on_tap = self.nothing
            else:
                if not i.reached_end and i.home_block != i.current_block:
                    i.move_permitted = True
                    i.gesture_cont.on_tap = i.move
                    i.hover_cont.on_tap = i.move
                    self.cont.on_tap = self.nothing
                    self.page.update()
        if self.number != 6:
            players = self.page.session.get('players')
            self.associate_player(players[(players.index(self.player_associated) + 1)%len(players)])
        return self.number
    
    def associate_player(self,player):
        print('DICE ASSOCIATED TO ',str(player))
        self.player_associated = player
        player.dice = self