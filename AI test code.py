from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import AsyncImage
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.network.urlrequest import UrlRequest
import json

# Predefined valid genres (can be expanded as needed)
VALID_GENRES = {
    "action": 1,
    "adventure": 2,
    "comedy": 4,
    "drama": 8,
    "fantasy": 10,
    "horror": 14,
    "mystery": 7,
    "romance": 22,
    "sci-fi": 24,
    "slice of life": 36,
}

# Screen for search
class StartScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Input field for anime genre
        self.genre_input = TextInput(hint_text='Enter Anime Genre', size_hint=(1, 0.2))
        layout.add_widget(self.genre_input)

        # Search Button
        search_button = Button(text='Search', size_hint=(1, 0.2))
        search_button.bind(on_press=self.search_anime)
        layout.add_widget(search_button)

        self.add_widget(layout)

    def show_error_popup(self, message):
        popup = Popup(title="Input Error",
                      content=Label(text=message),
                      size_hint=(0.8, 0.4))
        popup.open()

    def search_anime(self, instance):
        genre = self.genre_input.text.strip().lower()  # Convert input to lowercase
        if not genre:
            self.show_error_popup("Please enter a genre!")
            return

        if genre not in VALID_GENRES:
            self.show_error_popup(f"'{genre}' is not a valid genre. Please type something else!")
            return

        # Switch to results screen and start API search
        self.manager.current = 'results'
        self.manager.get_screen('results').fetch_anime(VALID_GENRES[genre])

# Screen for displaying results
class ResultsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10, size_hint_y=None)
        self.layout.bind(minimum_height=self.layout.setter('height'))

        self.scroll_view = ScrollView(size_hint=(1, 1))
        self.scroll_view.add_widget(self.layout)
        self.add_widget(self.scroll_view)

    def fetch_anime(self, genre_id):
        self.layout.clear_widgets()  # Clear previous results
        loading_label = Label(text="Loading...", size_hint_y=None, height=40)
        self.layout.add_widget(loading_label)

        # Fetch anime from API
        url = f"https://api.jikan.moe/v4/anime?genres={genre_id}&order_by=score&sort=desc&limit=10"
        UrlRequest(url, on_success=self.display_results, on_error=self.api_error, on_failure=self.api_error)

    def display_results(self, request, result):
        self.layout.clear_widgets()
        try:
            anime_list = result.get('data', [])
            for anime in anime_list:
                anime_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=100, padding=5, spacing=10)

                # Anime Image
                image_url = anime.get('images', {}).get('jpg', {}).get('image_url', '')
                anime_image = AsyncImage(source=image_url, size_hint=(0.2, 1))
                anime_box.add_widget(anime_image)

                # Anime Title
                title = anime.get('title', 'Unknown Title')
                anime_label = Label(text=title, size_hint=(0.8, 1), valign='middle', halign='left')
                anime_label.bind(size=anime_label.setter('text_size'))  # Allow text wrapping
                anime_box.add_widget(anime_label)

                self.layout.add_widget(anime_box)

            if not anime_list:
                self.layout.add_widget(Label(text="No results found. Try another genre."))
        except Exception as e:
            self.layout.add_widget(Label(text=f"Error parsing results: {e}"))

    def api_error(self, request, error):
        self.layout.clear_widgets()
        self.layout.add_widget(Label(text=f"API Error: {error}"))

# Main App
class AnimeApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(StartScreen(name='start'))
        sm.add_widget(ResultsScreen(name='results'))
        return sm

if __name__ == "__main__":
    AnimeApp().run()
