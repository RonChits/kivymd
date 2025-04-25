import sqlite3
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen, ScreenManager
from kivymd.app import MDApp
from kivymd.uix.tab import MDTabs, MDTabsBase
from kivymd.uix.toolbar import MDToolbar
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.list import TwoLineListItem
from kivymd.uix.dialog import MDDialog
from kivy.utils import platform
from kivy.clock import Clock
from kivy.properties import StringProperty, NumericProperty, ListProperty
from kivy.config import Config
Config.set('graphics', 'maxfps', 60)


class LoginScreen(Screen):
    pass


class SignupScreen(Screen):
    pass


class MainAppScreen(Screen):
    pass


class TabConverter(Screen, MDTabsBase):
    units = {
        'Length': {
            'mm': 0.001,
            'cm': 0.01,
            'm': 1.0,
            'km': 1000.0,
            'inch': 0.0254,
            'foot': 0.3048,
            'mile': 1609.344
        },
        'Weight': {
            'mg': 0.001,
            'g': 1.0,
            'kg': 1000.0,
            'ton': 1000000.0,
            'ounce': 28.3495,
            'pound': 453.592
        },
        'Temperature': {
            '°C': 'celsius',
            '°F': 'fahrenheit',
            'K': 'kelvin'
        }
    }

    current_category = StringProperty('Length')
    from_value = NumericProperty(0)
    to_value = NumericProperty(0)
    from_unit = StringProperty('m')
    to_unit = StringProperty('cm')

    def convert(self):
        try:
            value = float(self.ids.from_value.text)
        except ValueError:
            return

        if self.current_category == 'Temperature':
            self.handle_temperature_conversion(value)
        else:
            self.handle_standard_conversion(value)

    def handle_standard_conversion(self, value):
        from_factor = self.units[self.current_category][self.from_unit]
        to_factor = self.units[self.current_category][self.to_unit]
        self.to_value = value * from_factor / to_factor
        self.ids.to_value.text = f"{self.to_value:.4f}"

    def handle_temperature_conversion(self, value):
        if self.from_unit == '°C':
            if self.to_unit == '°F':
                self.to_value = (value * 9 / 5) + 32
            elif self.to_unit == 'K':
                self.to_value = value + 273.15
            else:
                self.to_value = value
        elif self.from_unit == '°F':
            if self.to_unit == '°C':
                self.to_value = (value - 32) * 5 / 9
            elif self.to_unit == 'K':
                self.to_value = (value - 32) * 5 / 9 + 273.15
            else:
                self.to_value = value
        elif self.from_unit == 'K':
            if self.to_unit == '°C':
                self.to_value = value - 273.15
            elif self.to_unit == '°F':
                self.to_value = (value - 273.15) * 9 / 5 + 32
            else:
                self.to_value = value

        self.ids.to_value.text = f"{self.to_value:.2f}"

    def swap_units(self):
        self.from_unit, self.to_unit = self.to_unit, self.from_unit
        self.convert()


class TabCalculator(Screen, MDTabsBase):
    expression = StringProperty('')

    def button_press(self, button):
        if button == 'C':
            self.expression = ''
        elif button == '⌫':
            self.expression = self.expression[:-1]
        elif button == '=':
            self.calculate()
        else:
            self.expression += button

    def calculate(self):
        try:
            self.expression = str(eval(self.expression))
        except:
            self.expression = 'Error'


class TabToDo(Screen, MDTabsBase):
    tasks = ListProperty([])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(on_enter=self.load_tasks)

    def load_tasks(self, *args):
        app = App.get_running_app()
        if hasattr(app, 'user_data') and 'id' in app.user_data:
            try:
                app.cursor.execute(
                    "SELECT task FROM tasks WHERE user_id = ?",
                    (app.user_data['id'],))
                self.tasks = [row[0] for row in app.cursor.fetchall()]
                self.update_task_list()
            except sqlite3.Error as e:
                print(f"Error loading tasks: {e}")

    def update_task_list(self):
        if hasattr(self, 'ids') and 'task_list' in self.ids:
            self.ids.task_list.clear_widgets()
            for task in self.tasks:
                item = TwoLineListItem(
                    text=task,
                    secondary_text="Click to delete",
                    on_release=lambda x, t=task: self.delete_task(t)
                )
                self.ids.task_list.add_widget(item)

    def add_task(self):
        task_text = self.ids.task_input.text.strip()
        if task_text and hasattr(App.get_running_app(), 'user_data'):
            try:
                app = App.get_running_app()
                app.cursor.execute(
                    "INSERT INTO tasks (user_id, task) VALUES (?, ?)",
                    (app.user_data['id'], task_text))
                app.conn.commit()
                self.tasks.append(task_text)
                self.ids.task_input.text = ''
                self.update_task_list()
            except sqlite3.Error as e:
                print(f"Error adding task: {e}")

    def delete_task(self, task):
        if task in self.tasks and hasattr(App.get_running_app(), 'user_data'):
            try:
                app = App.get_running_app()
                app.cursor.execute(
                    "DELETE FROM tasks WHERE user_id = ? AND task = ?",
                    (app.user_data['id'], task))
                app.conn.commit()
                self.tasks.remove(task)
                self.update_task_list()
            except sqlite3.Error as e:
                print(f"Error deleting task: {e}")


class TabInfo(Screen, MDTabsBase):
    def show_about(self):
        about_text = """Modern KivyMD App done by Ronald Isheanesu Chitsatso\n
Features:
- User authentication
- Unit converter
- Calculator
- To-Do list
- Responsive design\n
Created with Python and KivyMD"""

        MDDialog(
            title="About This App",
            text=about_text,
            size_hint=(0.8, None)
        ).open()


class RonaldChitsatsoMake(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dialog = None
        self.user_data = {}
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.theme_style = "Light"



    def build(self):
        from kivy.clock import Clock
        Clock.max_iteration = 20
        self.screen_manager = ScreenManager()
        Builder.load_file('main.kv')

        self.login_screen = LoginScreen(name='login')
        self.signup_screen = SignupScreen(name='signup')
        self.main_app_screen = MainAppScreen(name='main_app')

        self.screen_manager.add_widget(self.login_screen)
        self.screen_manager.add_widget(self.signup_screen)
        self.screen_manager.add_widget(self.main_app_screen)

        self.screen_manager.current = 'login'
        return self.screen_manager

    def on_start(self):
        self.conn = sqlite3.connect('users.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                task TEXT,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        ''')
        self.conn.commit()

    def show_signup(self):
        self.screen_manager.current = 'signup'

    def show_login(self):
        self.screen_manager.current = 'login'

    def login(self):
        username = self.root.get_screen('login').ids.username_field.text
        password = self.root.get_screen('login').ids.password_field.text

        if not username or not password:
            self.show_dialog("Please enter both username and password.")
            return

        try:
            self.cursor.execute(
                "SELECT * FROM users WHERE username = ? AND password = ?",
                (username, password))
            user = self.cursor.fetchone()
            if user:
                self.user_data = {'username': user[1], 'email': user[2], 'id': user[0]}
                self.show_dialog(f"Login successful! Welcome, {user[1]}!")
                self.screen_manager.current = 'main_app'
            else:
                self.show_dialog("Invalid username or password.")
        except sqlite3.Error as e:
            self.show_dialog(f"Database error: {e}")

    def signup(self):
        username = self.root.get_screen('signup').ids.username_field.text
        email = self.root.get_screen('signup').ids.email_field.text
        password = self.root.get_screen('signup').ids.password_field.text

        if not username or not email or not password:
            self.show_dialog("Please fill in all fields.")
            return

        if len(password) < 8:
            self.show_dialog("Password must be at least 8 characters long.")
            return

        try:
            self.cursor.execute(
                "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                (username, email, password))
            self.conn.commit()
            self.show_dialog("Signup successful! Please log in.")
            self.screen_manager.current = 'login'
        except sqlite3.IntegrityError:
            self.show_dialog("Username or email already exists.")
        except sqlite3.Error as e:
            self.show_dialog(f"Database error: {e}")

    def show_dialog(self, text):
        if not self.dialog:
            self.dialog = MDDialog(
                text=text,
                buttons=[
                    MDRaisedButton(
                        text="OK", on_release=self.close_dialog
                    ),
                ],
            )
        else:
            self.dialog.text = text
        self.dialog.open()

    def close_dialog(self, *args):
        if self.dialog:
            self.dialog.dismiss()
        self.dialog = None

    def on_stop(self):
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()

    def logout(self):
        self.user_data.clear()
        self.screen_manager.current = 'login'
        self.show_dialog("Logged out successfully.")


if __name__ == '__main__':
    RonaldChitsatsoMake().run()