import flet as ft
import base
try:
    from yaml import CLoader as Loader, CDumper as Dumper, load, dump
except ImportError:
    from yaml import Loader, Dumper, load, dump

def game(page,board_yaml_file):

    with open(board_yaml_file,'r') as file:
        data = load(file,Loader)

    w = page.width
    h = page.height
    board_w = data.get('board_width')
    board_h = data.get('board_height')
    print(w,h)
    cal_x = (w - board_w)//2
    cal_y = (h - board_h)//2
    print(cal_x, cal_y)

    bgimg = ft.Container(
        image = ft.DecorationImage('assets/background.png', fit = ft.ImageFit.COVER),
        expand = True
    )

    img = ft.Image(
        'https://raw.githubusercontent.com/YogyaChugh/Ludo/master/assets/board_4.jpg',
        fit=ft.ImageFit.FILL
    )

    dice_img = ft.Image(
        'https://raw.githubusercontent.com/YogyaChugh/Ludo/master/assets/base.png',
        width=22,
        height=22,
        top= 169,
        left= 25
    )
    main_board = ft.Container(img,alignment=ft.alignment.center)
    cont = ft.Stack([main_board,dice_img])

    bgimg.content = cont

    page.add(bgimg)
    page.update()

    a = base.Board('data/board_4.yaml')

def main(page: ft.Page):
    page.window.width = 400
    page.window.maximizable = False
    page.window.resizable = False
    page.padding = 0
    page.update()

    game(page,'data/board_4.yaml')

ft.app(main,assets_dir="assets")