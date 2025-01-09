from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import AsyncImage
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.network.urlrequest import UrlRequest
from kivy.core.window import Window

import json


# Predefined valid genres (matrix format: [genre_name, genre_id])
VALID_GENRES = [
    ["action", 1],
    ["adventure", 2],
    ["comedy", 4],
    ["drama", 8],
    ["fantasy", 10],
    ["horror", 14],
    ["mystery", 7],
    ["romance", 22],
    ["sci-fi", 24],
    ["slice of life", 36],
]

# Convert VALID_GENRES to a dictionary for quick ID lookup
GENRE_LOOKUP = {genre[0]: genre[1] for genre in VALID_GENRES}


# Screen for search
class StartScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Valid genres list for display in the search bar
        valid_genres_text = ", ".join([g[0] for g in VALID_GENRES])

        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Input field for anime genre with valid genres as placeholder text
        self.genre_input = TextInput(
            hint_text=f"Indtast animegenre (gyldige genrer: {valid_genres_text})",
            size_hint=(1, 0.2),
        )
        layout.add_widget(self.genre_input)

        # Search Button
        search_button = Button(text="Søg", size_hint=(1, 0.2))
        search_button.bind(on_press=self.search_anime)
        layout.add_widget(search_button)

        self.add_widget(layout)

    def show_error_popup(self, message):
        # Create a popup showing the error message
        popup = Popup(
            title="Inputfejl",
            content=Label(text=message),
            size_hint=(0.8, 0.6),
        )
        popup.open()

    def search_anime(self, instance):
        genre = self.genre_input.text.strip().lower()  # Convert input to lowercase
        if not genre:
            self.show_error_popup("Indtast venligst en genre!")
            return

        if genre not in GENRE_LOOKUP:
            valid_genres = ", ".join([g[0] for g in VALID_GENRES])
            self.show_error_popup(
                f"'{genre}' er ikke en gyldig genre.\n\nGyldige genrer er:\n{valid_genres}"
            )
            return

        # Switch to results screen and start API search
        self.manager.current = "results"
        self.manager.get_screen("results").fetch_anime(GENRE_LOOKUP[genre])


# Screen for displaying results
class ResultsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Use BoxLayout for the overall layout
        root_layout = BoxLayout(orientation="vertical", spacing=10, padding=10)

        # Scrollable results layout
        self.grid_layout = GridLayout(
            cols=5,  # Set 5 columns
            padding=10,
            spacing=10,
            size_hint_y=None,
        )
        self.grid_layout.bind(minimum_height=self.grid_layout.setter("height"))

        scroll_view = ScrollView(size_hint=(1, 0.9))
        scroll_view.add_widget(self.grid_layout)
        root_layout.add_widget(scroll_view)

        # Back Button at the bottom
        back_button = Button(text="Tilbage", size_hint=(1, 0.1))
        back_button.bind(on_press=self.go_back)
        root_layout.add_widget(back_button)

        self.add_widget(root_layout)

    def fetch_anime(self, genre_id):
        self.grid_layout.clear_widgets()  # Clear previous results
        loading_label = Label(text="Indlæser...", size_hint_y=None, height=40)
        self.grid_layout.add_widget(loading_label)

        # Fetch anime from API
        url = f"https://api.jikan.moe/v4/anime?genres={genre_id}&order_by=score&sort=desc&limit=10"
        UrlRequest(
            url,
            on_success=self.display_results,
            on_error=self.api_error,
            on_failure=self.api_error,
        )

    def display_results(self, request, result):
        self.grid_layout.clear_widgets()
        try:
            anime_list = result.get("data", [])
            for anime in anime_list:
                # Create a vertical layout for each anime (image + title)
                anime_box = BoxLayout(orientation="vertical", size_hint=(None, None))

                # Anime Image
                image_url = anime.get("images", {}).get("jpg", {}).get("image_url", "")
                anime_image = AsyncImage(source=image_url, size_hint=(1, 0.8))
                anime_image.size_hint_x = None
                anime_image.width = Window.width / 5  # Dynamic width per column
                anime_image.height = Window.height / 5  # Adjust height proportionally
                anime_box.add_widget(anime_image)

                # Anime Title
                title = anime.get("title", "Ukendt Titel")
                anime_label = Label(
                    text=title,
                    size_hint=(1, 0.2),
                    valign="middle",
                    halign="center",
                    font_size="14sp",
                )
                anime_label.bind(size=anime_label.setter("text_size"))  # Allow text wrapping
                anime_box.add_widget(anime_label)

                # Add anime box to grid layout
                anime_box.width = Window.width / 5
                anime_box.height = Window.height / 4
                self.grid_layout.add_widget(anime_box)

            if not anime_list:
                self.grid_layout.add_widget(Label(text="Ingen resultater. Prøv en anden genre."))
        except Exception as e:
            self.grid_layout.add_widget(Label(text=f"Fejl under indlæsning af resultater: {e}"))

    def api_error(self, request, error):
        self.grid_layout.clear_widgets()
        self.grid_layout.add_widget(Label(text=f"API-fejl: {error}"))

    def go_back(self, instance):
        self.manager.current = "start"


# Main App
class AnimeApp(App):
    def build(self):
        Window.maximize()  # Maximize the window to utilize the full screen
        sm = ScreenManager()
        sm.add_widget(StartScreen(name="start"))
        sm.add_widget(ResultsScreen(name="results"))
        return sm


if __name__ == "__main__":
    AnimeApp().run()
