import flet as ft
import base
import asyncio
import copy
import os
import exceptions
import random
import smtplib
from dotenv import load_dotenv
from functools import partial
from email.message import EmailMessage
try:
    from yaml import CLoader as Loader, CDumper as Dumper, load, dump
except ImportError:
    from yaml import Loader, Dumper, load, dump


# Send Diagnostics Data on error !
def send_mail(e,page,error_log):
    load_dotenv()
    if not os.environ.get('email') or not os.environ.get('password'):
        error_log.content.controls[0].value += "\n-------------------------\nCAN'T FIND THE SECRET ENVIRONMENT FILE !"
        page.update()
        return
    message = os.environ.get('error')
    msg = EmailMessage()
    msg.set_content(message)
    msg['Subject'] = "Diagnostics Data"
    msg['From'] = os.environ.get('email') # Fetched from the env secret's file
    msg['To'] = 'yogya.developer@gmail.com'
    try:
        with smtplib.SMTP('smtp.gmail.com',587) as server:
            server.starttls()
            server.login(os.environ.get('email'),os.environ.get('password'))
            server.sendmail(os.environ.get('email'),'yogya.developer@gmail.com',msg.as_string())
        error_log.content.controls[0].value += "\n-------------------------\nDIAGNOSTICS DATA SENT !"
        page.update()
    except Exception:
        error_log.content.controls[0].value +="\n-------------------------\nSENDING DIAGNOSTICS DATA FAILED !"
        page.update()
        return


async def game(page,board_yaml_file,e=None):
    page.session.set('game_running',True)

    # Load File
    try:
        with open(board_yaml_file,'r') as file:
            data = load(file,Loader)
    except Exception as e:
        raise exceptions.GameOver(f"File loading Failed:\n-------------------------\nFile: {board_yaml_file}\n{e.args[1]}")
    page.session.set('data',data) # Set in session so as to be used in base.py

    # Fetch the screen dimensions for mobile ! For desktop, its fixed in main function
    if page.platform == ft.PagePlatform.ANDROID or page.platform == ft.PagePlatform.IOS:
        w = page.width  # These values are read-only in flet
        h = page.height
    else:
        w = page.window.width
        h = page.window.height

    board_w = data.get('board_width')
    board_h = data.get('board_height')
    if not board_w or not board_h or not data.get('min_players') or not data.get('max_players'):
        raise exceptions.GameOver(f"Game File Corrupt ! File: {board_yaml_file}")

    page.session.set('scale',1) # Normal Scale

    # If screen dimensions are less than the board dimensions
    # mentioned in the game '.json' files, then reduce the scale to half
    while (w - board_w)<0 or (h - board_h)<0:
        page.session.set('scale',page.session.get('scale')/2)
        board_w = board_w*page.session.get('scale')
        board_h = board_h*page.session.get('scale')

    scale = page.session.get('scale') # Used everywhere in this function !
    # Calculate board dimensions based on screen dimensions
    cal_x = (w - board_w)//2
    cal_y = (h - board_h)//2
    print("x: ",cal_x,'y: ',cal_y)
    os.environ['dimensions'] = str((cal_x, cal_y))


    # IMAGES
    
    #Check first
    list_of_images = [data.get('bg_image'),data.get('asset_board'),data.get('asset_dice_base')]
    try:
        for i in range(0,len(list_of_images)):
            current='assets/' + list_of_images[i]
            open(current)
    except Exception as e:
        raise exceptions.GameOver(f"File loading Failed:\n-------------------------\nFile: {current}\n{e.args[1]}")

    # Background Image
    bgimg = ft.Container(
        image = ft.DecorationImage(data.get('bg_image'), fit = ft.ImageFit.COVER, opacity=0.5),
        expand = True
    )

    # Board Image
    img = ft.Image(
        data.get('asset_board'),
        fit=ft.ImageFit.FILL,
        width = board_w,
        height = board_h
    )

    # Soon I will compile these missing error checks in one function !
    if not data.get('asset_dice_base') or not data.get('dice_base_width') or not data.get('dice_base_height') or not data.get('tokens') or not data.get('frames'):
        raise exceptions.GameOver(f"Game File Corrupt ! File: {board_yaml_file}")

    # Base of Every Token - It's same for all color tokens
    dice_img = ft.Image(
        data.get('asset_dice_base'),
        width = data.get('dice_base_width')*scale,
        height = data.get('dice_base_height')*scale
    )

    # Main Board
    main_board = ft.Container(img,left=cal_x,top=cal_y)
    cont = ft.Stack([main_board])   # Stack for all objects !


    # Creating the board which generates all blocks and other stuff in the form of objects
    board = base.Board(board_yaml_file)

    colors_left = copy.deepcopy(board.colors) # Stores the colors left on the board (based on number of players playing)
    players = []
    num_players = eval(os.environ.get('num_players'))
    if num_players<data.get('min_players') or num_players>data.get('max_players'):
        raise exceptions.GameOver(f"\n-------------------------\nMinimum Number of players for board: {data.get('min_players')}\nMaximum Number of players for board: {data.get('max_players')}\nCurrent Number: {num_players}")
    prev = 0

    page.session.set('tokens',{}) # This will simultaneously store locations of each token on board !

    # Dice for the match
    dice = base.Dice([cal_x + board_w//2 - 28*scale, cal_y + board_h + 20*scale],page,data)


    for i in range(0,num_players):
        # If player_number is even (starts from 0), then randomly color is chosen
        # Else, the color diagnolly opposite to the previously randomly chosen color
        # is chosen !
        if i % 2 == 0:
            a = random.choice(list(colors_left.keys()))
            prev = list(board.colors.keys()).index(a)
            players.append(base.Player(page,color = colors_left[a]))
        else:
            a = list(board.colors.keys())[len(list(board.colors.keys())) - 1 - prev]
            players.append(base.Player(page,color = colors_left[a]))
        colors_left.pop(a)

        # Loops in all tokens, creating hover images (diff for each color)
        # and base images (the circle at bottom) with gesture containers to allow clicking tokens !
        for j in players[-1].tokens:
            hover_image = ft.Image(
                f'https://raw.githubusercontent.com/YogyaChugh/Ludo/master/assets/token_{players[-1].color.color}.png',
                width = data.get('tokens')['w']*scale,
                height = data.get('tokens')['h']*scale
            )
            container1, container2 = j.create_token(dice_img,hover_image)
            cont.controls.append(container1)
            cont.controls.append(container2)

        # Creates the frame for each player playing !
        color = players[-1].color.color
        frames = data.get('frames')
        player_frame = ft.Image(
            f"https://raw.githubusercontent.com/YogyaChugh/Ludo/master/assets/frame_{color}.jpg",
            width = frames[color]['w']*scale,
            height = frames[color]['h']*scale,
            top = cal_y + frames[color]['y']*scale,
            left = cal_x + frames[color]['x']*scale
        )
        players[-1].frame = player_frame
        cont.controls.append(players[-1].frame) # This is the whole frame shown !
        page.update()

    cont.controls.append(dice.dice_image) # The dice in real !
    # need to do this dice image just before the gesture container

    for i in players:
        # This is different from the frame shown, as it is only the part
        # where dice will be shown with the gesture controller so as to allow
        # click/touch events !
        cont.controls.append(i.frame_cont)
        page.update()

    # All players !
    players_playing = players
    page.session.set('players',players_playing)
    page.session.set('won_list',[])

    # Adds all contents to the bgimg to display with the background image !
    bgimg.content = cont
    page.add(bgimg)


    # Initializes the game play
    player_in_turn = random.choice(players)
    dice.associate_player(player_in_turn) # Very Important else GameOver error (check roll method of Dice class in base.py)
    dice.update_dice_locs()     # Update dice locs based on the player in turn
    player_in_turn.frame_cont.on_tap = dice.roll    # Allow rolling the dice when dice is clicked !
    page.update()

async def main(page: ft.Page):
    # Just for testing on desktops !
    page.window.width = 400
    page.window.maximizable = False
    page.window.resizable = False
    page.padding = 0    # Necessary for alignment calculation and background image
    page.update()
    page.session.set('game_running',False)

    # Fixed landing page !
    background_image = ft.Container(
        image = ft.DecorationImage('landing_page.png', fit = ft.ImageFit.FILL, opacity=0.8),
        expand = True
    )
    # Everything for the match is blitted onto another view

    menu = ft.Container(
        image = ft.DecorationImage('bgimg.png', fit = ft.ImageFit.FILL),
        expand = True
    )

    cont = ft.Stack([])

    if page.platform == ft.PagePlatform.ANDROID or page.platform == ft.PagePlatform.IOS:
        w = page.width  # These values are read-only in flet
        h = page.height
    else:
        w = page.window.width
        h = page.window.height

    icon = ft.Image(
        'ludoicon.png',
        left = w//2 - 173.5 - 4,
        top = h//2 - 147*2 - 40
    )
    uncle = ft.Image(
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
    async def call_the_match(e=None):
        #Call the match !
        page.controls.clear()
        page.update()
        try:
            await asyncio.create_task(game(page,'assets/board_4.yaml'))
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
                            color=ft.colors.RED_900,
                        )
                    ],
                    scroll=ft.ScrollMode.ALWAYS,
                ),
                width=600,
                height=200,
                padding=15,
                bgcolor=ft.colors.RED_100,
                border_radius=10,
                border=ft.border.all(1, ft.colors.RED_300),
            )
            page.add(error_log)
            os.environ['error'] = e.message
            send_error_mail = partial(send_mail,page=page,error_log=error_log)
            page.add(ft.Button('SEND DIAGNOSTICS',on_click=send_error_mail))
            page.update()

    def ask_num_players(e=None):
        def update_value(e=None):
            os.environ['num_players'] = str(int(slider.value))
        slider = ft.Slider(
                    min=2, max=4, divisions=2, label="{value}",on_change=update_value
                )
        cont.controls.append(ft.Card(
                content=ft.Container(
                    content=ft.Column(
                        [
                            slider,
                            ft.Row(
                                [ft.ElevatedButton("Play",on_click=call_the_match)],
                                alignment=ft.MainAxisAlignment.CENTER,
                            ),
                        ]
                    ),
                    width=400,
                    padding=10,
                ),
                shadow_color=ft.Colors.ON_SURFACE_VARIANT,
                width = w - 200,
                height = h-600,
                left = (w - (w - 200))/2,
                top=(h - (h - 600))/2
            )
        )
        page.update()
        call_the_match()
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
    cont.controls.append(uncle)
    cont.controls.append(play_gesture)
    cont.controls.append(about)
    cont.controls.append(settings)
    menu.content = cont
    page.add(menu)
    page.update()

ft.app(main,assets_dir="assets")