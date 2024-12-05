import kivy
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen

class SearchWindow(Screen):
    pass
class ResultWindow(Screen):
    pass
class WindowManager(ScreenManager):
    pass
kv = Builder.load_file('Windows.kv')
class AnimeApp(App):
    def build(self):
        return kv
if __name__ == '__main__':
    AnimeApp().run()


