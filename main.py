import kivy
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.animation import Animation
from kivymd.app import MDApp
import numpy as np
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRectangleFlatButton
from kivymd.uix.textfield import MDTextField
from kivy.graphics import Color, Line, Rectangle
import json
import threading  # Add this import
import time
import os
import math
from kivymd.uix.slider import MDSlider
from kivy.uix.spinner import Spinner
from kivymd.uix.dialog import MDDialog
from scipy.stats import norm
import matplotlib.pyplot as plt
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
from kivy.uix.scrollview import ScrollView
from kivymd.uix.card import MDCard
from kivymd.uix.chip import MDChip

kivy.require('2.0.0')


class BaseTile1(BoxLayout):
    def __init__(self, border_width=75, border_color=(0, 0, 0.5, 0.5), **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.border_width = border_width
        self.border_color = border_color

        # Header (Optional)
        self.header = BoxLayout(size_hint_y=None, height=50, padding=10)
        self.header_label = MDLabel(text="DGVTR-Barrier", halign="center")
        self.header.add_widget(self.header_label)
        self.add_widget(self.header)

        # Content Area (Where screen-specific content will go)
        self.content_area = BoxLayout(orientation='vertical', padding=10)
        self.add_widget(self.content_area)

        # Footer (Optional)
        self.footer = BoxLayout(size_hint_y=None, height=50, padding=10)
        self.footer_label = MDLabel(text="...............", halign="center")
        self.footer.add_widget(self.footer_label)
        self.add_widget(self.footer)

        # Draw Border
        self.bind(size=self._update_border, pos=self._update_border)
        self._update_border()

    def add_content(self, widget):
        self.content_area.add_widget(widget)

    def _update_border(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self.border_color)
            Line(rectangle=(self.pos[0], self.pos[1], self.size[0], self.size[1]), width=self.border_width)


class BaseTile(BoxLayout):
    def __init__(self, border_width=15, border_color=(0, 0, 1, 1), **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.border_width = border_width
        self.border_color = border_color

        # Header (Optional)
        self.header = BoxLayout(size_hint_y=None, height=50, padding=10)
        self.header_label = MDLabel(text="DGVTR-Barrier", halign="center")
        self.header.add_widget(self.header_label)
        self.add_widget(self.header)

        # Content Area (Where screen-specific content will go)
        self.content_area = BoxLayout(orientation='vertical', padding=10)
        self.add_widget(self.content_area)

        # Footer (Optional)
        self.footer = BoxLayout(size_hint_y=None, height=50, padding=10)
        self.footer_label = MDLabel(text="...............", halign="center")
        self.footer.add_widget(self.footer_label)
        self.add_widget(self.footer)

        # Draw Border
        self.bind(size=self._update_border, pos=self._update_border)
        self._update_border()

    def add_content(self, widget):
        self.content_area.add_widget(widget)

    def _update_border(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self.border_color)
            Line(rectangle=(self.pos[0], self.pos[1], self.size[0], self.size[1]), width=self.border_width)


class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Create an instance of the BaseTile
        self.base_tile = BaseTile()
        self.add_widget(self.base_tile)

        # Add your screen-specific content to the content area of the BaseTile
        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        self.base_tile.add_content(layout)

        self.label = MDLabel(text="Barrier Option Pricing", halign="center", font_style="H5")
        layout.add_widget(self.label)

        grid = GridLayout(cols=2, spacing=5, size_hint_y=None, row_default_height=40)
        grid.bind(minimum_height=grid.setter('height'))

        self.underlying_price_slider = MDSlider(min=10, max=200, value=100)
        self.strike_price_slider = MDSlider(min=10, max=200, value=100)
        self.barrier_level_slider = MDSlider(min=10, max=200, value=150)
        self.time_to_maturity_slider = MDSlider(min=0.1, max=5, value=1, step=0.1)
        self.volatility_slider = MDSlider(min=0.01, max=1, value=0.2, step=0.01)
        self.risk_free_rate_slider = MDSlider(min=0.01, max=0.2, value=0.05, step=0.01)

        grid.add_widget(MDLabel(text="Underlying Price:"))
        grid.add_widget(self.underlying_price_slider)
        grid.add_widget(MDLabel(text="Strike Price:"))
        grid.add_widget(self.strike_price_slider)
        grid.add_widget(MDLabel(text="Barrier Level:"))
        grid.add_widget(self.barrier_level_slider)
        grid.add_widget(MDLabel(text="Time to Maturity:"))
        grid.add_widget(self.time_to_maturity_slider)
        grid.add_widget(MDLabel(text="Volatility:"))
        grid.add_widget(self.volatility_slider)
        grid.add_widget(MDLabel(text="Risk-Free Rate:"))
        grid.add_widget(self.risk_free_rate_slider)

        self.option_type_spinner = Spinner(
            text='Select Option Type',
            values=('Up-and-Out Call', 'Down-and-Out Call', 'Up-and-In Call', 'Down-and-In Call',
                    'Up-and-Out Put', 'Down-and-Out Put', 'Up-and-In Put', 'Down-and-In Put'),
            size_hint=(None, None),
            size=(200, 44),
        )
        grid.add_widget(MDLabel(text="Option Type:"))
        grid.add_widget(self.option_type_spinner)

        layout.add_widget(grid)

        self.calculate_button = MDRectangleFlatButton(text="Calculate Option Price", on_press=self.calculate_price)
        layout.add_widget(self.calculate_button)

        self.result_label = MDLabel(text="", halign="center")
        layout.add_widget(self.result_label)

        self.graph_button = MDRectangleFlatButton(text="Graph Visualization", on_press=self.go_to_graph)
        layout.add_widget(self.graph_button)

        self.sensitivity_button = MDRectangleFlatButton(text="Sensitivity Analysis", on_press=self.go_to_sensitivity)
        layout.add_widget(self.sensitivity_button)

        self.back_to_signin_button = MDRectangleFlatButton(text="Sign-Out", on_press=self.go_to_signin)
        layout.add_widget(self.back_to_signin_button)

    def calculate_price(self, instance):
        try:
            S = self.underlying_price_slider.value
            K = self.strike_price_slider.value
            H = self.barrier_level_slider.value
            T = self.time_to_maturity_slider.value
            sigma = self.volatility_slider.value
            r = self.risk_free_rate_slider.value
            option_type = self.option_type_spinner.text.lower()

            price = self.barrier_option_price(S, K, H, T, sigma, r, option_type)
            self.result_label.text = f"Option Price: {price:.4f}"
        except Exception as e:
            self.result_label.text = f"An error occurred: {e}"


    def barrier_option_price(self, S, K, H, T, sigma, r, option_type):
        """
        Calculates the price of a barrier option (call or put).

        Args:
            S: Current price of the underlying asset.
            K: Strike price.
            H: Barrier level.
            T: Time to maturity (in years).
            sigma: Volatility.
            r: Risk-free interest rate.
            option_type: String specifying the option type ("up-and-out call", "down-and-out call",
                         "up-and-in call", "down-and-in call", "up-and-out put", "down-and-out put",
                         "up-and-in put", "down-and-in put").

        Returns:
            The price of the barrier option, or 0.0 if the option type is invalid.
        """

        d1 = (math.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * math.sqrt(T))
        d2 = d1 - sigma * math.sqrt(T)

        d1H = (math.log(H / S) + (r + 0.5 * sigma**2) * T) / (sigma * math.sqrt(T))
        d2H = d1H - sigma * math.sqrt(T)

        d1K = (math.log(H**2 / (S * K)) + (r + 0.5 * sigma**2) * T) / (sigma * math.sqrt(T))
        d2K = d1K - sigma * math.sqrt(T)

        d1KH = (math.log(H / S) + (r + 0.5 * sigma**2) * T) / (sigma * math.sqrt(T))
        d2KH = d1KH - sigma * math.sqrt(T)

        if "up-and-out call" in option_type:
            if H <= K:
                return 0.0
            if S >= H:
                return 0.0

            return (S * norm.cdf(d1) - K * math.exp(-r * T) * norm.cdf(d2) -
                    S * (H / S)**(2 * r / sigma**2) * norm.cdf(d1K) +
                    K * math.exp(-r * T) * (H / S)**(2 * r / sigma**2 - 2) * norm.cdf(d2K))

        elif "down-and-out call" in option_type:
            if H >= K:
                return S * norm.cdf(d1) - K * math.exp(-r * T) * norm.cdf(d2)
            if S <= H:
                return 0.0

            return (S * norm.cdf(d1) - K * math.exp(-r * T) * norm.cdf(d2) -
                    S * (H / S)**(2 * r / sigma**2) * norm.cdf(-d1K) +
                    K * math.exp(-r * T) * (H / S)**(2 * r / sigma**2 - 2) * norm.cdf(-d2K))

        elif "up-and-in call" in option_type:
            if H <= K:
                return S * norm.cdf(d1) - K * math.exp(-r * T) * norm.cdf(d2)
            if S >= H:
                return S * norm.cdf(d1) - K * math.exp(-r * T) * norm.cdf(d2)

            return (S * (H / S)**(2 * r / sigma**2) * norm.cdf(d1K) -
                    K * math.exp(-r * T) * (H / S)**(2 * r / sigma**2 - 2) * norm.cdf(d2K))

        elif "down-and-in call" in option_type:
             if H >= K:
                return 0.0
             if S <= H:
                return S * norm.cdf(d1) - K * math.exp(-r * T) * norm.cdf(d2)

             return (S * (H / S)**(2 * r / sigma**2) * norm.cdf(-d1K) -
                    K * math.exp(-r * T) * (H / S)**(2 * r / sigma**2 - 2) * norm.cdf(-d2K))

        elif "up-and-out put" in option_type:
            if H <= K:
                return K * math.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
            if S >= H:
                return 0.0

            return (K * math.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1) -
                    K * math.exp(-r * T) * (H / S)**(2 * r / sigma**2 - 2) * norm.cdf(-d2K) +
                    S * (H / S)**(2 * r / sigma**2) * norm.cdf(-d1K))

        elif "down-and-out put" in option_type:
            if H >= K:
                return 0.0
            if S <= H:
                return 0.0

            return (K * math.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1) -
                    K * math.exp(-r * T) * (H / S)**(2 * r / sigma**2 - 2) * norm.cdf(d2K) +
                    S * (H / S)**(2 * r / sigma**2) * norm.cdf(d1K))

        elif "up-and-in put" in option_type:
            if H <= K:
                return 0.0
            if S >= H:
                return K * math.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)

            return (K * math.exp(-r * T) * (H / S)**(2 * r / sigma**2 - 2) * norm.cdf(-d2K) -
                    S * (H / S)**(2 * r / sigma**2) * norm.cdf(-d1K))

        elif "down-and-in put" in option_type:
            if H >= K:
                return K * math.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
            if S <= H:
                return K * math.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)

            return (K * math.exp(-r * T) * (H / S)**(2 * r / sigma**2 - 2) * norm.cdf(d2K) -
                    S * (H / S)**(2 * r / sigma**2) * norm.cdf(d1K))

        else:
            return 0.0

    def calculate_delta(self, S, K, H, T, sigma, r, option_type):
        # Numerical approximation of delta
        dS = 0.01  # Small change in S
        price_up = self.barrier_option_price(S + dS, K, H, T, sigma, r, option_type)
        price_down = self.barrier_option_price(S - dS, K, H, T, sigma, r, option_type)
        return (price_up - price_down) / (2 * dS)

    def calculate_gamma(self, S, K, H, T, sigma, r, option_type):
        # Numerical approximation of gamma
        dS = 0.01
        price_up = self.barrier_option_price(S + dS, K, H, T, sigma, r, option_type)
        price_mid = self.barrier_option_price(S, K, H, T, sigma, r, option_type)
        price_down = self.barrier_option_price(S - dS, K, H, T, sigma, r, option_type)
        return (price_up - 2 * price_mid + price_down) / (dS ** 2)

    def calculate_vega(self, S, K, H, T, sigma, r, option_type):
        # Numerical approximation of vega
        d_sigma = 0.01
        price_up = self.barrier_option_price(S, K, H, T, sigma + d_sigma, r, option_type)
        price_down = self.barrier_option_price(S, K, H, T, sigma - d_sigma, r, option_type)
        return (price_up - price_down) / (2 * d_sigma)

    def go_to_greeks(self, instance):  # Add this
        self.manager.current = 'greeks'

    def go_to_graph(self, instance):
        self.manager.current = 'graph'

    def go_to_sensitivity(self, instance):
        self.manager.current = 'sensitivity'

    def go_to_signin(self, instance):  # Added function
        self.manager.current = 'signin'



class GraphScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Create an instance of the BaseTile
        self.base_tile = BaseTile()
        self.add_widget(self.base_tile)

        # Add your screen-specific content to the content area of the BaseTile
        layout = BoxLayout(orientation='vertical')
        self.base_tile.add_content(layout)

        self.plot_layout = BoxLayout(orientation='vertical', size_hint_y=0.8)
        layout.add_widget(self.plot_layout)

        self.graph_button = MDRectangleFlatButton(text="Generate Graphs", on_press=self.generate_graphs)
        layout.add_widget(self.graph_button)

        self.back_button = MDRectangleFlatButton(text="Back", on_press=self.go_back)
        layout.add_widget(self.back_button)

        self.sensitivity_button = MDRectangleFlatButton(text="Sensitivity Analysis",
                                                        on_press=self.go_to_sensitivity)
        layout.add_widget(self.sensitivity_button)

        self.back_to_signin_button = MDRectangleFlatButton(text="Sign-Out", on_press=self.go_to_signin)
        layout.add_widget(self.back_to_signin_button)

    def calculate_delta(self, S, K, H, T, sigma, r, option_type):
        # Numerical approximation of delta
        dS = 0.01  # Small change in S
        price_up = self.barrier_option_price(S + dS, K, H, T, sigma, r, option_type)
        price_down = self.barrier_option_price(S - dS, K, H, T, sigma, r, option_type)
        return (price_up - price_down) / (2 * dS)

    def calculate_gamma(self, S, K, H, T, sigma, r, option_type):
        # Numerical approximation of gamma
        dS = 0.01
        price_up = self.barrier_option_price(S + dS, K, H, T, sigma, r, option_type)
        price_mid = self.barrier_option_price(S, K, H, T, sigma, r, option_type)
        price_down = self.barrier_option_price(S - dS, K, H, T, sigma, r, option_type)
        return (price_up - 2 * price_mid + price_down) / (dS ** 2)

    def calculate_vega(self, S, K, H, T, sigma, r, option_type):
        # Numerical approximation of vega
        d_sigma = 0.01
        price_up = self.barrier_option_price(S, K, H, T, sigma + d_sigma, r, option_type)
        price_down = self.barrier_option_price(S, K, H, T, sigma - d_sigma, r, option_type)
        return (price_up - price_down) / (2 * d_sigma)

    def generate_graphs(self, instance):
        main_screen = self.manager.get_screen('main')
        S = main_screen.underlying_price_slider.value
        K = main_screen.strike_price_slider.value
        H = main_screen.barrier_level_slider.value
        T = main_screen.time_to_maturity_slider.value
        sigma = main_screen.volatility_slider.value
        r = main_screen.risk_free_rate_slider.value
        option_type = main_screen.option_type_spinner.text.lower()

        self.plot_layout.clear_widgets()

        # Payoff Diagram
        S_values = range(int(K * 0.5), int(K * 1.5))
        payoffs = []
        for s in S_values:
            payoff = 0
            if "call" in option_type:
                if "out" in option_type and s > H:
                    payoff = 0
                elif "in" in option_type and s < H:
                    payoff = 0
                else:
                    payoff = max(s - K, 0)
            elif "put" in option_type:
                if "out" in option_type and s < H:
                    payoff = 0
                elif "in" in option_type and s > H:
                    payoff = 0
                else:
                    payoff = max(K - s, 0)

            payoffs.append(payoff)

        fig, ax = plt.subplots(figsize=(8, 6))  # Increased figure size
        ax.plot(S_values, payoffs)
        ax.set_title("Payoff Diagram")
        ax.set_xlabel("Underlying Price")
        ax.set_ylabel("Payoff")
        self.plot_layout.add_widget(FigureCanvasKivyAgg(fig))

        # Option Value Graph (vs Underlying Price)
        S_values = range(int(K * 0.5), int(K * 1.5))
        option_prices = []
        for s in S_values:
            price = main_screen.barrier_option_price(s, K, H, T, sigma, r, option_type)
            option_prices.append(price)

        fig2, ax2 = plt.subplots(figsize=(8, 6))  # Increased figure size
        ax2.plot(S_values, option_prices)
        ax2.set_title("Option Value vs Underlying Price")
        ax2.set_xlabel("Underlying Price")
        ax2.set_ylabel("Option Value")
        self.plot_layout.add_widget(FigureCanvasKivyAgg(fig2))

    def go_back(self, instance):
        self.manager.current = 'main'

    def go_to_sensitivity(self, instance):
        self.manager.current = 'sensitivity'

    def go_to_signin(self, instance):
        self.manager.current = 'signin'


class SignInScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Use BaseTile1 as the base layout
        self.base_tile = BaseTile1()
        self.add_widget(self.base_tile)

        # Create the GridLayout and add it to the content area of BaseTile1
        self.layout = GridLayout(
            cols=2,
            rows=10,
            spacing=[0, 15],
            padding=10,
            opacity=0.7,
            size_hint=(0.9, 0.3),
            col_default_width=200,
            row_default_height=50,
            col_force_default=True,
            row_force_default=True,
        )
        self.layout.pos_hint = {'center_x': 0.82, 'center_y': 0.1}

        self.label = MDLabel(
            halign="center",
            text="Welcome.",
            font_size=50,
            font_name="Georgia",
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),
        )
        self.layout.add_widget(self.label)
        self.layout.add_widget(Label())
        self.layout.add_widget(Label())
        self.layout.add_widget(Label())
        self.username_input = MDTextField(
            hint_text="    Username",
            halign="center",
        )
        self.layout.add_widget(self.username_input)
        self.layout.add_widget(Label())

        self.password_input = MDTextField(
            hint_text="     Password",
            halign="center",
            password=True,
        )
        self.layout.add_widget(self.password_input)
        self.layout.add_widget(Label())

        self.submit_button = MDRectangleFlatButton(
            text="Sign In", font_size=15, font_name="Georgia"
        )
        self.submit_button.bind(on_press=self.validate_credentials)
        self.layout.add_widget(self.submit_button)

        self.signup_button = MDRectangleFlatButton(
            text="Sign Up", font_size=15, font_name="Georgia"
        )
        self.signup_button.bind(on_press=self.go_to_signup)
        self.layout.add_widget(self.signup_button)

        self.error_label = MDLabel(
            text="", halign="center", theme_text_color="Error"
        )
        self.layout.add_widget(self.error_label)

        # Add the layout to the content area of the BaseTile1
        self.base_tile.add_content(self.layout)




    def calculate_delta(self, S, K, H, T, sigma, r, option_type):
        # Numerical approximation of delta
        dS = 0.01  # Small change in S
        price_up = self.barrier_option_price(S + dS, K, H, T, sigma, r, option_type)
        price_down = self.barrier_option_price(S - dS, K, H, T, sigma, r, option_type)
        return (price_up - price_down) / (2 * dS)

    def calculate_gamma(self, S, K, H, T, sigma, r, option_type):
        # Numerical approximation of gamma
        dS = 0.01
        price_up = self.barrier_option_price(S + dS, K, H, T, sigma, r, option_type)
        price_mid = self.barrier_option_price(S, K, H, T, sigma, r, option_type)
        price_down = self.barrier_option_price(S - dS, K, H, T, sigma, r, option_type)
        return (price_up - 2 * price_mid + price_down) / (dS ** 2)

    def calculate_vega(self, S, K, H, T, sigma, r, option_type):
        # Numerical approximation of vega
        d_sigma = 0.01
        price_up = self.barrier_option_price(S, K, H, T, sigma + d_sigma, r, option_type)
        price_down = self.barrier_option_price(S, K, H, T, sigma - d_sigma, r, option_type)
        return (price_up - price_down) / (2 * d_sigma)

    def validate_credentials(self, instance):
        credentials = load_credentials()
        username = self.username_input.text
        password = self.password_input.text

        if username and password and username in credentials and credentials[username] == password:
            self.manager.current = "main"
        else:
            self.show_error_dialog("Incorrect or Blank Credentials")

    def go_to_signup(self, instance):
        self.manager.current = 'signup'

    def show_error_dialog(self, text):
        from kivy.app import App
        if not hasattr(self, 'dialog') or not self.dialog:
            self.dialog = MDDialog(
                text=text,
                buttons=[
                    MDRectangleFlatButton(
                        text="OK", text_color=App.get_running_app().theme_cls.primary_color,
                        on_release=self.close_dialog
                    ),
                ],
            )
        self.dialog.text = text
        self.dialog.open()

    def close_dialog(self, obj):
        self.dialog.dismiss()


class SignUpScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.layout = GridLayout(
            cols=1,
            rows=8,
            spacing=[0, 15],
            padding=10,
            opacity=0.7,
            size_hint=(0.9, 0.3),
            col_default_width=200,
            row_default_height=50,
            col_force_default=True,
            row_force_default=True,
        )
        self.layout.pos_hint = {'center_x': 0.85, 'center_y': 0.7}

        self.label = MDLabel(
            halign="center",
            text="Sign Up",
            font_size=46,
            font_name="Georgia",
            theme_text_color="Custom",
            text_color=(0, 0, 1, 1),
        )
        self.layout.add_widget(self.label)

        self.new_username_input = MDTextField(hint_text="New Username")
        self.layout.add_widget(self.new_username_input)

        self.new_password_input = MDTextField(hint_text="New Password", password=True)
        self.layout.add_widget(self.new_password_input)

        self.signup_submit_button = MDRectangleFlatButton(
            text="Create Account", font_size=20, font_name="Georgia"
        )
        self.signup_submit_button.bind(on_press=self.create_account)
        self.layout.add_widget(self.signup_submit_button)

        self.signup_error_label = MDLabel(
            text="", halign="center", theme_text_color="Error"
        )
        self.layout.add_widget(self.signup_error_label)
        self.add_widget(self.layout)

    def create_account(self, instance):
        username = self.new_username_input.text
        password = self.new_password_input.text
        if username and password:
            credentials = load_credentials()
            credentials[username] = password
            save_credentials(credentials)
            self.manager.current = "signin"
        else:
            self.signup_error_label.text = "Please fill in all fields."



def get_credentials_file():
    app_dir = App.get_running_app().user_data_dir
    if not os.path.exists(app_dir):
        os.makedirs(app_dir)
    return os.path.join(app_dir, 'credentials.json')


def load_credentials():
    credentials_file = get_credentials_file()
    try:
        with open(credentials_file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        return {}


def save_credentials(credentials):
    credentials_file = get_credentials_file()
    with open(credentials_file, 'w') as f:
        json.dump(credentials, f)


class SensitivityScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.sensitivity_data = {}

        # Use BaseTile as the base layout
        self.base_tile = BaseTile()
        self.add_widget(self.base_tile)

        # Add your screen-specific content to the content area of BaseTile
        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        self.base_tile.add_content(layout)

        self.label = MDLabel(text="Sensitivity Analysis", halign="center", font_style="H5")
        layout.add_widget(self.label)

        self.sensitivity_param_spinner = Spinner(
            text='Select Parameter',
            values=('Underlying Price', 'Strike Price', 'Barrier Level', 'Time to Maturity', 'Volatility', 'Risk-Free Rate'),
            size_hint=(None, None),
            size=(200, 44),
        )
        layout.add_widget(self.sensitivity_param_spinner)

        self.num_points_input = MDTextField(
            hint_text="Enter Number of Points",
            input_type='number',
            input_filter='int',
            text='10'  # Default value
        )
        layout.add_widget(self.num_points_input)

        self.sensitivity_results_label = MDLabel(text="", halign="center", valign="top", size_hint_y=None)
        layout.add_widget(self.sensitivity_results_label)

        greeks_button = MDRectangleFlatButton(text="Greeks Screen", on_press=self.go_to_greeks)  # Add this
        layout.add_widget(greeks_button)

        self.back_button = MDRectangleFlatButton(text="Back", on_press=self.go_back)
        layout.add_widget(self.back_button)

        self.back_to_signin_button = MDRectangleFlatButton(text="Back to Sign In", on_press=self.go_to_signin)
        layout.add_widget(self.back_to_signin_button)


    def go_to_greeks(self, instance):
        self.manager.current = 'greeks'

    def calculate_delta(self, S, K, H, T, sigma, r, option_type):
        # Numerical approximation of delta
        dS = 0.01  # Small change in S
        price_up = self.barrier_option_price(S + dS, K, H, T, sigma, r, option_type)
        price_down = self.barrier_option_price(S - dS, K, H, T, sigma, r, option_type)
        return (price_up - price_down) / (2 * dS)


    def barrier_option_price(self, S, K, H, T, sigma, r, option_type):
        """
        Calculates the price of a barrier option (call or put).

        Args:
            S: Current price of the underlying asset.
            K: Strike price.
            H: Barrier level.
            T: Time to maturity (in years).
            sigma: Volatility.
            r: Risk-free interest rate.
            option_type: String specifying the option type ("up-and-out call", "down-and-out call",
                         "up-and-in call", "down-and-in call", "up-and-out put", "down-and-out put",
                         "up-and-in put", "down-and-in put").

        Returns:
            The price of the barrier option, or 0.0 if the option type is invalid.
        """

        d1 = (math.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * math.sqrt(T))
        d2 = d1 - sigma * math.sqrt(T)

        d1H = (math.log(H / S) + (r + 0.5 * sigma**2) * T) / (sigma * math.sqrt(T))
        d2H = d1H - sigma * math.sqrt(T)

        d1K = (math.log(H**2 / (S * K)) + (r + 0.5 * sigma**2) * T) / (sigma * math.sqrt(T))
        d2K = d1K - sigma * math.sqrt(T)

        d1KH = (math.log(H / S) + (r + 0.5 * sigma**2) * T) / (sigma * math.sqrt(T))
        d2KH = d1KH - sigma * math.sqrt(T)

        if "up-and-out call" in option_type:
            if H <= K:
                return 0.0
            if S >= H:
                return 0.0

            return (S * norm.cdf(d1) - K * math.exp(-r * T) * norm.cdf(d2) -
                    S * (H / S)**(2 * r / sigma**2) * norm.cdf(d1K) +
                    K * math.exp(-r * T) * (H / S)**(2 * r / sigma**2 - 2) * norm.cdf(d2K))

        elif "down-and-out call" in option_type:
            if H >= K:
                return S * norm.cdf(d1) - K * math.exp(-r * T) * norm.cdf(d2)
            if S <= H:
                return 0.0

            return (S * norm.cdf(d1) - K * math.exp(-r * T) * norm.cdf(d2) -
                    S * (H / S)**(2 * r / sigma**2) * norm.cdf(-d1K) +
                    K * math.exp(-r * T) * (H / S)**(2 * r / sigma**2 - 2) * norm.cdf(-d2K))

        elif "up-and-in call" in option_type:
            if H <= K:
                return S * norm.cdf(d1) - K * math.exp(-r * T) * norm.cdf(d2)
            if S >= H:
                return S * norm.cdf(d1) - K * math.exp(-r * T) * norm.cdf(d2)

            return (S * (H / S)**(2 * r / sigma**2) * norm.cdf(d1K) -
                    K * math.exp(-r * T) * (H / S)**(2 * r / sigma**2 - 2) * norm.cdf(d2K))

        elif "down-and-in call" in option_type:
             if H >= K:
                return 0.0
             if S <= H:
                return S * norm.cdf(d1) - K * math.exp(-r * T) * norm.cdf(d2)

             return (S * (H / S)**(2 * r / sigma**2) * norm.cdf(-d1K) -
                    K * math.exp(-r * T) * (H / S)**(2 * r / sigma**2 - 2) * norm.cdf(-d2K))

        elif "up-and-out put" in option_type:
            if H <= K:
                return K * math.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
            if S >= H:
                return 0.0

            return (K * math.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1) -
                    K * math.exp(-r * T) * (H / S)**(2 * r / sigma**2 - 2) * norm.cdf(-d2K) +
                    S * (H / S)**(2 * r / sigma**2) * norm.cdf(-d1K))

        elif "down-and-out put" in option_type:
            if H >= K:
                return 0.0
            if S <= H:
                return 0.0

            return (K * math.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1) -
                    K * math.exp(-r * T) * (H / S)**(2 * r / sigma**2 - 2) * norm.cdf(d2K) +
                    S * (H / S)**(2 * r / sigma**2) * norm.cdf(d1K))

        elif "up-and-in put" in option_type:
            if H <= K:
                return 0.0
            if S >= H:
                return K * math.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)

            return (K * math.exp(-r * T) * (H / S)**(2 * r / sigma**2 - 2) * norm.cdf(-d2K) -
                    S * (H / S)**(2 * r / sigma**2) * norm.cdf(-d1K))

        elif "down-and-in put" in option_type:
            if H >= K:
                return K * math.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
            if S <= H:
                return K * math.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)

            return (K * math.exp(-r * T) * (H / S)**(2 * r / sigma**2 - 2) * norm.cdf(d2K) -
                    S * (H / S)**(2 * r / sigma**2) * norm.cdf(d1K))

        else:
            return 0.0

    def calculate_gamma(self, S, K, H, T, sigma, r, option_type):
        # Numerical approximation of gamma
        dS = 0.01
        price_up = self.barrier_option_price(S + dS, K, H, T, sigma, r, option_type)
        price_mid = self.barrier_option_price(S, K, H, T, sigma, r, option_type)
        price_down = self.barrier_option_price(S - dS, K, H, T, sigma, r, option_type)
        return (price_up - 2 * price_mid + price_down) / (dS ** 2)

    def calculate_vega(self, S, K, H, T, sigma, r, option_type):
        # Numerical approximation of vega
        d_sigma = 0.01
        price_up = self.barrier_option_price(S, K, H, T, sigma + d_sigma, r, option_type)
        price_down = self.barrier_option_price(S, K, H, T, sigma - d_sigma, r, option_type)
        return (price_up - price_down) / (2 * d_sigma)

    def generate_sensitivity_graph(self, instance):
        main_screen = self.manager.get_screen('main')
        S = main_screen.underlying_price_slider.value
        K = main_screen.strike_price_slider.value
        H = main_screen.barrier_level_slider.value
        T = main_screen.time_to_maturity_slider.value
        sigma = main_screen.volatility_slider.value
        r = main_screen.risk_free_rate_slider.value
        option_type = main_screen.option_type_spinner.text.lower()

        param_name = self.sensitivity_param_spinner.text
        num_points_str = self.num_points_input.text
        if not num_points_str.isdigit():
            self.sensitivity_results_label.text = "Error: Please enter a valid number for points."
            return
        num_points = int(num_points_str)
        if num_points <= 1:
            self.sensitivity_results_label.text = "Error: Number of points must be greater than 1."
            return

        param_values = []
        option_prices = []
        greek_values = []

        if param_name == 'Underlying Price':
            param_values = np.linspace(S * 0.8, S * 1.2, num_points)  # Vary +/- 20%
            for s in param_values:
                price = main_screen.barrier_option_price(s, K, H, T, sigma, r, option_type)
                option_prices.append(price)
            delta = self.calculate_delta(S, K, H, T, sigma, r, option_type)
            gamma = self.calculate_gamma(S, K, H, T, sigma, r, option_type)
            vega = self.calculate_vega(S, K, H, T, sigma, r, option_type)
            greek_values = [(delta, gamma, vega)] * num_points  # same greeks for all points

        elif param_name == 'Strike Price':
            param_values = np.linspace(K * 0.8, K * 1.2, num_points)
            for k in param_values:
                price = main_screen.barrier_option_price(S, k, H, T, sigma, r, option_type)
                option_prices.append(price)
            # greeks
            delta = self.calculate_delta(S, K, H, T, sigma, r, option_type)
            gamma = self.calculate_gamma(S, K, H, T, sigma, r, option_type)
            vega = self.calculate_vega(S, K, H, T, sigma, r, option_type)
            greek_values = [(delta, gamma, vega)] * num_points

        elif param_name == 'Barrier Level':
            param_values = np.linspace(H * 0.8, H * 1.2, num_points)
            for h in param_values:
                price = main_screen.barrier_option_price(S, K, h, T, sigma, r, option_type)
                option_prices.append(price)
            # greeks
            delta = self.calculate_delta(S, K, H, T, sigma, r, option_type)
            gamma = self.calculate_gamma(S, K, H, T, sigma, r, option_type)
            vega = self.calculate_vega(S, K, H, T, sigma, r, option_type)
            greek_values = [(delta, gamma, vega)] * num_points

        elif param_name == 'Time to Maturity':
            param_values = np.linspace(T * 0.5, T * 1.5, num_points)
            for t in param_values:
                price = main_screen.barrier_option_price(S, K, H, t, sigma, r, option_type)
                option_prices.append(price)
            # greeks
            delta = self.calculate_delta(S, K, H, T, sigma, r, option_type)
            gamma = self.calculate_gamma(S, K, H, T, sigma, r, option_type)
            vega = self.calculate_vega(S, K, H, T, sigma, r, option_type)
            greek_values = [(delta, gamma, vega)] * num_points

        elif param_name == 'Volatility':
            param_values = np.linspace(sigma * 0.5, sigma * 1.5, num_points)
            for vol in param_values:
                price = main_screen.barrier_option_price(S, K, H, T, vol, r, option_type)
                option_prices.append(price)
            # greeks
            delta = self.calculate_delta(S, K, H, T, sigma, r, option_type)
            gamma = self.calculate_gamma(S, K, H, T, sigma, r, option_type)
            vega = self.calculate_vega(S, K, H, T, sigma, r, option_type)
            greek_values = [(delta, gamma, vega)] * num_points

        elif param_name == 'Risk-Free Rate':
            param_values = np.linspace(r * 0.5, r * 1.5, num_points)
            for rate in param_values:
                price = main_screen.barrier_option_price(S, K, H, T, sigma, rate, option_type)
                option_prices.append(price)
            # greeks
            delta = self.calculate_delta(S, K, H, T, sigma, r, option_type)
            gamma = self.calculate_gamma(S, K, H, T, sigma, r, option_type)
            vega = self.calculate_vega(S, K, H, T, sigma, r, option_type)
            greek_values = [(delta, gamma, vega)] * num_points

        else:
            self.sensitivity_results_label.text = "Error: Invalid parameter selected."
            return

        self.sensitivity_results_label.text = f"Sensitivity analysis for {param_name} completed."

        # Store the data for graphing
        self.sensitivity_data = {
            'param_name': param_name,
            'param_values': param_values,
            'option_prices': option_prices,
            'greek_values': greek_values
        }

        # update graph screen
        if self.graph_screen:
           self.graph_screen.sensitivity_data = self.sensitivity_data

        # Switch to the graph screen to display the graph
        self.manager.current = 'graph'

    def go_back(self, instance):
        self.manager.current = 'main'

    def go_to_signin(self, instance):
        self.manager.current = 'signin'


class GreeksScreen(Screen):
    def display_single_greeks(self, instance=None):
        main_screen = self.manager.get_screen('main')
        if main_screen is None:
            print("Error: MainScreen not found!")
            return
        self.update_greeks_display()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Use BaseTile as the base layout
        self.base_tile = BaseTile()
        self.add_widget(self.base_tile)

        # Add your screen-specific content to the content area of BaseTile
        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        self.base_tile.add_content(layout)

        self.title_label = MDLabel(text="Option Greeks Analysis", halign="center", font_style="H4")
        layout.add_widget(self.title_label)

        # Container for displaying Greeks
        self.greeks_container = BoxLayout(orientation='vertical', spacing=15, padding=10)
        layout.add_widget(self.greeks_container)

        buttons_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=50)
        self.calculate_sensitivity_button = MDRectangleFlatButton(text="Calculate Sensitivity",
                                                                  on_press=self.calculate_sensitivity)
        buttons_layout.add_widget(self.calculate_sensitivity_button)

        self.calculate_greeks_button = MDRectangleFlatButton(text="Calculate Single Greeks",
                                                             on_press=self.display_single_greeks)
        buttons_layout.add_widget(self.calculate_greeks_button)

        layout.add_widget(buttons_layout)

        self.back_button = MDRectangleFlatButton(text="Back to Main", on_press=self.go_back)
        layout.add_widget(self.back_button)
        self.sensitivity_data = None

    def on_pre_enter(self, *args):
        self.update_greeks_display()

    def update_greeks_display(self):
        self.greeks_container.clear_widgets()

        if self.sensitivity_data:
            self.display_sensitivity_greeks()
        else:
            self.display_single_greeks()

    def calculate_sensitivity(self, instance=None):
        main_screen = self.manager.get_screen('main')
        sens_screen = self.manager.get_screen('sensitivity')
        S = main_screen.underlying_price_slider.value
        K = main_screen.strike_price_slider.value
        H = main_screen.barrier_level_slider.value
        T = main_screen.time_to_maturity_slider.value
        sigma = main_screen.volatility_slider.value
        r = main_screen.risk_free_rate_slider.value
        option_type = main_screen.option_type_spinner.text.lower()

        param_name = sens_screen.sensitivity_param_spinner.text
        num_points_str = sens_screen.num_points_input.text
        if not num_points_str.isdigit():
            return
        num_points = int(num_points_str)
        if num_points <= 1:
            return

        param_values = []
        greek_values = []

        if param_name == 'Underlying Price':
            param_values = np.linspace(S * 0.8, S * 1.2, num_points)
            for s in param_values:
                delta = self.calculate_delta(s, K, H, T, sigma, r, option_type)
                gamma = self.calculate_gamma(s, K, H, T, sigma, r, option_type)
                vega = self.calculate_vega(s, K, H, T, sigma, r, option_type)
                greek_values.append((delta, gamma, vega))

        elif param_name == 'Strike Price':
            param_values = np.linspace(K * 0.8, K * 1.2, num_points)
            for k in param_values:
                delta = self.calculate_delta(S, k, H, T, sigma, r, option_type)
                gamma = self.calculate_gamma(S, k, H, T, sigma, r, option_type)
                vega = self.calculate_vega(S, k, H, T, sigma, r, option_type)
                greek_values.append((delta, gamma, vega))

        elif param_name == 'Barrier Level':
            param_values = np.linspace(H * 0.8, H * 1.2, num_points)
            for h in param_values:
                delta = self.calculate_delta(S, K, h, T, sigma, r, option_type)
                gamma = self.calculate_gamma(S, K, h, T, sigma, r, option_type)
                vega = self.calculate_vega(S, K, h, T, sigma, r, option_type)
                greek_values.append((delta, gamma, vega))

        elif param_name == 'Time to Maturity':
            param_values = np.linspace(T * 0.5, T * 1.5, num_points)
            for t in param_values:
                delta = self.calculate_delta(S, K, H, t, sigma, r, option_type)
                gamma = self.calculate_gamma(S, K, H, t, sigma, r, option_type)
                vega = self.calculate_vega(S, K, H, t, sigma, r, option_type)
                greek_values.append((delta, gamma, vega))

        elif param_name == 'Volatility':
            param_values = np.linspace(sigma * 0.5, sigma * 1.5, num_points)
            for vol in param_values:
                delta = self.calculate_delta(S, K, H, T, vol, r, option_type)
                gamma = self.calculate_gamma(S, K, H, T, vol, r, option_type)
                vega = self.calculate_vega(S, K, H, T, vol, r, option_type)
                greek_values.append((delta, gamma, vega))

        elif param_name == 'Risk-Free Rate':
            param_values = np.linspace(r * 0.5, r * 1.5, num_points)
            for rate in param_values:
                delta = self.calculate_delta(S, K, H, T, sigma, rate, option_type)
                gamma = self.calculate_gamma(S, K, H, T, sigma, rate, option_type)
                vega = self.calculate_vega(S, K, H, T, sigma, rate, option_type)
                greek_values.append((delta, gamma, vega))

        self.sensitivity_data = {
            'param_name': param_name,
            'param_values': param_values,
            'greek_values': greek_values
        }
        self.update_greeks_display()

    def display_single_greeks(self, instance=None):
        main_screen = self.manager.get_screen('main')
        S = main_screen.underlying_price_slider.value
        K = main_screen.strike_price_slider.value
        H = main_screen.barrier_level_slider.value
        T = main_screen.time_to_maturity_slider.value
        sigma = main_screen.volatility_slider.value
        r = main_screen.risk_free_rate_slider.value
        option_type = main_screen.option_type_spinner.text.lower()

        delta = self.calculate_delta(S, K, H, T, sigma, r, option_type)
        gamma = self.calculate_gamma(S, K, H, T, sigma, r, option_type)
        vega = self.calculate_vega(S, K, H, T, sigma, r, option_type)

        self.add_greek_label("Delta", delta)
        self.add_greek_label("Gamma", gamma)
        self.add_greek_label("Vega", vega)

    def display_sensitivity_greeks(self, instance=None):
        param_name = self.sensitivity_data['param_name']
        param_values = self.sensitivity_data['param_values']
        greek_values = self.sensitivity_data['greek_values']

        title_label = MDLabel(text=f"Greeks Sensitivity: {param_name}", halign="center", font_style="H5")
        self.greeks_container.add_widget(title_label)

        # Headers
        headers_layout = BoxLayout(orientation='horizontal', spacing=10)
        headers_layout.add_widget(MDLabel(text=param_name, halign='center'))
        headers_layout.add_widget(MDLabel(text="Delta", halign='center'))
        headers_layout.add_widget(MDLabel(text="Gamma", halign='center'))
        headers_layout.add_widget(MDLabel(text="Vega", halign='center'))
        self.greeks_container.add_widget(headers_layout)

        for i, param_value in enumerate(param_values):
            delta, gamma, vega = greek_values[i]
            data_layout = BoxLayout(orientation='horizontal', spacing=10)
            data_layout.add_widget(MDLabel(text=f"{param_value:.4f}", halign='center'))
            data_layout.add_widget(MDLabel(text=f"{delta:.4f}", halign='center'))
            data_layout.add_widget(MDLabel(text=f"{gamma:.4f}", halign='center'))
            data_layout.add_widget(MDLabel(text=f"{vega:.4f}", halign='center'))
            self.greeks_container.add_widget(data_layout)

    def add_greek_label(self, greek_name, greek_value):
        label = MDLabel(text=f"{greek_name}: {greek_value:.4f}")
        self.greeks_container.add_widget(label)

    def calculate_delta(self, S, K, H, T, sigma, r, option_type):
        dS = 0.01
        price_up = self.barrier_option_price(S + dS, K, H, T, sigma, r, option_type)
        price_down = self.barrier_option_price(S - dS, K, H, T, sigma, r, option_type)
        return (price_up - price_down) / (2 * dS)

    def calculate_gamma(self, S, K, H, T, sigma, r, option_type):
        dS = 0.01
        price_up = self.barrier_option_price(S + dS, K, H, T, sigma, r, option_type)
        price_mid = self.barrier_option_price(S, K, H, T, sigma, r, option_type)
        price_down = self.barrier_option_price(S - dS, K, H, T, sigma, r, option_type)
        return (price_up - (2 * price_mid) + price_down) / (dS ** 2)

    def calculate_vega(self, S, K, H, T, sigma, r, option_type):
        d_sigma = 0.01
        price_up = self.barrier_option_price(S, K, H, T, sigma + d_sigma, r, option_type)
        price_down = self.barrier_option_price(S, K, H, T, sigma - d_sigma, r, option_type)
        return (price_up - price_down) / (2 * d_sigma)

    def barrier_option_price(self, S, K, H, T, sigma, r, option_type):
        """
        Calculates the price of a barrier option (call or put).

        Args:
            S: Current price of the underlying asset.
            K: Strike price.
            H: Barrier level.
            T: Time to maturity (in years).
            sigma: Volatility.
            r: Risk-free interest rate.
            option_type: String specifying the option type ("up-and-out call", "down-and-out call",
                         "up-and-in call", "down-and-in call", "up-and-out put", "down-and-out put",
                         "up-and-in put", "down-and-in put").

        Returns:
            The price of the barrier option, or 0.0 if the option type is invalid.
        """

        d1 = (math.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * math.sqrt(T))
        d2 = d1 - sigma * math.sqrt(T)

        d1H = (math.log(H / S) + (r + 0.5 * sigma**2) * T) / (sigma * math.sqrt(T))
        d2H = d1H - sigma * math.sqrt(T)

        d1K = (math.log(H**2 / (S * K)) + (r + 0.5 * sigma**2) * T) / (sigma * math.sqrt(T))
        d2K = d1K - sigma * math.sqrt(T)

        d1KH = (math.log(H / S) + (r + 0.5 * sigma**2) * T) / (sigma * math.sqrt(T))
        d2KH = d1KH - sigma * math.sqrt(T)

        if "up-and-out call" in option_type:
            if H <= K:
                return 0.0
            if S >= H:
                return 0.0

            return (S * norm.cdf(d1) - K * math.exp(-r * T) * norm.cdf(d2) -
                    S * (H / S)**(2 * r / sigma**2) * norm.cdf(d1K) +
                    K * math.exp(-r * T) * (H / S)**(2 * r / sigma**2 - 2) * norm.cdf(d2K))

        elif "down-and-out call" in option_type:
            if H >= K:
                return S * norm.cdf(d1) - K * math.exp(-r * T) * norm.cdf(d2)
            if S <= H:
                return 0.0

            return (S * norm.cdf(d1) - K * math.exp(-r * T) * norm.cdf(d2) -
                    S * (H / S)**(2 * r / sigma**2) * norm.cdf(-d1K) +
                    K * math.exp(-r * T) * (H / S)**(2 * r / sigma**2 - 2) * norm.cdf(-d2K))

        elif "up-and-in call" in option_type:
            if H <= K:
                return S * norm.cdf(d1) - K * math.exp(-r * T) * norm.cdf(d2)
            if S >= H:
                return S * norm.cdf(d1) - K * math.exp(-r * T) * norm.cdf(d2)

            return (S * (H / S)**(2 * r / sigma**2) * norm.cdf(d1K) -
                    K * math.exp(-r * T) * (H / S)**(2 * r / sigma**2 - 2) * norm.cdf(d2K))

        elif "down-and-in call" in option_type:
             if H >= K:
                return 0.0
             if S <= H:
                return S * norm.cdf(d1) - K * math.exp(-r * T) * norm.cdf(d2)

             return (S * (H / S)**(2 * r / sigma**2) * norm.cdf(-d1K) -
                    K * math.exp(-r * T) * (H / S)**(2 * r / sigma**2 - 2) * norm.cdf(-d2K))

        elif "up-and-out put" in option_type:
            if H <= K:
                return K * math.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
            if S >= H:
                return 0.0

            return (K * math.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1) -
                    K * math.exp(-r * T) * (H / S)**(2 * r / sigma**2 - 2) * norm.cdf(-d2K) +
                    S * (H / S)**(2 * r / sigma**2) * norm.cdf(-d1K))

        elif "down-and-out put" in option_type:
            if H >= K:
                return 0.0
            if S <= H:
                return 0.0

            return (K * math.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1) -
                    K * math.exp(-r * T) * (H / S)**(2 * r / sigma**2 - 2) * norm.cdf(d2K) +
                    S * (H / S)**(2 * r / sigma**2) * norm.cdf(d1K))

        elif "up-and-in put" in option_type:
            if H <= K:
                return 0.0
            if S >= H:
                return K * math.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)

            return (K * math.exp(-r * T) * (H / S)**(2 * r / sigma**2 - 2) * norm.cdf(-d2K) -
                    S * (H / S)**(2 * r / sigma**2) * norm.cdf(-d1K))

        elif "down-and-in put" in option_type:
            if H >= K:
                return K * math.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
            if S <= H:
                return K * math.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)

            return (K * math.exp(-r * T) * (H / S)**(2 * r / sigma**2 - 2) * norm.cdf(d2K) -
                    S * (H / S)**(2 * r / sigma**2) * norm.cdf(d1K))

        else:
            return 0.0

    def go_back(self, instance):
        self.manager.current = 'main'



class MyApp(MDApp):
    def build(self):
        sm = ScreenManager()
        sign_in_screen = SignInScreen(name='signin')
        sign_up_screen = SignUpScreen(name='signup')
        main_screen = MainScreen(name='main')
        graph_screen = GraphScreen(name='graph')
        sensitivity_screen = SensitivityScreen(name='sensitivity')  # Add this line
        greeks_screen = GreeksScreen(name='greeks')  # add this
        sm.add_widget(sign_in_screen)
        sm.add_widget(sign_up_screen)
        sm.add_widget(main_screen)
        sm.add_widget(graph_screen)
        sm.add_widget(sensitivity_screen)  # Add this line
        sm.add_widget(greeks_screen)  # add this
        sm.current = 'signin'

        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.primary_hue = "900"


        return sm

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.primary_hue = "900"




if __name__ == '__main__':
    MyApp().run()