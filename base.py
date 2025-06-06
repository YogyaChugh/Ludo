import random
from exceptions import GameOver

class token:
    def __init__(self,player):
        if not self.player.isinstance(Player):
            raise GameOver("Bugs in the game guyz !")
        self.player = player
        self.current_loc = None

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
            self.color = random.choice(Player.colors_available)
            Player.colors_available -= self.color
        else:
            self.color = kwargs.get('color')
        

        if not kwargs.get('num_tokens'):
            self.num_tokens = 4
        else:
            self.num_tokens = kwargs.get('num_tokens')

        self.token_dict = {}
        for i in range(0,self.num_tokens):
            str(i)
            temp = token(self)
            self.token_dict[str(hash(temp))] = temp
            self.path = Path(self)

class Block:
    def __init__(self):
        self.safe = False
        self.personal = False

class Path:
    def __init__(self,player):
        self.player = player
        self.center_loc = 1

class Board:

    ## Every player got 18 recs
    def __init__(self,**kwargs):
        self.max_players = kwargs.get('max_players')

        if not self.max_players:
            raise GameOver("Bugs in the game guyz !")
        
        self.players = []
        for i in range(0,self.max_players):
            self.players.append(Player())