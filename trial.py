import flet as ft

import flet_lottie as fl

def main(page: ft.Page):
    page.add(
        fl.Lottie(
            src='https://raw.githubusercontent.com/YogyaChugh/Ludo/master/assets/dice_1.json',
            reverse=False,
            animate=True
        )
    )

ft.app(main,assets_dir="assets")