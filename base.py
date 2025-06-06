import random
from exceptions import GameOver
try:
    from yaml import CLoader as Loader, CDumper as Dumper, load, dump
except ImportError:
    from yaml import Loader, Dumper, load, dump

class token:
    def __init__(self,player):
        if not self.player.isinstance(Player):
            raise GameOver("Bugs in the game guyz !")
        self.player = player
        self.home_block = None
        self.current_block = None

class Player:
    num = 0
    colors_available = []
    def __init__(self,**kwargs):
        if not kwargs.get('name'):
            self.name = f"Player {Player.num+1}"
            Player.num += 1
        else:
            self.name = kwargs.get('name')
        
        if not kwargs.get('color'):
            self.display_color = random.choice(Player.colors_available)
            Player.colors_available -= self.display_color
        else:
            self.display_color = kwargs.get('color')
        

        if not kwargs.get('num_tokens'):
            self.num_tokens = 4
        else:
            self.num_tokens = kwargs.get('num_tokens')

        self.token_dict = {}
        for i in range(0,self.num_tokens):
            str(i)
            temp = token(self)
            self.token_dict[str(hash(temp))] = temp
    
    def associate_color(self,color):
        self.color = color
        num = 0
        for i in self.token_dict.values():
            i.home_block = color.home_blocks[num]
            i.current_block = color.home_blocks[num]
            num += 1

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

        for i in data.get('base_positions'):
            if i in self.colors:
                temp = data.get('base_positions').get(i)
                temp_home_locs = []
                for k in temp:
                    tb = Block([k.get('x'), k.get('y')], [data.get('block_width'),data.get('block_height')], None, None, True, i)
                    temp_home_locs.append(tb)
                self.colors[i].home_blocks = temp_home_locs

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
        for i in data.get('rest_paths'):
            temp_prev = None
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
