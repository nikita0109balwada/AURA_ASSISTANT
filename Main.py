import customtkinter as ctk
from PIL import Image
import time
import threading
import tkinter.font as tkfont
import json
import os
import datetime  
import requests
from PIL import Image
from dotenv import load_dotenv
import backend
import tkinter as tk
import customtkinter as ctk
import time, matplotlib
matplotlib.use('Agg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
load_dotenv()
from top_bar import TopBar


OPEN_WEATHER_API_KEY = os.getenv("OPEN_WEATHER_API_KEY")

SETTINGS_FILE = "settings.json"

about_popup = None


def save_location_preference(city_name):
    try:
        # Load existing settings if exist
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, "r") as f:
                settings = json.load(f)
        else:
            settings = {}

        # Update or add city
        settings["city"] = city_name

        # Write back
        with open(SETTINGS_FILE, "w") as f:
            json.dump(settings, f)
        print(f"[Settings] Saved city: {city_name}")
    except Exception as e:
        print(f"[Settings] Error saving city: {e}")

def load_location_preference():
    try:
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, "r") as f:
                settings = json.load(f)
                city = settings.get("city")
                if city:
                    print(f"[Settings] Loaded saved city: {city}")
                    return city
    except Exception as e:
        print(f"[Settings] Error loading city: {e}")
    return "Delhi"

    
def display_message_old(text, sender):
    print(f"[Main] display_message called: {sender}: {text}")

    # Create a new label
    label = ctk.CTkLabel(
        output_box,
        text=f"{sender}: {text}",
        anchor="w",
        justify="left",
        wraplength=450,  # wrap long lines
        padx=8,
        pady=4
    )
    # Add to scrollable frame
    label.pack(fill="x", padx=10, pady=2)

    # Force scroll to bottom
    output_box.update_idletasks()
    try:
        output_box._parent_canvas.yview_moveto(1.0)
    except Exception as e:
        print(f"Scroll error: {e}")

    # Update top bar
    if sender == "assistant":
        top_bar.set_status("Idle")
    elif sender == "user":
        top_bar.set_status("User input received")


def save_theme_preference(theme_name):
    try:
        with open(SETTINGS_FILE, "w") as f:
            json.dump({"theme": theme_name}, f)
    except Exception as e:
        print(f"Error saving theme preference: {e}")


def load_theme_preference():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r") as f:
                settings = json.load(f)
                return settings.get("theme", "dark")
        except Exception as e:
            print(f"Error loading theme preference: {e}")
            return "dark"
    return "dark"

def save_location_preference(city_name):
    try:
        # Load existing settings or create new ones
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, "r") as f:
                settings = json.load(f)
        else:
            settings = {}
        
        # Update location
        settings["location"] = city_name
        
        # Save back to file
        with open(SETTINGS_FILE, "w") as f:
            json.dump(settings, f)
    except Exception as e:
        print(f"Error saving location preference: {e}")

def load_location_preference():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r") as f:
                settings = json.load(f)
                return settings.get("location", "Delhi")
        except Exception as e:
            print(f"Error loading location preference: {e}")
            return "Delhi"
    return "Delhi"

# Initialize theme and location
theme = load_theme_preference()
city = load_location_preference()
ctk.set_appearance_mode(theme)


# === Initialize App ===
app = ctk.CTk()

# --- Load Icons (AFTER app is created, BEFORE any widget uses them) ---
icons = {}
icon_size_button = (28, 28)
icon_size_submit = (20, 20)
weather_icon_size = (20,20)
icon_sizes = {
    "mic": (28, 28),
    "power": (28, 28),
    "image": (28, 28),
    "submit": (20, 20),
    "save": (28, 28),
    "history": (28, 28),
    "exit": (28, 28),
    "theme": (28, 28),
    "collapse": (28, 28),
    "clock": (24, 24),
    "weather": (18, 18),
    "location": (20, 20),
    "download": (24, 24),
    "edit": (24, 24),
    "regenerate": (24, 24),
    "humidity": (12, 12),
    "temperature": (48, 48),
    "aqi": (12, 12),
    "precipitation": (12, 12),
    "cpu": (18, 18),
    "ram": (18, 18),
    "disk": (18, 18),
    "ip": (18, 18),
    "battery": (18, 18),
    "uptime": (18, 18),
    "attach": (24, 24),
    "info": (24, 24),
}
icon_paths = {
    "mic": ("icons/light/mic.png", "icons/dark/mic.png"),
    "power": ("icons/light/power.png", "icons/dark/power.png"),
    "image": ("icons/light/image.png", "icons/dark/image.png"),
    "submit": ("icons/light/submit.png", "icons/dark/submit.png"),
    "save": ("icons/light/save.png", "icons/dark/save.png"),
    "history": ("icons/light/history.png", "icons/dark/history.png"),
    "exit": ("icons/light/exit.png", "icons/dark/exit.png"),
    "theme": ("icons/light/theme.png", "icons/dark/theme.png"),
    "collapse": ("icons/light/collapse.png", "icons/dark/collapse.png"),
    "clock": ("icons/light/clock.png", "icons/dark/clock.png"),
    "weather": ("icons/light/weather.png", "icons/dark/weather.png"),
    "location": ("icons/light/location.png", "icons/dark/location.png"),
    "download": ("icons/light/download.png", "icons/dark/download.png"),
    "edit": ("icons/light/edit.png", "icons/dark/edit.png"),
    "regenerate": ("icons/light/regenrate.png", "icons/dark/regenrate.png"),
    "humidity": ("icons/light/humidity.png", "icons/dark/humidity.png"),
    "temperature": ("icons/light/temperature.png", "icons/dark/temperature.png"),
    "aqi": ("icons/light/aqi.png", "icons/dark/aqi.png"),
    "precipitation": ("icons/light/precipitation.png", "icons/dark/precipitation.png"),
    "battery": ("icons/light/battery.png", "icons/dark/battery.png"),
    "ram": ("icons/light/ram.png", "icons/dark/ram.png"),
    "disk": ("icons/light/disk.png", "icons/dark/disk.png"),
    "ip": ("icons/light/ip.png", "icons/dark/ip.png"),
    "cpu": ("icons/light/cpu.png", "icons/dark/cpu.png"),
    "attach": ("icons/light/attach.png", "icons/dark/attach.png"),
    "info": ("icons/light/info.png", "icons/dark/info.png"),

}
if not os.path.exists("icons"):
    os.makedirs("icons/light")
    os.makedirs("icons/dark")
    print("Created 'icons/light' and 'icons/dark' directories. Please place your icon files there.")
for name, (light_path, dark_path) in icon_paths.items():
    try:
        light_img = Image.open(light_path) if os.path.exists(light_path) else None
        dark_img = Image.open(dark_path) if os.path.exists(dark_path) else None
        if light_img and dark_img:
            size = icon_sizes.get(name, icon_size_button)
            icons[name] = ctk.CTkImage(light_image=light_img, dark_image=dark_img, size=size)
        elif light_img:
            size = icon_size_submit if name == "submit" else icon_size_button
            icons[name] = ctk.CTkImage(light_image=light_img, dark_image=light_img, size=size)
        elif dark_img:
            size = icon_size_submit if name == "submit" else icon_size_button
            icons[name] = ctk.CTkImage(light_image=dark_img, dark_image=dark_img, size=size)
        else:
            print(f"Error: Could not load any image for icon '{name}'.")
            icons[name] = None
    except Exception as e:
        print(f"An unexpected error occurred loading icon '{name}': {e}")
        icons[name] = None

# --- Set app icon after app is created and icons are loaded ---
try:
    icon_image = tk.PhotoImage(file="icon.png")
    app.iconphoto(True, icon_image)
except Exception as e:
    print(f"Warning: Could not set app icon: {e}")

is_listening = False

# === Theme Definitions ===
light_theme = {
    "primary": "#6200EE",
    "primary_variant": "#3700B3",
    "secondary": "#03DAC6",
    "secondary_variant": "#018786",
    "background": "#F0F0F0",
    "surface": "#FFFFFF",
    "surface_variant": "#E0E0E0",
    "error": "#B00020",
    "on_primary": "#FFFFFF",
    "on_secondary": "#000000",
    "on_background": "#000000",
    "on_surface": "#000000",
    "on_error": "#FFFFFF",
    "visualizer_bar": "#018786",
    "progress_bar": "#3700B3",
    "textbox_fg": "#FFFFFF",
    "textbox_text": "#000000",
    "entry_fg": "#E0E0E0",
    "entry_text": "#000000",
    "placeholder": "#757575",
    "clock_text": "#000000",
    "label_text": "#000000",
    "transparent_hover": "#D0D0D0"
}
dark_theme = {
    "primary": "#BB86FC",
    "primary_variant": "#9e47f5",
    "secondary": "#03DAC6",
    "secondary_variant": "#00A090",
    "background": "#121212",
    "surface": "#1E1E1E",
    "surface_variant": "#2C2C2C",
    "error": "#CF6679",
    "on_primary": "#000000",
    "on_secondary": "#000000",
    "on_background": "#FFFFFF",
    "on_surface": "#E0E0E0",
    "on_error": "#000000",
    "visualizer_bar": "#03DAC6",
    "progress_bar": "#BB86FC",
    "textbox_fg": "#2C2C2C",
    "textbox_text": "#E0E0E0",
    "entry_fg": "#2C2C2C",
    "entry_text": "#E0E0E0",
    "placeholder": "#888888",
    "clock_text": "#FFFFFF",
    "label_text": "#FFFFFF",
    "transparent_hover": "#4A4A4A"
}

# --- Theme Management ---

def toggle_theme_method(self):
    current = ctk.get_appearance_mode()  # returns "Dark" or "Light"
    new_theme = "light" if current == "Dark" else "dark"
    ctk.set_appearance_mode(new_theme)
    save_theme_preference(new_theme)
    self.refresh_icons()

def refresh_icons(self):
    # Force all widgets with CTkImage to reapply icon
    self.theme_button.configure(image=self.icons.get("theme"))
    self.location_icon.configure(image=self.icons.get("location"))
    self.weather_icon.configure(image=self.icons.get("weather"))
    # Add any other buttons/labels using icons here


# === Load Initial Theme ===
current_theme = load_theme_preference()
current_theme_dict = light_theme if current_theme == "light" else dark_theme
ctk.set_appearance_mode(current_theme)

# --- Load Custom Font ---
def register_ttf_fonts(font_dir="fonts"):
    for font_file in os.listdir(font_dir):
        if font_file.lower().endswith(".ttf"):
            font_path = os.path.join(font_dir, font_file)
            try:
                ctk.CTkFont(family=os.path.splitext(font_file)[0], size=12)
            except Exception as e:
                print(f"Error registering font {font_file}: {e}")


def show_about_popup():
    global about_popup
    import webbrowser

    if about_popup is not None and about_popup.winfo_exists():
        # Already open → bring to front
        about_popup.lift()
        about_popup.focus_force()
        return

    about_popup = ctk.CTkToplevel()
    about_popup.title("About Aura")
    about_popup.geometry("320x140")
    about_popup.resizable(False, False)
    about_popup.attributes('-topmost', True)  # Always on top

    # Disable minimize & maximize buttons (Windows only)
    about_popup.overrideredirect(False)  # keep normal border
    try:
        about_popup.attributes('-toolwindow', True)  # remove minimize & maximize on Windows
    except:
        pass

    # When closed, clear the global variable
    def on_close():
        global about_popup
        if about_popup is not None:
            about_popup.destroy()
        about_popup = None


    about_popup.protocol("WM_DELETE_WINDOW", on_close)

    title_label = ctk.CTkLabel(
        about_popup,
        text="About Aura",
        font=ctk.CTkFont(size=16, weight="bold")
    )
    title_label.pack(pady=(10, 5))

    my_link = ctk.CTkLabel(
        about_popup,
        text="My GitHub",
        font=ctk.CTkFont(size=14, underline=True),
        text_color="#1e90ff",
        cursor="hand2"
    )
    my_link.pack(pady=2)
    my_link.bind("<Button-1>", lambda e: webbrowser.open_new("https://github.com/dheeraj-srma"))

    collaborator_link = ctk.CTkLabel(
        about_popup,
        text="Collaborator GitHub",
        font=ctk.CTkFont(size=14, underline=True),
        text_color="#1e90ff",
        cursor="hand2"
    )
    collaborator_link.pack(pady=2)
    collaborator_link.bind("<Button-1>", lambda e: webbrowser.open_new("https://github.com/nikita0109balwada"))

    close_btn = ctk.CTkButton(about_popup, text="Close", command=on_close, width=80, height=48)
    close_btn.pack(pady=(10, 8), ipady = 6)

    # Focus on the popup
    about_popup.focus_force()


def load_custom_fonts(app, font_dir="fonts"):
    loaded_fonts = {}
    available_fonts = tkfont.families()
    desired_fonts = {
        "STEELAR": 22,
        "Aquire": 26,
        "DAGGERSQUARE": 20,
        "Enter Sansman": 24,
        "NCL Monster Beast Demo": 24,
        "Planet Space": 24,
        "Squares Bold": 24,
        "Digital Cards Demo": 26,
        "Swera Demo": 32,
        "Bord Demo": 10,
        "Momcake": 14,
    }
    for font_name, font_size in desired_fonts.items():
        try:
            if font_name in available_fonts:
                loaded_fonts[font_name] = ctk.CTkFont(family=font_name, size=font_size)
            else:
                print(f"⚠️ Font '{font_name}' not found. Using fallback 'Arial'")
                loaded_fonts[font_name] = ctk.CTkFont(family="Arial", size=font_size)
        except Exception as e:
            loaded_fonts[font_name] = ctk.CTkFont(family="Arial", size=font_size)
    return loaded_fonts
try:
    custom_font_name = "STEELAR"
    custom_font_size = 22
    if custom_font_name in tkfont.families():
        custom_font = ctk.CTkFont(family=custom_font_name, size=custom_font_size)
    else:
        custom_font_name = "Arial"
        custom_font = ctk.CTkFont(family=custom_font_name, size=custom_font_size)
except Exception as e:
    print(f"Error loading font: {e}. Using fallback.")
    custom_font_name = "Arial"
    custom_font_size = 26
    custom_font = ctk.CTkFont(family=custom_font_name, size=custom_font_size)
register_ttf_fonts("fonts")
fonts = load_custom_fonts(app)

# --- Panel Size Variables ---
tools_panel_width = 65
left_panel_width = 165
bottom_panel_height = 60
panel_spacing = 5
app_padding = 10
remaining_width = 700 - (app_padding * 2) - tools_panel_width - left_panel_width - (panel_spacing * 2)
right_panel_width = remaining_width
submit_button_width = 40
submit_button_x_padding = 10
button_y_in_panel = 10
button_x_padding = 10

# --- Utility Functions ---
def power_action():
    app.quit()
def save_chat():
    if backend.last_generated_text:
        backend.save_pdf_dialog(backend.last_generated_text)
    else:
        print("No recent chat to save.")
def chat_history():
    history = backend.conversation_history
    if not history:
        display_message("No chat history available yet.", "assistant")
        return
    display_message("📜 Chat History:", "assistant")
    for item in history[-5:]:
        sender = item["sender"]
        text = item["text"]
        display_message(text, sender)
def toggle_listening():
    global is_listening
    if not is_listening:
        is_listening = True
        backend.speak_enabled = True
        display_message("🎙️ Listening activated. Say something!", "assistant")
        backend.speak_text("Listening activated. Say something!", lang='en')
        def listen_loop():
            while is_listening:
                recorded_text = backend.record_audio()
                if recorded_text:
                    display_message(recorded_text, "user")
                    lang_code = backend.detect_language(recorded_text)
                    main_response, follow_up = backend.get_ai_response(recorded_text, lang_code)
                    if main_response:
                        backend.speak_text(main_response, lang_code)
                    if follow_up:
                        backend.speak_text(follow_up, lang_code)
                else:
                    backend.speak_text("Sorry, I didn't catch that.", lang='en')
        threading.Thread(target=listen_loop, daemon=True).start()
    else:
        is_listening = False
        backend.speak_enabled = False
        display_message("Listening stopped.", "assistant")
        backend.speak_text("Listening stopped.", lang='en')
def change_location():
    def update_city(city_name):
        global city
        city = city_name
        save_location_preference(city_name)  # Save to settings
        # Update the TopBar location display
        top_bar.location_name_var.set(city_name)
        update_weather()
        display_message(f"📍 Location changed to: {city}", "assistant")
    CityInputPopup(app, on_submit_callback=update_city)
def update_weather():
    global city
    try:
        api_key = os.getenv("OPEN_WEATHER_API_KEY")
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
        response = requests.get(url)
        data = response.json()
        if data.get("main"):
            temp = data["main"]["temp"]
            desc = data["weather"][0]["description"].capitalize()
            humidity = data["main"]["humidity"]
            top_bar.temperature_label.configure(text=f"{int(temp)}°C")
            top_bar.condition_label.configure(text=desc)
            top_bar.humidity_label.configure(text=f"Humidity: {humidity}%")
        else:
            top_bar.temperature_label.configure(text="--°C")
            top_bar.condition_label.configure(text="Not found")
            top_bar.humidity_label.configure(text="--")
    except Exception as e:
        print(f"Weather error: {e}")
        top_bar.temperature_label.configure(text="Error")
        top_bar.condition_label.configure(text="Error")
        top_bar.humidity_label.configure(text="--")
def submit_message(event=None):
    message = command_entry.get()
    if not message.strip():
        return
    command_entry.delete(0, ctk.END)
    if not generate_image_mode and not edit_image_mode:
        display_message(message, "user")

    top_bar.set_status("Thinking")
    threading.Thread(target=process_message, args=(message,), daemon=True).start()

def toggle_theme():
    global current_theme, current_theme_dict
    if current_theme == "dark":
        new_mode = "light"
        new_theme_dict = light_theme
    else:
        new_mode = "dark"
        new_theme_dict = dark_theme
    current_theme = new_mode
    current_theme_dict = new_theme_dict
    ctk.set_appearance_mode(current_theme)
    apply_theme(current_theme_dict)
    save_theme_preference(current_theme)

def apply_theme(theme_dict):
    main_frame.configure(fg_color=theme_dict["surface"])
    output_frame.configure(fg_color=theme_dict["surface_variant"])
    output_label.configure(text_color=theme_dict["label_text"])
    output_box.configure(fg_color=theme_dict["textbox_fg"], border_color=theme_dict["surface_variant"])
    for child in output_box.winfo_children():
        if isinstance(child, ChatBubble):
            child.update_theme_with_dict(theme_dict)
    command_entry.configure(fg_color=theme_dict["entry_fg"], text_color=theme_dict["entry_text"], border_color=theme_dict["surface_variant"], placeholder_text_color=theme_dict["placeholder"])
    themed_button_list = [tools_btn, btn_submit, save_icon_btn, history_icon_btn, close_icon_btn, theme_toggle_btn, collapse_icon_btn]
    for btn in themed_button_list:
        if btn:
            hover_c = theme_dict["error"] if btn == close_icon_btn else theme_dict["primary_variant"]
            fg_c = theme_dict["primary"]
            btn.configure(fg_color=fg_c, hover_color=hover_c)
            if btn.cget("text"):
                btn.configure(text_color=theme_dict["on_primary"])
    transparent_hover_color = theme_dict["transparent_hover"]
    for btn in [btn_image, btn_mic, btn_power]:
        if btn:
            btn.configure(hover_color=transparent_hover_color)

def process_message(message):
    global generate_image_mode, edit_image_mode, edit_image_prompt
    if edit_image_mode:
        display_message(message, "user")
        try:
            top_bar.set_status("Generating")
            display_message("Editing image...", "assistant")
            combined_prompt = f"{edit_image_prompt}, {message}"
            url = f"https://image.pollinations.ai/prompt/{combined_prompt}"
            response = requests.get(url)
            response.raise_for_status()
            from PIL import Image
            import io
            edited_image = Image.open(io.BytesIO(response.content))
            display_image_bubble(edited_image, "assistant", combined_prompt)
        except Exception as e:
            display_message(f"❌ Failed to edit image: {e}", "assistant")
        finally:
            top_bar.set_status("Idle")
        
        edit_image_mode = False
        edit_image_prompt = None
        return
    if generate_image_mode:
        display_message(message, "user")
        try:
            top_bar.set_status("Generating")
            display_message("Generating image...", "assistant")
            url = f"https://image.pollinations.ai/prompt/{message}"
            response = requests.get(url)
            response.raise_for_status()
            from PIL import Image
            import io
            image = Image.open(io.BytesIO(response.content))
            display_image_bubble(image, "assistant", message)
        except requests.exceptions.HTTPError as e:
            if response.status_code == 502:
                display_message("❌ The image service is temporarily unavailable (502 error). Please try again later.", "assistant")
            else:
                display_message(f"❌ Failed to generate image: {e}", "assistant")
        except Exception as e:
            display_message(f"❌ Failed to generate image: {e}", "assistant")
        finally:
            top_bar.set_status("Idle")
        return
    
    lang_code = backend.detect_language(message)
    intent_data = backend.detect_intent(message)
    intent = intent_data.get("intent")
    query = intent_data.get("query")
    if intent == "save_previous":
        if backend.last_generated_text:
            try:
                top_bar.set_status("Saving")
                backend.save_pdf_dialog(backend.last_generated_text, lang=lang_code)
            finally:
                top_bar.set_status("Idle")
        else:
            display_message("No previous response to save.", "assistant")
    elif intent in ["chat", "chat_and_save"]:
        main_response, follow_up = backend.get_ai_response(query, lang_code)
        if main_response:
            display_message(main_response, "assistant")
        if follow_up:
            display_message(follow_up, "assistant")
        if intent == "chat_and_save" and main_response:
            top_bar.set_status("Saving")
            backend.save_pdf_dialog(main_response, lang=lang_code)
            top_bar.set_status("Idle")
    elif intent == "image_generation":
        backend.handle_image_generation(query)

# === App Theme Settings ===
ctk.set_appearance_mode("dark")  
ctk.set_default_color_theme("blue")

# Initialize global message counter
message_counter = 0  

class CityInputPopup(ctk.CTkToplevel):
    def __init__(self, parent, on_submit_callback):
        super().__init__(parent)
        self.title("Change City")
        self.geometry("300x160")
        self.resizable(False, False)
        self.grab_set()  # Modal window

        self.label = ctk.CTkLabel(self, text="Enter City Name:")
        self.label.pack(pady=(20, 10))

        self.entry = ctk.CTkEntry(self, width=200)
        self.entry.pack(pady=(0, 10))
        self.entry.focus()

        self.submit_btn = ctk.CTkButton(self, text="Submit", command=self.submit)
        self.submit_btn.pack()

        self.callback = on_submit_callback

    def submit(self):
        city = self.entry.get().strip()
        if city:
            self.callback(city)
        self.destroy()

class ChatBubble(ctk.CTkFrame):
    def __init__(self, master, text, is_user=False):
        # Use theme dictionary for colors
        theme_dict = current_theme_dict if 'current_theme_dict' in globals() else dark_theme
        self.is_user = is_user
        if is_user:
            bubble_bg = theme_dict["primary"]
            bubble_text_color = theme_dict["on_primary"]
        else:
            if current_theme == "Light":
                bubble_bg = "#f5f5f5"
                bubble_text_color = "#333333"
            else:
                bubble_bg = "#3a3a3a"
                bubble_text_color = "#e0e0e0"
        
        super().__init__(master, fg_color=bubble_bg, corner_radius=14)
        
        # Modern wraplength for chat area
        wraplength = 440
        message_font = ctk.CTkFont(family="Inter", size=15, weight="normal")
        self.label = ctk.CTkLabel(self, text=text, text_color=bubble_text_color,
                                  justify="right" if is_user else "left", anchor="w", 
                                  wraplength=wraplength, font=message_font)
        self.label.pack(fill="x", padx=16, pady=8)

    def update_theme_with_dict(self, theme_dict):
        if self.is_user:
            self.configure(fg_color=theme_dict["primary"])
            self.label.configure(text_color=theme_dict["on_primary"])
        else:
            if current_theme == "light":
                ai_bg = "#f5f5f5"
                ai_text = "#333333"
            else:
                ai_bg = "#3a3a3a"
                ai_text = "#e0e0e0"
            self.configure(fg_color=ai_bg)
            self.label.configure(text_color=ai_text)


# Updated display_message function
def display_message(message, sender):
    global message_counter

    if not message.strip():
        return

    is_user = (sender == "user")
    bubble = ChatBubble(output_box, message, is_user=is_user)

    # Modern padding and alignment
    if is_user:
        bubble.grid(row=message_counter, column=0, padx=(80, 15), pady=(6, 10), sticky="e")
    else:
        bubble.grid(row=message_counter, column=0, padx=(15, 80), pady=(6, 10), sticky="w")

    message_counter += 1

    # Scroll to bottom after a short delay
    output_box.after(100, lambda: output_box._parent_canvas.yview_moveto(1.0))

# Add global state for image mode
generate_image_mode = False

# Modify the photo icon button callback to toggle image mode
def image_upload():
    global generate_image_mode
    generate_image_mode = not generate_image_mode
    if generate_image_mode:
        display_message("Generating images", "assistant")
    else:
        display_message("🖼️ Image mode OFF. Back to normal chat.", "assistant")

# Add global state for edit image mode
edit_image_mode = False
edit_image_prompt = None

# Update display_image_bubble to implement regenerate and edit logic
def display_image_bubble(image, sender, prompt):
    # Move DownloadBubble class definition to top-level (before display_image_bubble)
    class DownloadBubble(ctk.CTkFrame):
        def __init__(self, master, on_download, on_edit):
            super().__init__(master, fg_color="transparent", corner_radius=0)
            theme_dict = current_theme_dict if 'current_theme_dict' in globals() else dark_theme
            self.download_btn = ctk.CTkButton(
                self,
                image=icons.get("download"),
                text="",
                width=40,
                height=32,
                command=on_download,
                fg_color=theme_dict["primary"],
                hover_color=theme_dict["primary_variant"]
            )
            self.download_btn.pack(side="left", padx=4, pady=2)
            self.edit_btn = ctk.CTkButton(
                self,
                image=icons.get("edit"),
                text="",
                width=40,
                height=32,
                command=on_edit,
                fg_color=theme_dict["primary"],
                hover_color=theme_dict["primary_variant"]
            )
            self.edit_btn.pack(side="left", padx=4, pady=2)

    # In display_image_bubble, restore ImageBubble as a local class so 'bubble' is defined before use
    class ImageBubble(ctk.CTkFrame):
        def __init__(self, master, pil_image, is_user=False):
            theme_dict = current_theme_dict if 'current_theme_dict' in globals() else dark_theme
            if is_user:
                bubble_bg = theme_dict["primary"]
            else:
                if current_theme == "Light":
                    bubble_bg = "#f5f5f5"
                else:
                    bubble_bg = "#3a3a3a"
            super().__init__(master, fg_color=bubble_bg, corner_radius=14)
            
            # Preserve original image orientation and create thumbnail with proper aspect ratio
            self.pil_image = pil_image
            
            # Calculate thumbnail size while preserving aspect ratio
            max_thumb_size = 256
            original_width, original_height = pil_image.size
            aspect_ratio = original_width / original_height
            
            if aspect_ratio > 1:  # Landscape
                thumb_width = max_thumb_size
                thumb_height = int(max_thumb_size / aspect_ratio)
            else:  # Portrait or square
                thumb_height = max_thumb_size
                thumb_width = int(max_thumb_size * aspect_ratio)
            
            # Create thumbnail with proper aspect ratio
            thumb_image = pil_image.resize((thumb_width, thumb_height), Image.Resampling.LANCZOS)
            self.thumb_image = thumb_image
            
            self.tk_img = ctk.CTkImage(light_image=thumb_image, dark_image=thumb_image, size=(thumb_width, thumb_height))
            self.img_label = ctk.CTkLabel(self, image=self.tk_img, text="")
            self.img_label.pack(padx=8, pady=8)
            self.img_label.bind("<Button-1>", self.open_enlarged_image)
        def open_enlarged_image(self, event=None):
            top = tk.Toplevel()
            top.title("Enlarged Image")
            app_width = self.winfo_toplevel().winfo_width()
            max_width = int(app_width * 0.9) if app_width > 0 else 640
            w, h = self.pil_image.size
            aspect_ratio = h / w if w != 0 else 1
            new_width = min(max_width, w)
            new_height = int(new_width * aspect_ratio)
            enlarged_image = self.pil_image.resize((new_width, new_height))
            tk_enlarged = ctk.CTkImage(light_image=enlarged_image, dark_image=enlarged_image, size=(new_width, new_height))
            img_label = ctk.CTkLabel(top, image=tk_enlarged, text="")
            img_label.pack(padx=10, pady=10)
            self._enlarged_img_ref = tk_enlarged
            close_btn = ctk.CTkButton(top, text="Close", command=top.destroy)
            close_btn.pack(pady=(0, 10))

    is_user = (sender == "user")
    def edit_image():
        global edit_image_mode, edit_image_prompt
        edit_image_mode = True
        edit_image_prompt = prompt
        display_message("Please type your edit prompt for the image.", "assistant")
    def download_image():
        from tkinter import filedialog
        base_name = "_".join(prompt.split()[:3]) or "image"
        file_path = filedialog.asksaveasfilename(defaultextension=".png", initialfile=f"{base_name}.png", filetypes=[("PNG files", "*.png"), ("All files", "*.*")])
        if file_path:
            try:
                top_bar.set_status("Saving")
                image.save(file_path)
            except Exception as e:
                display_message(f"Error saving image: {e}", "assistant")
            finally:
                top_bar.set_status("Idle")
                display_message(f"Image saved to {file_path}", "assistant")
    download_bubble = DownloadBubble(output_box, download_image, edit_image)
    bubble = ImageBubble(output_box, image, sender)
    if is_user:
        bubble.grid(row=globals()['message_counter'], column=0, padx=(80, 15), pady=(6, 2), sticky="e")
        download_bubble.grid(row=globals()['message_counter']+1, column=0, padx=(80, 15), pady=(0, 10), sticky="e")
    else:
        bubble.grid(row=globals()['message_counter'], column=0, padx=(15, 80), pady=(6, 2), sticky="w")
        download_bubble.grid(row=globals()['message_counter']+1, column=0, padx=(15, 80), pady=(0, 10), sticky="w")
    globals()['message_counter'] += 2
    output_box.after(100, lambda: output_box._parent_canvas.yview_moveto(1.0))

# === Initialize App ===
# app = ctk.CTk()  # <-- REMOVE THIS DUPLICATE INITIALIZATION
app.geometry("900x650")  # starting size
app.resizable(True, True)
app.minsize(700, 550)
app.title("AURA")
# --- Fix app icon error ---
try:
    icon_image = tk.PhotoImage(file="icon.png")  # PNG works here
    app.iconphoto(True, icon_image)  # True = affects the root window
except Exception as e:
    print(f"Warning: Could not set app icon: {e}")

# --- Main Frame ---
main_frame = ctk.CTkFrame(app, corner_radius=0, border_width=0)
main_frame.pack(fill="both", expand=True)

main_frame.grid_rowconfigure(0, weight=0)   # top bar fixed height
main_frame.grid_rowconfigure(1, weight=1)   # chat area grows
main_frame.grid_rowconfigure(2, weight=0)   # bottom panels fixed height
main_frame.grid_columnconfigure(0, weight=1)

# --- Top Bar ---
top_bar = TopBar(main_frame, fonts, icons, initial_city=city)
top_bar.grid(row=0, column=0, sticky="ew", padx=10, pady=5)

# Set up backend callbacks
backend.display_message_callback = display_message
backend.topbar_status_callback = top_bar.set_status

# --- Output Area ---
output_frame = ctk.CTkFrame(main_frame, width=685, height=410, corner_radius=16)
output_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
output_frame.grid_rowconfigure(0, weight=0)
output_frame.grid_rowconfigure(1, weight=1)
output_frame.grid_columnconfigure(0, weight=1)
output_label = ctk.CTkLabel(output_frame, text="RESULTS", font=fonts["Aquire"])
output_label.grid(row=0, column=0, sticky="w", padx=10, pady=(10, 0))
output_box = ctk.CTkScrollableFrame(output_frame, width=640, height=355, corner_radius=10, border_width=1)
output_box.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
output_box.grid_columnconfigure(0, weight=1)

# --- Bottom Row Container ---
bottom_row = ctk.CTkFrame(main_frame)
bottom_row.grid(row=2, column=0, sticky="ew", padx=10, pady=5)
bottom_row.grid_columnconfigure(0, weight=0)
bottom_row.grid_columnconfigure(1, weight=0)
bottom_row.grid_columnconfigure(2, weight=1)

# --- Tools Panel (Far Left) ---
tools_panel = ctk.CTkFrame(bottom_row, width=tools_panel_width, height=bottom_panel_height, corner_radius=16)
tools_panel.grid(row=0, column=0, sticky="w", padx=(0, panel_spacing))

# --- Left Bottom Panel (Image, Power, Mic) ---
left_bottom_panel = ctk.CTkFrame(bottom_row, width=left_panel_width, height=bottom_panel_height, corner_radius=16)
left_bottom_panel.grid(row=0, column=1, sticky="w", padx=(0, panel_spacing))

# --- Right Bottom Panel (Entry, Submit) ---
right_bottom_panel = ctk.CTkFrame(bottom_row, width=right_panel_width, height=bottom_panel_height, corner_radius=16)
right_bottom_panel.grid(row=0, column=2, sticky="ew")

# (Keep widgets inside each panel using .place() for now)

# --- Tools Button (in tools_panel) ---
tools_btn = ctk.CTkButton(tools_panel,  # PARENT: tools_panel
                          text="☰", width=45, height=40,
                          font=("Arial", 18), corner_radius=10,
                          command=lambda: toggle_side_menu())  # Updated command
tools_btn.place(relx=0.5, rely=0.5, anchor=ctk.CENTER)

# --- Input Buttons (in left_bottom_panel) ---
# transparent_hover_color is set dynamically in apply_theme
button_y_in_panel = 10
button_x_padding = 10

# Place Image button
current_x = button_x_padding
btn_image = ctk.CTkButton(left_bottom_panel,  # PARENT: left_bottom_panel
                          image=icons.get("image"), text="", width=40, height=40,
                          fg_color="transparent",  # <<< SET TRANSPARENT HERE
                          hover=True,  # Disable default hover color (we set it manually)
                          corner_radius=10, command=image_upload)
btn_image.place(x=current_x, y=button_y_in_panel)

# Place Power button next to Image
current_x += 40 + button_x_padding
btn_power = ctk.CTkButton(left_bottom_panel,  # PARENT: left_bottom_panel
                          image=icons.get("power"), text="", width=40, height=40,
                          fg_color="transparent", 
                          hover=True,  # Disable default hover color
                          corner_radius=10, command=power_action)
btn_power.place(x=current_x, y=button_y_in_panel)

# Place Mic button next to Power
current_x += 40 + button_x_padding
btn_mic = ctk.CTkButton(left_bottom_panel,  # PARENT: left_bottom_panel
                        image=icons.get("mic"), text="", width=40, height=40,
                        fg_color="transparent",  # <<< SET TRANSPARENT HERE
                        hover=True,  # Disable default hover color
                        corner_radius=10, command = toggle_listening)
btn_mic.place(x=current_x, y=button_y_in_panel)

# --- Command Entry (in right_bottom_panel) ---
# Adjust the entry width so it fills up to the button

def handle_attach_image():
    from tkinter import filedialog
    import os
    from PIL import Image

    file_path = filedialog.askopenfilename(
        title="Select image to analyze",
        filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif"), ("All files", "*.*")]
    )
    if file_path:
        print(f"User attached image: {file_path}")
        
        try:
            # Load and display the image as a user bubble
            image = Image.open(file_path)
            file_name = os.path.basename(file_path)
            display_image_bubble(image, "user", f"Uploaded: {file_name}")

            # Update status to show analyzing
            top_bar.set_status("Analyzing")
            
            # start backend analysis in background
            threading.Thread(
                target=backend.get_image_description_from_path,
                args=(file_path,),
                daemon=True
            ).start()
        except Exception as e:
            print(f"Error loading image: {e}")
            display_message(f"❌ Error loading image: {e}", "assistant")
            top_bar.set_status("Idle")

attach_button = ctk.CTkButton(
    right_bottom_panel,    # same parent
    image=icons.get("attach"),  # Use the attach icon
    text="",
    width=36, height=36,
    fg_color="transparent",
    hover_color="#e0e0e0",
    command=handle_attach_image
)
attach_button.place(x=10, y=10)

entry_x = 10 + 36 + 5   # button width + spacing
entry_width = right_panel_width - entry_x - submit_button_width - (submit_button_x_padding * 2)

command_entry = ctk.CTkEntry(right_bottom_panel,  # PARENT: right_bottom_panel
                            placeholder_text="Type your message...",
                            width=entry_width,
                            height=40,
                            corner_radius=10, border_width=1,font=ctk.CTkFont(size=15),)
command_entry.place(x=entry_x, y=button_y_in_panel)
command_entry.bind("<Return>", submit_message)  # Bind Enter key

# --- Submit Button (in right_bottom_panel) ---
# Place the submit button flush to the right edge
btn_submit = ctk.CTkButton(right_bottom_panel,  # PARENT: right_bottom_panel
                           image=icons.get("submit"), text="", width=submit_button_width, height=40,
                           fg_color="transparent",  # <<< SET TRANSPARENT HERE
                           corner_radius=10, command=submit_message)
btn_submit.place(relx=1.0, x=-submit_button_x_padding, y=button_y_in_panel, anchor="ne")


# === Side Menu (Initially hidden) ===
side_menu_width = 70
side_menu_visible = False
side_menu = ctk.CTkFrame(main_frame, width=0, height=app.winfo_reqheight(), corner_radius=0, border_width=0)
# Place it initially off-screen to the left or with 0 width at x=0
side_menu.place(x=-1, y=0, relheight=1)

# --- Side Menu Buttons ---
button_y_start = 20
button_spacing = 60
button_x = 10  # Center buttons horizontally

save_icon_btn = ctk.CTkButton(side_menu, image=icons.get("save"), text="", width=38, height=40,
                             corner_radius=10, command=save_chat)
save_icon_btn.place(x=button_x, y=button_y_start)

history_icon_btn = ctk.CTkButton(side_menu, image=icons.get("history"), text="", width=38, height=40,
                                 corner_radius=10, command=chat_history)
history_icon_btn.place(x=button_x, y=button_y_start + button_spacing)

theme_toggle_btn = ctk.CTkButton(side_menu, image=icons.get("theme"), text="", width=38, height=40,
                                  corner_radius=10, command=toggle_theme)
theme_toggle_btn.place(x=button_x, y=button_y_start + 2 * button_spacing)

close_icon_btn = ctk.CTkButton(side_menu, image=icons.get("exit"), text="", width=38, height=40,
                               corner_radius=10, command=app.quit)
close_icon_btn.place(x=button_x, y=button_y_start + 3 * button_spacing)



# --- ADD THE COLLAPSE BUTTON ---
# --- Fix collapse button linter error ---
collapse_content = icons.get("collapse") if icons.get("collapse") else "←"
collapse_text = "" if icons.get("collapse") else (str(collapse_content) if collapse_content is not None else "")
collapse_image = icons.get("collapse")
collapse_icon_btn = ctk.CTkButton(side_menu,
                                  image=collapse_image,
                                  text=collapse_text,
                                  font=("Arial", 18),
                                  width=40, height=40,
                                  corner_radius=10,
                                  fg_color="transparent",
                                  command=lambda: toggle_side_menu())
collapse_icon_btn.place(relx=0.49, rely=0.962, anchor='s')

about_icon_btn = ctk.CTkButton(
    side_menu,
    image=icons.get("info"),   # make sure you have "info" icon in your icons dict
    text="",
    width=38, height=40,
    corner_radius=10,
    fg_color="#A155E4",
    hover_color="#B06AF2",
    command=show_about_popup
)

# Place it below existing buttons, adjust Y as needed
about_icon_btn.place(x=button_x, y=button_y_start + 4 * button_spacing)


# === Menu Animation ===
animation_steps = 10
animation_delay = 10

def animate_side_menu(target_width):
    current_width = side_menu.winfo_width()

    # Avoid division by zero or unnecessary animation if already at target
    if animation_steps <= 0:
        side_menu.configure(width=int(target_width))
        if target_width == 0:
            side_menu.lower()
        else:
            side_menu.lift()
        return

    # If already at the target width, just ensure lift/lower state is correct
    if current_width == target_width:
        if target_width == 0:
            side_menu.lower()
        else:
            side_menu.lift()
        return  # Exit if no animation needed

    step_size = (target_width - current_width) / animation_steps

    def step_animation(step=0):
        # Calculate the new width for this step
        new_width = current_width + step_size * (step + 1)

        # Determine if the animation should continue based on direction
        continue_animation = False
        if step_size > 0:  # Opening
            if new_width < target_width:
                continue_animation = True
        else:  # Closing
            if new_width > target_width:
                continue_animation = True

        # Ensure we don't exceed the number of steps
        if step >= animation_steps:
            continue_animation = False

        if continue_animation:
            side_menu.configure(width=int(new_width))
            app.after(animation_delay, step_animation, step + 1)
        else:
            # Animation finished or overshot, set final width and state
            side_menu.configure(width=int(target_width))
            if target_width == 0:
                side_menu.lower()  # Lower when fully closed


    # --- Action before starting steps ---
    if target_width > 0:  # If opening animation is intended
        side_menu.lift()  # <<< CRITICAL: Lift unconditionally before starting to open

    # Start the animation steps
    step_animation()


# Ensure the toggle function remains the same
def toggle_side_menu():
    global side_menu_visible
    if side_menu_visible:
        animate_side_menu(0)  # Animate closing
    else:
        animate_side_menu(side_menu_width)  # Animate opening
    side_menu_visible = not side_menu_visible



# === Clock Update ===
def update_clock():
    now = datetime.datetime.now().strftime("%H:%M")
    # Use the correct clock_label defined in the top bar UI
    top_bar.clock_label.configure(text=now)
    app.after(1000, update_clock)  # Update every second



# === Initial Setup Calls ===
apply_theme(current_theme_dict)  # Apply the loaded theme initially
update_clock()  # Start the clock

def on_window_configure(event=None):
    # On Windows, maximized state is 'zoomed'
    try:
        if app.state() == 'zoomed':
            top_bar.set_middle_info_visible(True)
        else:
            top_bar.set_middle_info_visible(False)
    except Exception:
        pass

app.bind('<Configure>', on_window_configure)

# === Start App ===
app.mainloop()
