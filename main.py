import flet as ft
import asyncio
import os
import exceptions
import game
import diagnostics
from functools import partial
try:
    from yaml import CLoader as Loader, CDumper as Dumper, load, dump
except ImportError:
    from yaml import Loader, Dumper, load, dump


num_players = None
map_selected = False
num_selected = False
app_temp_path = os.getenv("FLET_APP_STORAGE_TEMP")
logfile_path = app_temp_path + "/logs.txt"
logfile = open(logfile_path,'a')

async def main(page: ft.Page):
    logfile.write('Game Started\n')
    logfile.flush()

    def github_card():
        return ft.Container(
            top = 570,
            left = 50,
            width=300,
            height=80,
            padding=20,
            ink=True,
            border_radius=15,
            on_click=take_to_github_repo,
            bgcolor=ft.Colors.BLACK,
            alignment=ft.alignment.center_left,
            content=ft.Row(
                controls=[
                    ft.Image(
                        src="assets/icon.png",  # GitHub logo
                        width=40,
                        height=40,
                    ),
                    ft.Column(
                        spacing=5,
                        alignment=ft.MainAxisAlignment.CENTER,
                        controls=[
                            ft.Text("My GitHub Repository", weight="bold", color=ft.Colors.WHITE),
                            ft.Text("github.com/YogyaChugh/Ludo", color=ft.Colors.GREY_300, size=12),
                        ]
                    )
                ]
            )
        )

    def take_to_github_repo(e):
        page.launch_url("https://www.github.com/YogyaChugh/Ludo")
    email = "yogyachugh10@gmail.com"
    password = "yqgv dryt fobd rjpz"
    os.environ['email'] = email
    os.environ['password'] = password
    # Just for testing on desktops !
    def nothing(e):
        return
    page.window.width = 400
    page.window.maximizable = False
    page.window.resizable = False
    page.fonts = {
        'yourgone' : "assets/Youre Gone.otf",
        'angel': "assets/Lunera-Bold.otf"
    }
    page.padding = 0    # Necessary for alignment calculation and background image
    page.update()
    page.session.set('game_running',False)

    def back_to_the_main(e=None):
        logfile.write('\n\n\nBACK TO THE MAIN PAGE\n')
        temp_store = page.views.pop()
        a = page.views[-1]
        page.go(a.route)
        page.update()
        diagnostics.send_diagnostics_data(None,page,logfile_path)


    # Fixed landing page !
    background_image = ft.Container(
        image = ft.DecorationImage('landing_page.png', fit = ft.ImageFit.FILL, opacity=0.8),
        expand = True
    )
    logfile.write('Temporary Image Added\n')
    logfile.flush()
    page.add(background_image)
    await asyncio.sleep(1.5)
    page.remove(background_image)
    logfile.write('Temporary Image Removed\n')
    logfile.flush()
    # Everything for the match is blitted onto another view

    with open('assets/board_4.yaml') as file:
        data = load(file,Loader=Loader)
    if page.platform == ft.PagePlatform.ANDROID or page.platform == ft.PagePlatform.IOS:
        w = page.width  # These values are read-only in flet
        h = page.height
    else:
        w = page.window.width
        h = page.window.height
    
    logfile.write('Page Dimensions Calculated\n')
    logfile.flush()

    # I have written the functions earlier so that the logic is all sorted at the end

    # The number of player selection card ! Used later
    async def ask_num_players(e=None):
        logfile.write('Play Button Animation Started\n')
        logfile.flush()
        play_button.src = "play02.png"
        page.update()
        await asyncio.sleep(0.3)
        play_button.src = "play01.png"
        page.update()
        logfile.write('Play Button Animation Closed\n')
        logfile.flush()
        cont.controls.append(
            ask_the_num_player_card
        )
        logfile.write('Num Player Window Blitted\n')
        logfile.flush()
        page.update()

    # Actually calling the match after play in the ask_num_player function's card is clicked !
    async def call_the_match(e):
        #Call the match !
        cont.controls.remove(ask_the_num_player_card)
        page.update()
        try:
            the_epic_game = game.Game(page,num_players)
            logfile.write('Game Object created & Called !\n')
            logfile.flush()
            await asyncio.create_task(the_epic_game.game())
        except exceptions.GameOver or Exception as e:
            logfile.write(f'Exception Raised ! {e.args[1]}\n')
            logfile.flush()
            # Error showing
            try:
                if e.message=="DUDE THE GAME IS OVER !":
                    logfile.write('\n\n\nGAME IS NOW OVER\n')
                    logfile.write(f'Player Won List: {page.session.get('won_list')}')
                    logfile.flush()
                    leader = ft.Image(
                        "assets/leaderboard_man.png",
                        top = (h - 450)/2,
                        left = (w - 300)/2,
                        width = 300,
                        height = 450,
                    )
                    backer = ft.Container(
                        ft.Image(
                            "back.png",
                            width = 30,
                            height = 30
                        ),
                        on_click=back_to_the_main,
                        padding = ft.Padding(10,10,10,20),
                        top = leader.top + 40,
                        left = leader.left + 20
                    )
                    cont.controls.append(leader)
                    nanaa = 1
                    b = []
                    cont.controls.append(backer)
                    for i in page.session.get('won_list'):
                        contain = ft.Container(
                            content = ft.Text(i.name,font_family='yourgone'),
                            bgcolor = data.get('hex_values').get(i.color.color),
                            top = leader.top + 65 + 60*nanaa,
                            left = leader.left + 30,
                            width = 240,
                            height = 50,
                            border_radius= 20,
                            padding = 10
                        )
                        nanaa += 1
                        b.append(contain)
                        cont.controls.append(contain)
                    logfile.write('LeaderBoard Added\n')
                    logfile.flush()
                    page.update()
                    diagnostics.send_diagnostics_data(None,page,logfile_path)
            except Exception:
                pass
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
            logfile.write('Error Logs Added to Screen !\n')
            logfile.write(f"ERROR LOGS: {e.message}")
            logfile.flush()
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
        )
    )

    play_the_game = ft.Container(
        content=ft.Text(" PLAY ! ", size=20, weight="bold", color="white"),
        width = 90,
        height=50,
        alignment=ft.alignment.center,
        bgcolor=ft.Colors.LIME,
        border_radius=30,
        ink=True,
        data=[4,False],
        animate=ft.Animation(300, "easeInOut"),
        on_click=call_the_match
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
        logfile.write('Map Selection Panel Created\n')
        logfile.flush()

    def update_value(value,e=None):
        global num_selected,map_selected
        num_selected = True
        global num_players
        num_players = value
        if map_selected:
            play_the_game.disabled = False
        page.update()
    
    def remove_ask(i,e):
        if i==1:
            cont.controls.remove(ask_the_num_player_card)
        global num_selected
        num_selected = False
        play_the_game.disabled = True
        page.update()

    back = ft.Container(
        ft.Image(
            "back.png",
            width = 30,
            height = 30
        ),
        on_click=partial(remove_ask,1),
        padding = ft.Padding(10,10,10,20)
    )

    #THIS BUTTON IS WRITTEN BY CHATGPT ! JUST THIS ! I WAS TOO LAZY
    # Selection state

    # Button border colors
    border_color_selected = "#000000"
    border_color_none = "transparent"

    # Function to toggle selection
    def toggle_selection(k,e):
        logfile.write('2/3/4 Player Button Toggled\n')
        logfile.flush()
        for i in buttons:
            i.data[1] = False
            i.border = ft.border.all(4,border_color_none)
            i.update()
        k.data[1] = not k.data[1]
        k.border = ft.border.all(4, border_color_selected if k.data[1] else border_color_none)
        k.update()
        logfile.write(f'{k} Selected\n')
        logfile.flush()
        update_value(value=k.data[0])

    # Ludo-themed colorful button
    ludo_button2 = ft.Container(
        content=ft.Text(" 2P ", size=20, weight="bold", color="white"),
        width = 60,
        height=50,
        alignment=ft.alignment.center,
        bgcolor=ft.Colors.AMBER,
        border_radius=30,
        border=ft.border.all(4, border_color_none),
        ink=True,
        data=[2,False],
        animate=ft.Animation(300, "easeInOut"),
    )
    ludo_button2.on_click=partial(toggle_selection,ludo_button2)
    ludo_button3 = ft.Container(
        content=ft.Text(" 3P ", size=20, weight="bold", color="white"),
        width = 60,
        height=50,
        alignment=ft.alignment.center,
        bgcolor=ft.Colors.CYAN_ACCENT,
        border_radius=30,
        border=ft.border.all(4, border_color_none),
        ink=True,
        data=[3,False],
        animate=ft.Animation(300, "easeInOut"),
    )
    ludo_button3.on_click=partial(toggle_selection,ludo_button3)
    ludo_button4 = ft.Container(
        content=ft.Text(" 4P ", size=20, weight="bold", color="white"),
        width = 60,
        height=50,
        alignment=ft.alignment.center,
        bgcolor=ft.Colors.DEEP_PURPLE_ACCENT,
        border_radius=30,
        border=ft.border.all(4, border_color_none),
        ink=True,
        data=[4,False],
        animate=ft.Animation(300, "easeInOut"),
    )
    ludo_button4.on_click=partial(toggle_selection,ludo_button4)

    buttons = [ludo_button2,ludo_button3,ludo_button4]
    ask_the_num_player_card = ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        back,
                        maps_images,
                        ft.Row(
                            [
                                ludo_button2,
                                ludo_button3,
                                ludo_button4
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
            height = 380,
            left = 50,
            top = (h - (h-380))/2,
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

    async def about_func(e):
        logfile.write('About Page Added\n')
        logfile.flush()
        about.src = 'about02.png'
        page.update()
        await asyncio.sleep(0.3)
        about.src = 'about01.png'
        page.update()
        new_view = ft.View(route="/about",padding=0)
        page.update()
        bac = ft.Container(
            ft.Image(
                "back.png",
                width = 30,
                height = 30
            ),
            on_click=back_to_the_main,
            padding = ft.Padding(10,10,10,20)
        )
        bac.left = 20
        bac.top = 20
        
        new_menu = ft.Container(
            image = ft.DecorationImage('bgimg.png', fit = ft.ImageFit.FILL),
            expand = True
        )
        new_cont = ft.Stack([])
        new_cont.controls.append(bac)
        new_cont.controls.append(
            ft.Row(
                [ft.Text('ABOUT',font_family='yourgone',size=50,text_align=ft.TextAlign.CENTER)],
                top = 30,
                left = (w//2) - 80
            )
        )
        def openthegithub(e):
            logfile.write('My Github Opened\n')
            logfile.flush()
            page.launch_url("https://www.github.com/YogyaChugh")

        def openthefont(e):
            logfile.write('1001 Fonts Page Opened\n')
            logfile.flush()
            page.launch_url("https://www.1001fonts.com/")
        
        def openthelottie(e):
            logfile.write('lottiefiles Page Opened\n')
            logfile.flush()
            page.launch_url("https://lottiefiles.com/")

        def openthefreepik(e):
            logfile.write('Freepik Page Opened\n')
            logfile.flush()
            page.launch_url("https://www.freepik.com/")
        
        contai = ft.Container(
            ft.Image('assets/github_logo.png'),
            margin = 10,
            width = 80,
            height = 80,
            top = 170,
            left = 30,
            border_radius=20,
            ink = True,
            on_click=openthegithub
        )
        a = ft.Text("-----   CREATOR   -----",size=30,font_family="yourgone",top=120,left=40)
        b = ft.Text("YOGYA CHUGH",size=20,font_family="yourgone",top=190,left=140)
        c = ft.Text("yogya.developer@gmail.com",size=13,font_family="yourgone",top=230,left=140)
        a1 = ft.Text("-----   CREDITS   -----",size=30,font_family="yourgone",top=300,left=40)

        contai2 = ft.Container(
            ft.Image('assets/1001.png'),
            margin = 10,
            top = 330,
            left = 20,
            width = 120,
            height = 120,
            border_radius=20,
            ink = True,
            on_click = openthefont
        )

        contai3 = ft.Container(
            ft.Image('assets/lottiefiles.png'),
            margin = 10,
            top = 330,
            left = 140,
            width = 120,
            height = 120,
            border_radius=20,
            ink = True,
            on_click=openthelottie
        )

        contai4 = ft.Container(
            ft.Image('assets/freepik.png'),
            margin = 10,
            top = 360,
            left = 260,
            width = 60,
            height = 60,
            border_radius=20,
            ink = True,
            on_click=openthefreepik
        )

        gg = ft.Text("It's an Educational project ! All open-source\n and free ! Any person/company left for\n credits can kindly mail to the above mail !",size=12,font_family="angel",top=480,left=70)

        new_cont.controls.append(a)
        new_cont.controls.append(contai)
        new_cont.controls.append(b)
        new_cont.controls.append(c)
        new_cont.controls.append(a1)
        new_cont.controls.append(contai2)
        new_cont.controls.append(contai3)
        new_cont.controls.append(contai4)
        new_cont.controls.append(gg)
        new_cont.controls.append(github_card())
        logfile.write('About Page Components Added to View\n')
        logfile.flush()
        new_menu.content = new_cont
        new_view.controls.append(new_menu)
        page.views.append(new_view)
        logfile.write('About Page view added\n')
        logfile.flush()
        page.go('/about')
        logfile.write('Navigated to About Page\n')
        logfile.flush()
        page.update()


    about = ft.Image(
        'about01.png',
        width = 144,
        height=72,
        fit = ft.ImageFit.FILL
    )

    about_gesture = ft.GestureDetector(
        mouse_cursor=ft.MouseCursor.CLICK,
        content=about,
        on_tap=about_func,
        left = w//2 - 72,
        top = h - 130
    )
    cont.controls.append(icon)
    logfile.write('Ludo Clash Added\n')
    logfile.flush()
    cont.controls.append(brand_ambassador)
    logfile.write('Brand Ambassador Added\n')
    logfile.flush()
    cont.controls.append(play_gesture)
    logfile.write('Play Button Added\n')
    logfile.flush()
    cont.controls.append(about_gesture)
    logfile.write('About Button Added\n')
    logfile.flush()
    menu.content = cont
    page.session.set('cont',cont)
    page.add(menu)
    logfile.write('Main Page Added\n')
    logfile.flush()
    page.update()

ft.app(main,assets_dir="assets")