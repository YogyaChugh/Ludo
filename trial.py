import flet as ft

def main(page: ft.Page):
    page.horizontal_alignment = "center"
    page.vertical_alignment = "center"

    # Selection state
    selected = ft.Ref[bool]()
    selected.value = False

    # Button border colors
    border_color_selected = "#000000"
    border_color_none = "transparent"

    # Function to toggle selection
    def toggle_selection(e):
        selected.value = not selected.value
        ludo_button.border = ft.border.all(4, border_color_selected if selected.value else border_color_none)
        ludo_button.update()

    # Ludo-themed colorful button
    ludo_button = ft.Container(
        content=ft.Text("Play Ludo!", size=20, weight="bold", color="white"),
        width=200,
        height=60,
        alignment=ft.alignment.center,
        bgcolor=ft.LinearGradient(
            begin=ft.alignment.top_left,
            end=ft.alignment.bottom_right,
            colors=["#f44336", "#4caf50", "#2196f3", "#ffeb3b"]
        ),
        border_radius=30,
        border=ft.border.all(4, border_color_none),
        on_click=toggle_selection,
        ink=True,
        animate=ft.Animation(300, "easeInOut"),
    )

    page.add(ludo_button)

ft.app(target=main)
