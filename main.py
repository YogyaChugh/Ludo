import flet as ft
import base
import asyncio
import copy
import os
import exceptions
import random
try:
    from yaml import CLoader as Loader, CDumper as Dumper, load, dump
except ImportError:
    from yaml import Loader, Dumper, load, dump


async def game(page,board_yaml_file):

    page.session.set('game_running',True)

    # Load File
    with open(board_yaml_file,'r') as file:
        data = load(file,Loader)


    # Calculate board dimensions based on screen dimensions
    if page.platform == ft.PagePlatform.ANDROID or page.platform == ft.PagePlatform.IOS:
        w = page.width
        h = page.height
    else:
        w = page.window.width
        h = page.window.height


    board_w = data.get('board_width')
    board_h = data.get('board_height')
    cal_x = (w - board_w)//2
    cal_y = (h - board_h)//2
    os.environ['dimensions'] = str((cal_x, cal_y))

    # Background Image
    bgimg = ft.Container(
        image = ft.DecorationImage("https://raw.githubusercontent.com/YogyaChugh/Ludo/master/assets/" + data.get('bg_image'), fit = ft.ImageFit.COVER, opacity=0.7),
        expand = True
    )

    # Board Image
    img = ft.Image(
        "https://raw.githubusercontent.com/YogyaChugh/Ludo/master/assets/" + data.get('asset_board'),
        fit=ft.ImageFit.FILL
    )


    # Base of Every Token
    dice_img = ft.Image(
        "https://raw.githubusercontent.com/YogyaChugh/Ludo/master/assets/" + data.get('asset_dice_base'),
        width = data.get('dice_base_width'),
        height = data.get('dice_base_height')
    )

    # Main Board & Stack
    main_board = ft.Container(img,left=cal_x,top=cal_y)
    cont = ft.Stack([main_board])


    # Creating classes from base.py
    # Board, all players, tokens, colors, and blocks !
    board = base.Board(board_yaml_file)
    colors_left = copy.deepcopy(board.colors)
    players = []
    num_players = eval(os.environ.get('num_players'))
    if num_players<data.get('min_players') or num_players>data.get('max_players'):
        raise exceptions.GameOver("Bugs in the game guyz !")
    prev = 0

    # Randomizing color selection for players
    for i in range(0,num_players):
        players.append(base.Player())
        if i % 2 == 0:
            a = random.choice(list(colors_left.keys()))
            prev = list(board.colors.keys()).index(a)
            players[-1].associate_color(colors_left[a])
            colors_left.pop(a)
        else:
            a = list(board.colors.keys())[len(list(board.colors.keys())) - 1 - prev]
            players[-1].associate_color(colors_left[a])
            colors_left.pop(a)

    page.session.set('players',players)
    page.session.set('tokens',{})

    # Generating Player tokens and handling click events
    for i in players:
        for j in i.tokens:
            hover_image = ft.Image(
                f'https://raw.githubusercontent.com/YogyaChugh/Ludo/master/assets/token_{i.color.color}.png',
                width = 22,
                height = 30
            )
            container1, container2 = j.create_token(dice_img,hover_image,page)
            cont.controls.append(container1)
            cont.controls.append(container2)
    page.update()

    dice = base.Dice([cal_x + board_w//2 - 28, cal_y + board_h + 20],[50,50],page)
    
    pl = ft.Text('None',size=30,left = cal_x + board_w//2 - 15, top = cal_y + board_h + 85)
    cont.controls.append(dice.cont)
    cont.controls.append(dice.lottie2)

    player_frame = ft.Image(
        "https://raw.githubusercontent.com/YogyaChugh/Ludo/master/assets/frame.jpg",
        width = 115,
        height = 57.5,
        top = cal_y - 10 - 57.5,
        left = cal_x + 20
    )
    player_frame2 = ft.Image(
        "https://raw.githubusercontent.com/YogyaChugh/Ludo/master/assets/frame.jpg",
        width = 115,
        height = 57.5,
        top = cal_y - 10 - 57.5,
        left = cal_x + 24*9 + (24*6 - 115) - 20
    )
    player_frame3 = ft.Image(
        "https://raw.githubusercontent.com/YogyaChugh/Ludo/master/assets/frame.jpg",
        width = 115,
        height = 57.5,
        top = cal_y + data.get('board_height') + 10,
        left = cal_x + 20
    )
    player_frame4 = ft.Image(
        "https://raw.githubusercontent.com/YogyaChugh/Ludo/master/assets/frame.jpg",
        width = 115,
        height = 57.5,
        top = cal_y + data.get('board_height') + 10,
        left = cal_x + 24*9 + (24*6 - 115) - 20
    )
    
    cont.controls.append(player_frame)
    cont.controls.append(player_frame2)
    cont.controls.append(player_frame3)
    cont.controls.append(player_frame4)

    bgimg.content = cont
    page.add(bgimg)
    page.update()

    # THE GAME PLAY
    player_in_turn = random.choice(players)
    print('Player in turn: ',player_in_turn.color.color)
    dice.associate_player(player_in_turn) #Very Important else GameOver error (check roll method of Dice class in base.py)
    dice.cont.on_tap = dice.roll
    page.session.set('player_name',pl)
    page.session.set('game_running', False)
    page.update()

async def main(page: ft.Page):
    page.window.width = 400
    page.window.maximizable = False
    page.window.resizable = False
    page.padding = 0
    page.update()
    os.environ['num_players'] = '2'
    page.session.set('game_running',False)

    bgimg = ft.Container(
        image = ft.DecorationImage('lander.png', fit = ft.ImageFit.FILL, opacity=0.8),
        expand = True
    )
    page.add(bgimg)

    await asyncio.sleep(3)

    page.remove(bgimg)
    await asyncio.create_task(game(page,'assets/board_4.yaml'))

ft.app(main,assets_dir="assets")