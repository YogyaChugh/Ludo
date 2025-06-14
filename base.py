import random
import flet as ft
import flet_lottie as fl
import copy
import math
import os
import asyncio
import base64
from exceptions import GameOver, PlayerReachedEnd
try:
    from yaml import CLoader as Loader, CDumper as Dumper, load, dump
except ImportError:
    from yaml import Loader, Dumper, load, dump

class token:
    def __init__(self,player,page):
        if not isinstance(player, Player):
            raise GameOver("Bugs in the game guyz !")
        self.player = player
        self.home_block = None
        self.current_block = None
        self.gesture_cont = None

        self.hover_cont = None

        self.move_permitted = False
        self.reached_end = False

        self.page = page
    
    def __repr__(self):
        return str(self.player) + "\t" + str(hash(self)) + "\t" + str(self.home_block)

    async def move(self,e=None):
        self.gesture_cont.on_tap = self.nothing
        self.hover_cont.on_tap = self.nothing
        disabled = False
        animation_allowed = True

        scale = self.page.session.get('scale')

        num = eval(os.environ.get('dice_num'))
        dimensions = eval(os.environ.get('dimensions'))
        if not self.move_permitted:
            return
        if self.home_block == self.current_block:
            num = 1
            animation_allowed = False
        a = self.current_block
        if not disabled:
            for i in range(0,num):
                print('-------------------------------')
                print('Player: ',self.player.color.color)
                print('Blocks:')
                print("Current: ",self.current_block.location)
                print("Next: ",self.current_block.next_block.location)
                if self.current_block == self.player.color.last_path_block:
                    self.current_block = self.player.color.end_entry_block
                else:
                    self.current_block = self.current_block.next_block
                    if not animation_allowed:
                        break
                    gesture_cont_top = dimensions[1] + self.current_block.location[1]*scale + math.fabs(self.current_block.dimension[1]*scale - self.image.height)//2
                    gesture_cont_left = dimensions[0] + self.current_block.location[0]*scale + math.fabs(self.current_block.dimension[0]*scale - self.image.width)//2
                    hover_cont_top = dimensions[1] + self.current_block.location[1]*scale - (self.image.height*9)//10 + math.fabs(self.current_block.dimension[1]*scale - self.image.height)//2
                    hover_cont_left = dimensions[0] + self.current_block.location[0]*scale + math.fabs(self.current_block.dimension[0]*scale - self.image.width)//2

                    vary_top_g = (gesture_cont_top - self.gesture_cont.top)/(self.page.session.get('data').get('block_height')*scale)
                    vary_left_g = (gesture_cont_left - self.gesture_cont.left)/(self.page.session.get('data').get('block_width')*scale)

                    vary_top_h = (hover_cont_top - self.hover_cont.top)/(self.page.session.get('data').get('block_height')*scale)
                    vary_left_h = (hover_cont_left - self.hover_cont.left)/(self.page.session.get('data').get('block_width')*scale)
                    for i in range(24):
                        self.gesture_cont.top = self.gesture_cont.top + vary_top_g
                        self.gesture_cont.left = self.gesture_cont.left + vary_left_g
                        self.hover_cont.top = self.hover_cont.top + vary_top_h
                        self.hover_cont.left = self.hover_cont.left + vary_left_h
                        if i%2!=0:
                            if i<12:
                                self.gesture_cont.top -= 1*scale
                                self.gesture_cont.left -=1*scale
                                self.hover_cont.top -=1*scale
                                self.hover_cont.left -=1*scale

                                self.gesture_cont.content.width +=1*scale
                                self.gesture_cont.content.height +=1*scale
                                self.hover_cont.content.width +=1*scale
                                self.hover_cont.content.height +=1*scale

                            else:
                                self.gesture_cont.top += 1*scale
                                self.gesture_cont.left +=1*scale
                                self.hover_cont.top +=1*scale
                                self.hover_cont.left +=1*scale

                                self.gesture_cont.content.width -=1*scale
                                self.gesture_cont.content.height -=1*scale
                                self.hover_cont.content.width -=1*scale
                                self.hover_cont.content.height -=1*scale

                        self.page.update()
                        await asyncio.sleep(0.002)
                await asyncio.sleep(0.1)
                try:
                    print('THE NEXT BLOCK TO THE NEW CURRENT: ',self.current_block.next_block.location)
                except Exception:
                    print('THE NEXT BLOCK TO THE NEW CURRENT: ',self.current_block.next_block)

        temp = self.page.session.get('tokens')
        player_cutted_baby = False
        for p in temp:
            if self.current_block == temp[p] and not temp[p].safe and not p.player==self.player:
                temp[p] = p.home_block
                player_cutted_baby = True
                await p.return_home()
        
        temp[self] = self.current_block
        self.page.session.set('tokens',temp)

        self.gesture_cont.top = dimensions[1] + self.current_block.location[1]*scale + math.fabs(self.current_block.dimension[1]*scale - self.image.height)//2
        self.gesture_cont.left = dimensions[0] + self.current_block.location[0]*scale + math.fabs(self.current_block.dimension[0]*scale - self.image.width)//2

        self.hover_cont.top = dimensions[1] + self.current_block.location[1]*scale - (self.image.height*9)//10 + math.fabs(self.current_block.dimension[1]*scale - self.image.height)//2
        self.hover_cont.left = dimensions[0] + self.current_block.location[0]*scale + math.fabs(self.current_block.dimension[0]*scale - self.image.width)//2

        if self.current_block.next_block == None:
            print('Boy the next to next move is None')
            self.reached_end = True
            self.player.reached_end(self)
            self.player.disable_movement_for_tokens(True)
        elif player_cutted_baby:
            self.player.disable_movement_for_tokens(True)
        else:
            self.player.disable_movement_for_tokens(False)

        self.page.update()

    def nothing(self,e=None):
        return
    
    async def return_home(self):
        dimensions = eval(os.environ.get('dimensions'))
        while self.current_block != self.player.color.start_block:
            self.current_block = self.current_block.prev_block
            scale = self.page.session.get('scale')
            self.gesture_cont.top = dimensions[1] + self.current_block.location[1]*scale + math.fabs(self.current_block.dimension[1]*scale - self.image.height)//2
            self.gesture_cont.left = dimensions[0] + self.current_block.location[0]*scale + math.fabs(self.current_block.dimension[0]*scale - self.image.width)//2

            self.hover_cont.top = dimensions[1] + self.current_block.location[1]*scale - (self.image.height*9)//10 + math.fabs(self.current_block.dimension[1]*scale - self.image.height)//2
            self.hover_cont.left = dimensions[0] + self.current_block.location[0]*scale + math.fabs(self.current_block.dimension[0]*scale - self.image.width)//2

            self.page.update()

            await asyncio.sleep(0.037)
            
        self.current_block = self.home_block

        self.gesture_cont.top = dimensions[1] + self.current_block.location[1]*scale + math.fabs(self.current_block.dimension[1]*scale - self.image.height)//2
        self.gesture_cont.left = dimensions[0] + self.current_block.location[0]*scale + math.fabs(self.current_block.dimension[0]*scale - self.image.width)//2
        self.hover_cont.top = dimensions[1] + self.current_block.location[1]*scale - (self.image.height*9)//10 + math.fabs(self.current_block.dimension[1]*scale - self.image.height)//2
        self.hover_cont.left = dimensions[0] + self.current_block.location[0]*scale + math.fabs(self.current_block.dimension[0]*scale - self.image.width)//2

        self.page.update()

    def create_token(self,image,image2):

        a = self.page.session.get('tokens')
        a[self] = self.current_block
        self.page.session.set('tokens',a)

        if not self.current_block:
            raise GameOver("Token Image created before setting actual position on board !")
        self.image = copy.deepcopy(image)
        self.hover_image = copy.deepcopy(image2)

        dimensions = eval(os.environ.get('dimensions'))

        scale = self.page.session.get('scale')

        self.gesture_cont = ft.GestureDetector(
            mouse_cursor = ft.MouseCursor.CLICK,
            on_tap = self.nothing,
            content = self.image,
            top = dimensions[1] + self.current_block.location[1]*scale + math.fabs(self.current_block.dimension[1]*scale - self.image.height)//2,
            left = dimensions[0] + self.current_block.location[0]*scale + math.fabs(self.current_block.dimension[0]*scale - self.image.width)//2,
        )

        self.hover_cont = ft.GestureDetector(
            mouse_cursor = ft.MouseCursor.CLICK,
            on_tap = self.nothing,
            content = self.hover_image,
            top = dimensions[1] + self.current_block.location[1]*scale - (self.image.height*9)//10 + math.fabs(self.current_block.dimension[1]*scale - self.image.height)//2,
            left = dimensions[0] + self.current_block.location[0]*scale + math.fabs(self.current_block.dimension[0]*scale - self.image.width)//2,
        )

        return (self.gesture_cont,self.hover_cont)
class Player:
    num = 0
    dice = None
    frame = None

    def __init__(self,page,**kwargs):
        self.page = page

        self.data = self.page.session.get('data')
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
        self.finished_tokens = []
        for i in range(0,self.num_tokens):
            str(i)
            temp = token(self,page)
            self.tokens.append(temp)

        if not kwargs.get('color'):
            self.color = None
        else:
            self.associate_color(kwargs.get('color'))

        dimensions = eval(os.environ.get('dimensions'))
        scale=page.session.get('scale')

        self.frame_cont = ft.GestureDetector(
            mouse_cursor=ft.MouseCursor.CLICK,
            disabled=True,
            on_tap = self.nothing,
            left = dimensions[0] + self.data['frames'][self.color.color]['x']*scale + self.data['dice']['x']*scale,
            top = dimensions[1] + self.data['frames'][self.color.color]['y']*scale + self.data['dice']['y']*scale,
            width = self.data['dice']['w']*scale,
            height = self.data['dice']['h']*scale
        )
        self.page.update()

    def set_player_won(self):
        for i in self.tokens:
            i.gesture_cont.visible = False
            i.hover_cont.visible = False
            self.page.update()
        with open('assets/won_1st.json','r',encoding='utf-8') as file:
            data_json = file.read()
        bsdata = base64.b64encode(data_json.encode('utf-8')).decode('utf-8')

        dimensions = self.page.session.get('dimensions')
        scale = self.page.session.get('scale')
        came_first = fl.Lottie(
            src_base64=bsdata,
            width = (6*self.data.get('block_width')*scale)//2,
            height = (6*self.data.get('block_height')*scale)//2,
            top = dimensions[0] + (6 * self.data.get('block_height')*scale)//4,
            left = dimensions[1] + (6 * self.data.get('block_width')*scale)//4
        )
        self.page.add(came_first)
        self.page.update()
        

    def reached_end(self,token):
        self.finished_tokens.append(token)
        print('-------------------------------')
        print('Player: ',self.color.color)
        print('reached end !')
        print('total reached end: ',len(self.finished_tokens))
        if len(self.finished_tokens)==4:
            a = self.page.session.get('players')
            a.remove(self)
            self.page.session.set('players',a)

            b = self.page.session.get('won_list')
            b.append(self)
            self.page.session.set('won_list',b)
            play = self.page.session.get('players')
            self.set_player_won()
            if len(b) == len(play) - 1:
                raise GameOver('DUDE THE GAME IS OVER !')
            self.page.update()
    
    def associate_color(self,color):
        self.color = color
        num = 0
        for i in self.tokens:
            i.home_block = color.home_blocks[num]
            i.current_block = color.home_blocks[num]
            num += 1

    def disable_movement_for_tokens(self,allow_again):
        if not self.dice:
            raise GameOver('Bugs in the game guyz !')

        for i in self.tokens:
            i.move_permitted = False
            i.gesture_cont.on_tap = i.nothing
            i.hover_cont.on_tap = i.nothing

        if self.dice.number!=6 and not allow_again:
            players = self.dice.page.session.get('players')
            self.dice.associate_player(players[(players.index(self.dice.player_associated) + 1)%len(players)])
        else:
            self.frame_cont.on_tap = self.dice.roll
        
        self.dice.page.update()
    
    def __str__(self):
        return self.name
    
    def nothing(self,e=None):
        return

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
    number = 1
    cont = []

    def __init__(self,position,page,data):
        self.page = page

        self.data = data
        scale = page.session.get('scale')

        self.dice_image = ft.Image(
            "dice_1.jpg",
            width=data['dice']['w']*scale,
            height=data['dice']['h']*scale,
            gapless_playback=True,
        )
        self.page.update()

    def nothing(self,e=None):
        return

    async def roll(self,e=None):
        if not self.player_associated:
            raise GameOver("Bugs in the game guyz !")
        self.number = random.randint(1,6)
        await self.animate_and_display_num()
        self.page.update()
        os.environ['dice_num'] = str(self.number)
        num = 0
        lasti = None
        locs_w = []
        locs_h = []
        for i in self.player_associated.tokens:
            t = i.current_block
            done = False
            for j in range(0,self.number):
                if t.next_block:
                    t = t.next_block
                else:
                    done = True
                    break
            if done:
                continue
            if self.number == 6:
                if not i.reached_end:
                    locs_w.append(i.current_block.location[0])
                    locs_h.append(i.current_block.location[1])
                    num +=1
                    lasti = i
                    i.move_permitted = True
                    i.gesture_cont.on_tap = i.move
                    i.hover_cont.on_tap = i.move
                    self.player_associated.frame_cont.on_tap = self.nothing
            else:
                if not i.reached_end and i.home_block != i.current_block:
                    locs_w.append(i.current_block.location[0])
                    locs_h.append(i.current_block.location[1])
                    num +=1
                    lasti = i
                    i.move_permitted = True
                    i.gesture_cont.on_tap = i.move
                    i.hover_cont.on_tap = i.move
                    self.player_associated.frame_cont.on_tap = self.nothing
                    self.page.update()
        if num==1:
            lasti.gesture_cont.on_tap = lasti.nothing
            lasti.hover_cont.on_tap = lasti.nothing
            self.page.update()
            await asyncio.sleep(0.4)
            await lasti.move()
        if len(set(locs_w))==1 and len(set(locs_h))==1:
            await asyncio.sleep(0.4)
            await lasti.move()
        if num==0:
            self.player_associated.frame_cont.on_tap = self.nothing
            await asyncio.sleep(1)
            players = self.page.session.get('players')
            self.associate_player(players[(players.index(self.player_associated) + 1)%len(players)])
        players = self.page.session.get('players')

        return self.number
    
    def associate_player(self,player):
        if self.player_associated:
            self.player_associated.frame_cont.disabled = True
        self.player_associated = player
        player.dice = self
        player.frame_cont.disabled = False
        player.frame_cont.on_tap = self.roll
        self.page.update()
        self.update_dice_locs()

    def update_dice_locs(self):
        scale = self.page.session.get('scale')
        self.dice_image.top = self.player_associated.frame.top + self.data['dice']['y']*scale
        self.dice_image.left = self.player_associated.frame.left + self.data['dice']['x']*scale
        self.page.update()

    async def animate_and_display_num(self):
        for i in range(1,7):
            self.dice_image.src = f"dice_roll_images/{i}.jpg"
            self.page.update()
            await asyncio.sleep(0.1)
        self.dice_image.src = f"dice_{self.number}.jpg"
        self.page.update()