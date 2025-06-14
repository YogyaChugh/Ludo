class GameOver(Exception):
    def __init__(self,message):
        self.message = message
        self.extras = {}
        super().__init__(self.message)
        

class PlayerReachedEnd(Exception):
    def __init__(self,player):
        self.message = "Player Reached End !"
        self.player = player
        super().__init__(self.message)