import flet as ft

def main(page: ft.Page):
    page.window.width = 144
    page.window.height = 144
    page.padding = 0
    image = ft.Image(
        'player_frame.png',
        width=144,
        height=144,
        top=0,
        left=0
    )
    anoth = ft.Image(
        'ok.jpg',
        width = 120,
        height = 95,
        top=11.5,
        left=12,
        fit = ft.ImageFit.FILL
    )

    stacker = ft.Stack([image,anoth])
    page.add(stacker)
    page.update()

ft.app(main,assets_dir='assets')