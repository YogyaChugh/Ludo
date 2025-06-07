class GameOver(Exception):
    def __init__(self,message):
        self.message = message
        super().__init__(self.message)
        

class DiceReachedEnd(Exception):
    def __init__(self,dice):
        self.message = "Dice Reached End !"
        self.dice = dice
        super().__init__(self.message)