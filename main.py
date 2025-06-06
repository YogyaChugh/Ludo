import flet as ft

def main(page: ft.Page):
    page.padding = 0
    
    img = ft.Image(
        'https://raw.githubusercontent.com/YogyaChugh/Ludo/master/assets/board_4.jpg',
        fit=ft.ImageFit.FILL
    )

    anoth_img = ft.Image(
        'https://raw.githubusercontent.com/YogyaChugh/Ludo/master/assets/base.png',
        width=24,
        top=144,
        left=24
    )

    gg = ft.Container(img,alignment=ft.alignment.top_left)

    cont = ft.Stack([gg,anoth_img])

    page.add(cont)
    page.update()

ft.app(main,assets_dir="assets")