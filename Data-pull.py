from.kivy.app import app
from.kivy.uix.widget import widget
from.kivy.lang import builder
from.kivy.uix.screenmanager import screenmanager, screen
from jikanpy import Jikan
jikan = Jikan()

anime = jikan.anime(14719)

print(anime)