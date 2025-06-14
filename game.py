import exceptions
import random
import copy
import base
import flet as ft
import os
try:
    from yaml import CLoader as Loader, CDumper as Dumper, load, dump
except ImportError:
    from yaml import Loader, Dumper, load, dump

class Game:
    num_players = 2
    board_yaml = "assets/board_4.yaml"
    def __init__(self,page,num_players):
        self.page = page
        self.view = ft.View()
        self.page.views.append(self.view)
        self.view.padding = 0
        if num_players:
            self.num_players = int(num_players)

    async def game(self,e=None):
        self.page.session.set('game_running',True)

        # Load File
        try:
            with open(self.board_yaml,'r') as file:
                data = load(file,Loader)
        except Exception as e:
            raise exceptions.GameOver(f"File loading Failed:\n-------------------------\nFile: {self.board_yaml}\n{e.args[1]}")
        self.page.session.set('data',data) # Set in session so as to be used in base.py

        # Fetch the screen dimensions for mobile ! For desktop, its fixed in main function
        if self.page.platform == ft.PagePlatform.ANDROID or self.page.platform == ft.PagePlatform.IOS:
            w = self.page.width  # These values are read-only in flet
            h = self.page.height
        else:
            w = self.page.window.width
            h = self.page.window.height

        board_w = data.get('board_width')
        board_h = data.get('board_height')
        if not board_w or not board_h or not data.get('min_players') or not data.get('max_players'):
            raise exceptions.GameOver(f"Game File Corrupt ! File: {self.board_yaml}")

        self.page.session.set('scale',1) # Normal Scale

        # If screen dimensions are less than the board dimensions
        # mentioned in the game '.json' files, then reduce the scale to half
        while (w - board_w)<0 or (h - board_h)<0:
            self.page.session.set('scale',self.page.session.get('scale')/2)
            board_w = board_w*self.page.session.get('scale')
            board_h = board_h*self.page.session.get('scale')

        scale = self.page.session.get('scale') # Used everywhere in this function !
        # Calculate board dimensions based on screen dimensions
        cal_x = (w - board_w)//2
        cal_y = (h - board_h)//2
        print("x: ",cal_x,'y: ',cal_y)
        os.environ['dimensions'] = str((cal_x, cal_y))

        # IMAGES

        #Check first
        list_of_images = [data.get('bg_image'),data.get('asset_board'),data.get('asset_dice_base')]
        try:
            for i in range(0,len(list_of_images)):
                current='assets/' + list_of_images[i]
                open(current)
        except Exception as e:
            raise exceptions.GameOver(f"File loading Failed:\n-------------------------\nFile: {current}\n{e.args[1]}")

        # Background Image
        bgimg = ft.Container(
            image = ft.DecorationImage(data.get('bg_image'), fit = ft.ImageFit.COVER, opacity=0.5),
            expand = True
        )

        # Board Image
        img = ft.Image(
            data.get('asset_board'),
            fit=ft.ImageFit.FILL,
            width = board_w,
            height = board_h
        )

        # Soon I will compile these missing error checks in one function !
        if not data.get('asset_dice_base') or not data.get('dice_base_width') or not data.get('dice_base_height') or not data.get('tokens') or not data.get('frames'):
            raise exceptions.GameOver(f"Game File Corrupt ! File: {self.board_yaml}")

        # Base of Every Token - It's same for all color tokens
        dice_img = ft.Image(
            data.get('asset_dice_base'),
            width = data.get('dice_base_width')*scale,
            height = data.get('dice_base_height')*scale
        )

        # Main Board
        main_board = ft.Container(img,left=cal_x,top=cal_y)
        cont = ft.Stack([main_board])   # Stack for all objects !


        # Creating the board which generates all blocks and other stuff in the form of objects
        board = base.Board(self.board_yaml)

        colors_left = copy.deepcopy(board.colors) # Stores the colors left on the board (based on number of players playing)
        players = []
        if self.num_players<data.get('min_players') or self.num_players>data.get('max_players'):
            raise exceptions.GameOver(f"\n-------------------------\nMinimum Number of players for board: {data.get('min_players')}\nMaximum Number of players for board: {data.get('max_players')}\nCurrent Number: {self.num_players}")
        prev = 0

        self.page.session.set('tokens',{}) # This will simultaneously store locations of each token on board !

        # Dice for the match
        dice = base.Dice([cal_x + board_w//2 - 28*scale, cal_y + board_h + 20*scale],self.page,data)

        for i in range(0,self.num_players):
            # If player_number is even (starts from 0), then randomly color is chosen
            # Else, the color diagnolly opposite to the previously randomly chosen color
            # is chosen !
            if i % 2 == 0:
                a = random.choice(list(colors_left.keys()))
                prev = list(board.colors.keys()).index(a)
                players.append(base.Player(self.page,self.view,color = colors_left[a]))
            else:
                a = list(board.colors.keys())[len(list(board.colors.keys())) - 1 - prev]
                players.append(base.Player(self.page,self.view,color = colors_left[a]))
            colors_left.pop(a)

            # Loops in all tokens, creating hover images (diff for each color)
            # and base images (the circle at bottom) with gesture containers to allow clicking tokens !
            for j in players[-1].tokens:
                hover_image = ft.Image(
                    f'token_{players[-1].color.color}.png',
                    width = data.get('tokens')['w']*scale,
                    height = data.get('tokens')['h']*scale
                )
                container1, container2 = j.create_token(dice_img,hover_image)
                cont.controls.append(container1)
                cont.controls.append(container2)

            # Creates the frame for each player playing !
            color = players[-1].color.color
            frames = data.get('frames')
            player_frame = ft.Image(
                f"frame_{color}.jpg",
                width = frames[color]['w']*scale,
                height = frames[color]['h']*scale,
                top = cal_y + frames[color]['y']*scale,
                left = cal_x + frames[color]['x']*scale
            )
            players[-1].frame = player_frame
            cont.controls.append(players[-1].frame) # This is the whole frame shown !
            self.page.update()

        cont.controls.append(dice.dice_image) # The dice in real !
        # need to do this dice image just before the gesture container
        for i in players:
            # This is different from the frame shown, as it is only the part
            # where dice will be shown with the gesture controller so as to allow
            # click/touch events !
            cont.controls.append(i.frame_cont)
            self.page.update()

        # All players !
        players_playing = players
        self.page.session.set('players',players_playing)
        self.page.session.set('won_list',[])

        # the back button
        back = ft.Image(
            "back.png",
            width = data.get('block_width')*1.5,
            height = data.get('block_height')*1.5
        )
        def back_to_the_main(e=None):
            temp_store = self.page.views.pop()
            self.page.update()
            return
        back_gesture = ft.GestureDetector(
            mouse_cursor=ft.MouseCursor.CLICK,
            content=back,
            on_tap = back_to_the_main,
            width = data.get('block_width')*1.5,
            height = data.get('block_height')*1.5,
            top = 20,
            left = 20
        )
        cont.controls.append(back_gesture)

        # Adds all contents to the bgimg to display with the background image !
        bgimg.content = cont
        self.view.controls.append(bgimg)

        # Initializes the game play
        player_in_turn = random.choice(players)
        dice.associate_player(player_in_turn) # Very Important else GameOver error (check roll method of Dice class in base.py)
        dice.update_dice_locs()     # Update dice locs based on the player in turn
        player_in_turn.frame_cont.on_tap = dice.roll    # Allow rolling the dice when dice is clicked !
        self.page.update()