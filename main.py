import flet as ft
import copy
import yaml
import math
import base
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

def main(page: ft.Page):
    page.window.width = 400
    page.window.maximizable = False
    page.window.resizable = False
    page.padding = 0
    
    img = ft.Image(
        'https://raw.githubusercontent.com/YogyaChugh/Ludo/master/assets/board_4.jpg',
        fit=ft.ImageFit.FILL
    )

    dice_img = ft.Image(
        'https://raw.githubusercontent.com/YogyaChugh/Ludo/master/assets/base.png',
        width=22,
        height=22,
        top=169,
        left=25
    )

    main_board = ft.Container(img,alignment=ft.alignment.top_left)
    cont = ft.Stack([main_board,dice_img])

    page.add(cont)

    a = base.Board('data/board_4.yaml')
    page.update()

ft.app(main,assets_dir="assets")