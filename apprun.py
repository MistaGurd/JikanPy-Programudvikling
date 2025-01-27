from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy.network.urlrequest import UrlRequest
from kivy.uix.label import Label

# Liste af genre, med en key (genrenavn) og en value (tal-ID)
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

# Konverterer VALID_GENRES til et dictionary
GENRE_LOOKUP = {genre[0]: genre[1] for genre in VALID_GENRES}


class StartScreen(Screen):
    def show_error_popup(self, message): # Opret sit error pop up hvis der bliver indtastede en ugyldig genre
        # Reference the popup template in the .kv file
        popup = ErrorPopup()
        popup.ids.error_message.text = message  # Beskeden indsættes i et dynamisk label-widget som har id: Error_message i pop up
        popup.open() # Den del af koden som åbner error pop up

    def search_anime(self, genre_input):
        genre = genre_input.strip().lower()  # Convert input to lowercase
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


class ResultsScreen(Screen):
    def fetch_anime(self, genre_id): # Vores funktion, som finder data via API'en
        self.ids.grid_layout.clear_widgets()  # Kalder på grid_layout i kv filen, og rydder den
        self.ids.grid_layout.add_widget(Label(text="Indlæser...", size_hint_y=None, height=40)) # Kalder på grid_layout i kv filen, og tilføjer en loading label

        url = f"https://api.jikan.moe/v4/anime?genres={genre_id}&order_by=score&sort=desc&limit=10"
        # Definerer API'ens URL som en variabel,
        # hvor genre_id kommer frem GENRE_LOOKUP,
        # som kommer fra listen VALID_GENRES
        UrlRequest(
            url,
            on_success=self.display_results,
            on_error=self.api_error,
            on_failure=self.api_error,
        )
        # UrlRequest lader programmet køre videre når den har fetched data, hvor:
        # Hvis succes, går koden videre til display_results
        # Hvis fejl, går koden mod api_error

    def display_results(self, request, result):
        self.ids.grid_layout.clear_widgets() # Starter med at rydde bordet
        try:
            anime_list = result.get("data", []) # Ny variabel som liste
            for anime in anime_list: # For hver anime i listen
                image_url = anime.get("images", {}).get("jpg", {}).get("image_url", "") # Tag billede-
                title = anime.get("title", "Ukendt Titel") # og titel- ("Ukendt Titel" er en pre-defineret sætning, hvis der er fejl)
                self.ids.grid_layout.add_widget(
                    self.create_anime_item(image_url, title)
                )
                # Og samle det i et grid_layout, med de betingelser,
                # som bliver defineret i kv filen
            if not anime_list:
                self.ids.grid_layout.add_widget(Label(text="Ingen resultater. Prøv en anden genre."))
        except Exception as e:
            self.ids.grid_layout.add_widget(Label(text=f"Fejl under indlæsning af resultater: {e}"))
            # Fejlhåndtering, hvis en anime enten ikke er i listen, eller en datalæsefejl fra API

    def api_error(self, request, error):
        self.ids.grid_layout.clear_widgets()
        self.ids.grid_layout.add_widget(Label(text=f"API-fejl: {error}"))
        # Hvis der er fejl i API'en, vil fetch_anime kalde på denne funktion, som viser en error textlabel

    def create_anime_item(self, image_url, title):
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.image import AsyncImage
        from kivy.uix.label import Label

        anime_box = BoxLayout(orientation="vertical", size_hint_y=None, height=300)

        anime_image = AsyncImage(source=image_url, size_hint=(1, 0.8))
        anime_box.add_widget(anime_image)

        anime_label = Label(
            text=title,
            size_hint=(1, 0.2),
            valign="middle",
            halign="center",
            font_size="14sp",
        )
        anime_label.bind(size=anime_label.setter("text_size"))  # Allow text wrapping
        anime_box.add_widget(anime_label)

        return anime_box


class ErrorPopup(Popup):
    pass
    # Error screen, som bliver håndteret af Kivy i kv filen

class AnimeApp(App):
    def build(self):
        Window.maximize()  # Får programmet til at åbne i Windowded borderless
        sm = ScreenManager() # Variabel for håndtering af start-skærm, og resultatskærm
        sm.add_widget(StartScreen(name="start"))
        sm.add_widget(ResultsScreen(name="results"))
        return sm


if __name__ == "__main__":
    AnimeApp().run()
    # Start programmet!