import flet as ft
import copy
import yaml
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
        top=253,
        left=37
    )
    with open('data/board_4.yaml', 'r') as file:
        data = yaml.load(file,Loader=Loader)
    print(data)
    main_board = ft.Container(img,alignment=ft.alignment.top_left)
    cont = ft.Stack([main_board])

    positions = data.get('base_positions')

    for i in positions:
        for j in i.values():
            for k in j:
                temp = copy.deepcopy(dice_img)
                extra_dist = (k.get('w')-dice_img.width)/2
                temp.top = k.get('y') + extra_dist
                temp.left = k.get('x') + extra_dist
                cont.controls.append(temp)
    page.update()

    page.add(cont)
    page.update()

ft.app(main,assets_dir="assets")