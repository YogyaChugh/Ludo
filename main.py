import flet as ft
import asyncio
import os
import exceptions
import game
import diagnostics
import sys
from functools import partial
try:
    from yaml import CLoader as Loader, CDumper as Dumper, load, dump
except ImportError:
    from yaml import Loader, Dumper, load, dump


num_players = None
map_selected = False
num_selected = False

async def main(page: ft.Page):
    email = "yogyachugh10@gmail.com"
    password = "yqgv dryt fobd rjpz"
    os.environ['email'] = email
    os.environ['password'] = password
    # Just for testing on desktops !
    page.window.width = 400
    page.window.maximizable = False
    page.window.resizable = False
    page.padding = 0    # Necessary for alignment calculation and background image
    page.update()
    page.session.set('game_running',False)

    def back_to_the_main(e=None):
        temp_store = page.views.pop()
        page.update()

    page.on_route_change = back_to_the_main


    # Fixed landing page !
    background_image = ft.Container(
        image = ft.DecorationImage('landing_page.png', fit = ft.ImageFit.FILL, opacity=0.8),
        expand = True
    )
    page.add(background_image)
    await asyncio.sleep(1.5)
    page.remove(background_image)
    # Everything for the match is blitted onto another view

    if page.platform == ft.PagePlatform.ANDROID or page.platform == ft.PagePlatform.IOS:
        w = page.width  # These values are read-only in flet
        h = page.height
    else:
        w = page.window.width
        h = page.window.height

    # I have written the functions earlier so that the logic is all sorted at the end

    # The number of player selection card ! Used later
    async def ask_num_players(e=None):
        play_button.src = "play02.png"
        page.update()
        await asyncio.sleep(0.3)
        play_button.src = "play01.png"
        page.update()
        cont.controls.append(
            ask_the_num_player_card
        )
        page.update()

    # Actually calling the match after play in the ask_num_player function's card is clicked !
    async def call_the_match(e):
        #Call the match !
        cont.controls.remove(ask_the_num_player_card)
        page.update()
        try:
            play_the_game.disabled = True
            the_epic_game = game.Game(page,num_players)
            await asyncio.create_task(the_epic_game.game())
        except exceptions.GameOver or Exception as e:
            # Error showing
            page.controls.clear()
            page.padding=10
            error_log = ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text(
                            "Sorry ! Game Encountered Errors\nIf you consider improving the game click on the button to send diagnostics data !\n----------------------------------\nLOGS:\n" + e.message,
                            size=12,
                            font_family="Courier New",
                            selectable=True,
                            color=ft.Colors.RED_900,
                        )
                    ],
                    scroll=ft.ScrollMode.ALWAYS,
                ),
                width=600,
                height=200,
                padding=15,
                bgcolor=ft.Colors.RED_100,
                border_radius=10,
                border=ft.border.all(1, ft.Colors.RED_300),
            )
            page.add(error_log)
            os.environ['error'] = e.message
            send_error_mail = partial(diagnostics.send_diagnostics_data,page=page,error_log=error_log)
            page.add(ft.Button('SEND DIAGNOSTICS',on_click=send_error_mail))
            page.update()
    
    maps = [
        ft.Image(
            "board_4.jpg",
            width = 20,
            height = 20
        ),
        ft.Image(
            'board_5.png',
            width = 120,
            height = 120
        )
    ]
    

    maps_images = ft.Container(
        ft.Row(
            scroll=ft.ScrollMode.HIDDEN,
            alignment=ft.MainAxisAlignment.CENTER,
            expand = False,
            run_spacing= 10
        ),
        bgcolor = ft.Colors.GREY_300
    )

    def select_it(i,e):
        global map_selected,num_selected
        map_selected = True
        if num_selected:
            play_the_game.disabled = False
        for j in maps_images.content.controls:
            j.border = None
        maps_images.content.controls[i].border = ft.border.all(4,ft.Colors.BLACK)
        page.update()

    for i in range(0,len(maps)):
        map_image = ft.Container(
            content = maps[i],
            width = 150,
            height = 150,
            border_radius=10,
            border = None,
            ink = True,
            bgcolor=ft.Colors.WHITE,
            on_click=partial(select_it,i)
        )
        maps_images.content.controls.append(map_image)
        maps_images.content.controls[0].border = ft.border.all(4,ft.Colors.BLACK)
        select_it(0,'go')
        global map_selected
        map_selected = True
        page.update()

    play_the_game = ft.ElevatedButton("Play",disabled=True,on_click=call_the_match)

    def update_value(value,e):
        global num_selected,map_selected
        num_selected = True
        global num_players
        num_players = value
        if map_selected:
            play_the_game.disabled = False
        page.update()
    
    def remove_ask(e):
        global num_selected
        num_selected = False
        play_the_game.disabled = True
        cont.controls.remove(ask_the_num_player_card)
        page.update()

    back = ft.Container(
        ft.Image(
            "back.png",
            width = 30,
            height = 30
        ),
        on_click=remove_ask,
        padding = ft.Padding(10,10,10,20)
    )

    ask_the_num_player_card = ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        back,
                        maps_images,
                        ft.Row(
                            [
                                ft.ElevatedButton("2P",on_click=partial(update_value,2)),
                                ft.ElevatedButton("3P",on_click=partial(update_value,3)),
                                ft.ElevatedButton("4P",on_click=partial(update_value,4)),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER
                        ),
                        ft.Row(
                            [play_the_game],
                            alignment=ft.MainAxisAlignment.CENTER,
                        ),
                    ],
                ),
                width=400,
                padding=10
            ),
            shadow_color=ft.Colors.ON_SURFACE_VARIANT,
            width = w - 100,
            height = 350,
            left = 50,
            top = (h - (h-350))/2,
        )

    menu = ft.Container(
        image = ft.DecorationImage('bgimg.png', fit = ft.ImageFit.FILL),
        expand = True
    )

    cont = ft.Stack([])

    icon = ft.Image(
        'ludoicon.png',
        left = w//2 - 173.5 - 4,
        top = h//2 - 147*2 - 40
    )
    brand_ambassador = ft.Image(
        'uncleji.png',
        width = 1024/4,
        height = 1536/4,
        left = (w - (1024)/4)/2,
        top = (h - (1536)/4)/2
    )

    play_button = ft.Image(
        'play01.png',
        width = 144,
        height = 72,
        fit=ft.ImageFit.FILL
    )

    # The gesture detector to detect the play button clicking !
    play_gesture = ft.GestureDetector(
        mouse_cursor=ft.MouseCursor.CLICK,
        content=play_button,
        on_tap=ask_num_players,
        left = w//2 - 72,
        top = h - 200
    )
    
    about = ft.Image(
        'about01.png',
        width = 144,
        height=72,
        left = w//2 - 180,
        top = h - 130,
        fit = ft.ImageFit.FILL
    )
    settings = ft.Image(
        'settings.png',
        width = 144,
        height=72,
        left = w - 180,
        top = h - 130,
        fit = ft.ImageFit.FILL
    )

    cont.controls.append(icon)
    cont.controls.append(brand_ambassador)
    cont.controls.append(play_gesture)
    cont.controls.append(about)
    cont.controls.append(settings)
    menu.content = cont
    page.add(menu)
    page.update()

ft.app(main,assets_dir="assets")