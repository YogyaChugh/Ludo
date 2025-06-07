import flet as ft
import base
import asyncio
import copy
import math
import os
import exceptions
import random
try:
    from yaml import CLoader as Loader, CDumper as Dumper, load, dump
except ImportError:
    from yaml import Loader, Dumper, load, dump


async def game(page,board_yaml_file):

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
    print("w: ", w,"\nh: ",h)


    board_w = data.get('board_width')
    board_h = data.get('board_height')
    cal_x = (w - board_w)//2
    cal_y = (h - board_h)//2
    print("calx: ",cal_x,"\ncaly: ",cal_y)

    # Background Image
    bgimg = ft.Container(
        image = ft.DecorationImage('https://raw.githubusercontent.com/YogyaChugh/Ludo/master/assets/background.png', fit = ft.ImageFit.COVER, opacity=0.8),
        expand = True
    )

    # Board Image
    img = ft.Image(
        'https://raw.githubusercontent.com/YogyaChugh/Ludo/master/assets/board_4.jpg',
        fit=ft.ImageFit.FILL
    )


    # Base of Every Token
    dice_img = ft.Image(
        'https://raw.githubusercontent.com/YogyaChugh/Ludo/master/assets/base.png',
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

    num = ft.Text('0',left = cal_x + board_w//2 - 20, top = cal_y + board_h + 80)

    def do_it(e=None):
        print("e: ",e)
        print('hi')
        page.update()

    def create_token(i,j,n):
        temp = copy.deepcopy(dice_img)
        
        def dont_do_it(e=None):
            pass

        temporary = ft.GestureDetector(
            mouse_cursor=ft.MouseCursor.CLICK,
            on_tap = dont_do_it,
            content = temp,
            top = cal_y + j.location[1] + math.fabs(j.dimension[1] - data.get('dice_base_height'))//2,
            left = cal_x + j.location[0] + math.fabs(j.dimension[0] - data.get('dice_base_width'))//2
        )

        return temporary

    # Generating Player tokens and handling click events
    for i in players:
        n = 0
        for j in i.color.home_blocks:
            i.tokens[n].current_block = j
            i.tokens[n].gesture_cont = create_token(i,j,n)
            cont.controls.append(i.tokens[n].gesture_cont)
            n += 1
    page.update()
    
    cur_number = 0
    def roll(e=None):
        cur_number = random.randint(1,6)
        num.value = cur_number
        page.update()

    but = ft.ElevatedButton("Roll Dice",on_click=roll,left = cal_x + board_w//2 - 35, top = cal_y + board_h + 20,disabled=True)
    cont.controls.append(but)
    cont.controls.append(num)

    bgimg.content = cont
    page.add(bgimg)
    page.update()

async def main(page: ft.Page):
    page.window.width = 400
    page.window.maximizable = False
    page.window.resizable = False
    page.padding = 0
    page.update()
    os.environ['num_players'] = '2'

    bgimg = ft.Container(
        image = ft.DecorationImage('https://raw.githubusercontent.com/YogyaChugh/Ludo/master/assets/landing_page.png', fit = ft.ImageFit.FILL, opacity=0.8),
        expand = True
    )
    page.add(bgimg)

    await asyncio.sleep(3)

    page.remove(bgimg)
    await asyncio.create_task(game(page,'data/board_4.yaml'))

    print("It's running")

ft.app(main,assets_dir="assets",port=5000)