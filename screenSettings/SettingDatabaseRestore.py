from kivy.app import App
from kivy.uix.settings import SettingItem

from kivy.lang.builder import Builder

Builder.load_string("""
<SettingDatabaseRestore>:
    WideButton:
        text: 'Restore Database Backup'
        size: root.size
        pos: root.pos
        font_size: '15sp'
        on_release: root.database_restore()
""")
class SettingDatabaseRestore(SettingItem):
    """Database backup restore widget for the settings screen."""
    def database_restore(self):
        app = App.get_running_app()
        app.database_restore()