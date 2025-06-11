import flet as ft

def main(page: ft.Page):
    page.bgcolor = ft.colors.GREY_200
    page.window_width = 800
    page.window_height = 600

    play_button = ft.Ref[ft.ElevatedButton]()
    card_container = ft.Ref[ft.Container]()
    selected_option_index = {"index": None}

    def option_selected(e):
        for i, btn in enumerate(option_buttons):
            btn.style.bgcolor = ft.colors.BLUE if e.control == btn else ft.colors.SURFACE_VARIANT
        play_button.current.disabled = False
        selected_option_index["index"] = option_buttons.index(e.control)
        page.update()

    def close_card(e):
        card_container.current.visible = False
        page.update()

    def update_card_position():
        w, h = page.window_width, page.window_height
        card_width, card_height = 300, 200
        offset_x = (w - card_width) / 2
        offset_y = (h - card_height) / 2
        card_container.current.left = offset_x
        card_container.current.top = offset_y

    option_buttons = [
        ft.TextButton("2/3/4P", on_click=option_selected),
        ft.TextButton("5P", on_click=option_selected),
        ft.TextButton("6P", on_click=option_selected),
    ]

    for btn in option_buttons:
        btn.style = ft.ButtonStyle(bgcolor=ft.colors.SURFACE_VARIANT, padding=10)

    play = ft.ElevatedButton("Play", disabled=True, ref=play_button)

    close_icon = ft.IconButton(icon=ft.icons.CLOSE, on_click=close_card, icon_color=ft.colors.RED)

    # Card content
    card = ft.Container(
        ref=card_container,
        content=ft.Stack([
            ft.Column([
                ft.Row(option_buttons, alignment=ft.MainAxisAlignment.SPACE_AROUND),
                play,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=20),
            ft.Container(
                content=close_icon,
                alignment=ft.alignment.top_right
            )
        ]),
        width=300,
        height=200,
        bgcolor=ft.colors.WHITE,
        border_radius=15,
        padding=20,
        left=0,  # will be adjusted
        top=0,
    )

    # Place card inside a full-screen stack so we can use top/left
    root = ft.Stack(
        controls=[card],
        width=page.window_width,
        height=page.window_height,
    )

    def on_resize(e):
        root.width = page.window_width
        root.height = page.window_height
        update_card_position()
        page.update()

    page.on_resize = on_resize
    page.add(root)
    update_card_position()

ft.app(target=main)
