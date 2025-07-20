import customtkinter as ctk
import psutil, time, socket
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os
import requests
import backend
import webbrowser

class TopBar(ctk.CTkFrame):
    def __init__(self, parent, fonts, icons, initial_city="Delhi"):
        super().__init__(parent, corner_radius=0, height=100)
        self.grid_propagate(False)
        self.fonts = fonts
        self.icons = icons
        self.current_status = "Idle"

        saved_city = backend.load_location_preference() or initial_city
        self.location_name_var = ctk.StringVar(value=saved_city)

        # Grid config: left (fixed), middle(dynamic), right(fixed)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=0)

        # --- Top Left Box ---
        self.top_left_box = ctk.CTkFrame(self, height=100, corner_radius=16)
        self.top_left_box.grid(row=0, column=0, sticky="nsw", padx=0, pady=0)
        self.top_left_box.grid_propagate(False)
        self.name_label = ctk.CTkLabel(self.top_left_box, text="AURA",
                                       font=ctk.CTkFont(family="Digital Cards Demo", size=22))
        self.name_label.pack(anchor="nw", padx=10, pady=(5,0))
        self.status_label = ctk.CTkLabel(self.top_left_box, text="Idle",
                                         font=ctk.CTkFont(family="Bord Demo", size=12))
        self.status_label.pack(anchor="nw", padx=10, pady=(0,5))
        self.animate_status()

        # --- Top Right Box ---
        self.top_right_box = ctk.CTkFrame(self, height=100, corner_radius=16)
        self.top_right_box.grid(row=0, column=1, columnspan=2, sticky="nsew", padx=5, pady=0)
        self.top_right_box.grid_propagate(False)
        self.top_right_box.grid_rowconfigure(0, weight=1)
        self.top_right_box.grid_columnconfigure(0, weight=0)  # clock
        self.top_right_box.grid_columnconfigure(1, weight=1)  # middle info
        self.top_right_box.grid_columnconfigure(2, weight=1)  # weather

        # --- Clock frame ---
        self.clock_frame = ctk.CTkFrame(self.top_right_box, fg_color="transparent")
        self.clock_frame.grid(row=0, column=0, sticky="w", padx=10, pady=5)
        self.clock_label = ctk.CTkLabel(self.clock_frame, text="00:00",
                                        font=ctk.CTkFont(family="DAGGERSQUARE", size=50))
        self.clock_label.pack(anchor="w")
        self.date_label = ctk.CTkLabel(self.clock_frame, text="Date",
                                       font=ctk.CTkFont(family="Bord Demo", size=14))
        self.date_label.pack(anchor="w")

        # --- Middle info frame ---
        self.create_info_rows()

        # --- Weather Frame ---
        self.weather_frame = ctk.CTkFrame(self.top_right_box, fg_color="transparent")
        self.weather_frame.grid(row=0, column=2, sticky="nse", padx=(0,10), pady=5)
        self.weather_frame.grid_columnconfigure(0, weight=0)
        self.weather_frame.grid_columnconfigure(1, weight=1)
        self.weather_frame.grid_rowconfigure(0, weight=1)

        temp_row = ctk.CTkFrame(self.weather_frame, fg_color="transparent")
        temp_row.grid(row=0, column=0, sticky="w")
        self.weather_icon = ctk.CTkLabel(temp_row, image=self.icons.get("temperature"), text="")
        self.weather_icon.grid(row=0, column=0, sticky="w", padx=2)
        self.temperature_label = ctk.CTkLabel(temp_row, text="--°C",
                                              font=ctk.CTkFont(family="DAGGERSQUARE", size=46))
        self.temperature_label.grid(row=0, column=1, sticky="w", padx=5)
        self.location_icon = ctk.CTkButton(temp_row, image=self.icons.get("location"), text="",
                                          width=36, height=36,
                                          fg_color="transparent", hover_color="#e0e0e0",
                                          command=self.change_location_callback)
        self.location_icon.grid(row=1, column=0, sticky="w", padx=2, pady=(2,0))
        self.location_label = ctk.CTkLabel(temp_row, textvariable=self.location_name_var,
                                          anchor="w", font=ctk.CTkFont(family="Bord Demo", size=12))
        self.location_label.grid(row=1, column=1, sticky="w", padx=5, pady=(2,0))

        # --- Details frame next to temp_row ---
        details_frame = ctk.CTkFrame(self.weather_frame, fg_color="transparent")
        details_frame.grid(row=0, column=1, sticky="n", padx=5)
        small_font = self.fonts["Bord Demo"]

        # Weather details rows
        self.condition_label = self._add_weather_row(details_frame, 0, "weather", "Sunny", small_font)
        self.precip_label = self._add_weather_row(details_frame, 1, "precipitation", "Precipitation --", small_font)
        self.humidity_label = self._add_weather_row(details_frame, 2, "humidity", "Humidity --%", small_font)
        self.aqi_label = self._add_weather_row(details_frame, 3, "aqi", "AQI --", small_font)

        # Start updates
        self.update_weather(saved_city)
        self.update_system_info()
        self.update_clock()

    def _add_weather_row(self, parent, row, icon_name, text, font):
        row_frame = ctk.CTkFrame(parent, fg_color="transparent")
        row_frame.grid(row=row, column=0, sticky="w")
        icon = ctk.CTkLabel(row_frame, image=self.icons.get(icon_name), text="", font=font)
        icon.pack(side="left", padx=1)
        label = ctk.CTkLabel(row_frame, text=text, font=ctk.CTkFont(family="Bord Demo", size=12))
        label.pack(side="left", padx=1)
        return label

    def set_status(self, new_status):
        self.after(0, self._update_status, new_status)

    def _update_status(self, new_status):
        self.current_status = new_status
        # status_label will be updated by animate_status or directly:
        self.status_label.configure(text=new_status)

    def animate_status(self, count=0):
        dots = "." * (count % 4)
        self.status_label.configure(text=f"{self.current_status}{dots}")
        self.after(500, self.animate_status, count+1)

    def update_clock(self):
        now = time.strftime("%H:%M")
        date = time.strftime("%a, %d %B")
        self.clock_label.configure(text=now)
        self.date_label.configure(text=date)
        self.after(1000, self.update_clock)

    def create_info_rows(self):
        # Create middle_info_frame first
        self.middle_info_frame = ctk.CTkFrame(self.top_right_box, fg_color="transparent")
        self.middle_info_frame.grid(row=0, column=1, sticky="nsew", padx=10)

        # 5 columns: 0=icon, 1=label, 2=sparkline, 3=status icon, 4=status label
        self.middle_info_frame.grid_columnconfigure(0, weight=0)
        self.middle_info_frame.grid_columnconfigure(1, weight=0)
        self.middle_info_frame.grid_columnconfigure(2, weight=0)
        self.middle_info_frame.grid_columnconfigure(3, weight=0)
        self.middle_info_frame.grid_columnconfigure(4, weight=0)
        
        for r in range(3):
            self.middle_info_frame.grid_rowconfigure(r, weight=1)

        big_font = ctk.CTkFont(family="Bord Demo", size=14)

        # --- CPU row ---
        self.cpu_icon = ctk.CTkLabel(self.middle_info_frame, image= self.icons.get("cpu"),text= "", font=big_font)
        self.cpu_icon.grid(row=0, column=0, sticky="w", padx=(0,1), pady=0)
        self.cpu_label = ctk.CTkLabel(self.middle_info_frame, text="CPU: 0%", font=big_font)
        self.cpu_label.grid(row=0, column=1, sticky="w", padx=1, pady=0)
        self.cpu_fig, self.cpu_line, self.cpu_canvas = self.create_sparkline(self.middle_info_frame, color='lime')
        self.cpu_canvas.get_tk_widget().grid(row=0, column=2, sticky="w", padx=1, pady=0)
        self.cpu_data = [0.0]*30

        # --- RAM row ---
        self.ram_icon = ctk.CTkLabel(self.middle_info_frame, image= self.icons.get("ram"),text= "", font=big_font)
        self.ram_icon.grid(row=1, column=0, sticky="w", padx=(0,1), pady=0)
        self.ram_label = ctk.CTkLabel(self.middle_info_frame, text="RAM: 0%", font=big_font)
        self.ram_label.grid(row=1, column=1, sticky="w", padx=1, pady=0)
        self.ram_fig, self.ram_line, self.ram_canvas = self.create_sparkline(self.middle_info_frame, color='cyan')
        self.ram_canvas.get_tk_widget().grid(row=1, column=2, sticky="w", padx=1, pady=0)
        self.ram_data = [0.0]*30

        # --- Disk row ---
        self.disk_icon = ctk.CTkLabel(self.middle_info_frame, image= self.icons.get("disk"),text= "", font=big_font)
        self.disk_icon.grid(row=2, column=0, sticky="w", padx=(0,1), pady=0)
        self.disk_label = ctk.CTkLabel(self.middle_info_frame, text="Disk: 0%", font=big_font)
        self.disk_label.grid(row=2, column=1, sticky="w", padx=1, pady=0)
        self.disk_fig, self.disk_line, self.disk_canvas = self.create_sparkline(self.middle_info_frame, color='magenta')
        self.disk_canvas.get_tk_widget().grid(row=2, column=2, sticky="w", padx=1, pady=0)
        self.disk_data = [0.0]*30

        # --- Uptime, Battery, IP in column 3 ---
        big_status_font = ctk.CTkFont(family="Bord Demo", size=16)
        self.uptime_icon = ctk.CTkLabel(self.middle_info_frame, image= self.icons.get("clock"),text= "", font=big_status_font)
        self.uptime_icon.grid(row=0, column=3, sticky="w", padx=(16,2))
        self.uptime_label = ctk.CTkLabel(self.middle_info_frame, text="Uptime: 0h", font=big_status_font)
        self.uptime_label.grid(row=0, column=4, sticky="w", padx=2)
        self.battery_icon = ctk.CTkLabel(self.middle_info_frame, image= self.icons.get("battery"),text= "", font=big_status_font)
        self.battery_icon.grid(row=1, column=3, sticky="w", padx=(16,2))
        self.battery_label = ctk.CTkLabel(self.middle_info_frame, text="Battery: --%", font=big_status_font)
        self.battery_label.grid(row=1, column=4, sticky="w", padx=2)
        self.ip_icon = ctk.CTkLabel(self.middle_info_frame, image= self.icons.get("ip"),text= "", font=big_status_font)
        self.ip_icon.grid(row=2, column=3, sticky="w", padx=(16,2))
        self.ip_label = ctk.CTkLabel(self.middle_info_frame, text="IP: --", font=big_status_font)
        self.ip_label.grid(row=2, column=4, sticky="w", padx=2)

    def create_sparkline(self, parent, color):
        fig = Figure(figsize=(1.2,0.25), dpi=100, facecolor='#111')  # larger sparkline
        ax = fig.add_subplot(111)
        ax.axis('off')
        line, = ax.plot([], [], color=color, linewidth=1)
        canvas = FigureCanvasTkAgg(fig, master=parent)
        return fig, line, canvas

    def update_system_info(self):
        # --- CPU ---
        cpu = psutil.cpu_percent()
        self.cpu_label.configure(text=f"CPU: {cpu}%")
        self.cpu_data.append(cpu); self.cpu_data.pop(0)
        self.cpu_line.set_data(range(len(self.cpu_data)), self.cpu_data)
        if self.cpu_line.axes is not None:
            self.cpu_line.axes.set_xlim(0, len(self.cpu_data))
            self.cpu_line.axes.set_ylim(0, 100)
        self.cpu_canvas.draw()

        # --- RAM ---
        ram = psutil.virtual_memory().percent
        self.ram_label.configure(text=f"RAM: {ram}%")
        self.ram_data.append(ram); self.ram_data.pop(0)
        self.ram_line.set_data(range(len(self.ram_data)), self.ram_data)
        if self.ram_line.axes is not None:
            self.ram_line.axes.set_xlim(0, len(self.ram_data))
            self.ram_line.axes.set_ylim(0, 100)
        self.ram_canvas.draw()

        # --- Disk ---
        disk = psutil.disk_usage('/').percent
        self.disk_label.configure(text=f"Disk: {disk}%")
        self.disk_data.append(disk); self.disk_data.pop(0)
        self.disk_line.set_data(range(len(self.disk_data)), self.disk_data)
        if self.disk_line.axes is not None:
            self.disk_line.axes.set_xlim(0, len(self.disk_data))
            self.disk_line.axes.set_ylim(0, 100)
        self.disk_canvas.draw()

        # --- Battery ---
        battery = psutil.sensors_battery()
        if battery:
            self.battery_label.configure(text=f"Battery: {battery.percent}%")
        else:
            self.battery_label.configure(text="Battery: --%")

        # --- Uptime ---
        uptime = int((time.time() - psutil.boot_time()) // 3600)
        self.uptime_label.configure(text=f"Uptime: {uptime}h")

        # --- IP ---
        try:
            ip = socket.gethostbyname(socket.gethostname())
        except:
            ip = "--"
        self.ip_label.configure(text=f"IP: {ip}")

        self.after(1000, self.update_system_info)

    def set_middle_info_visible(self, visible: bool):
        if visible:
            self.middle_info_frame.grid()
        else:
            self.middle_info_frame.grid_remove()

    def update_weather(self, city):
        """Fetch weather data and update labels."""
        try:
            api_key = os.getenv("OPEN_WEATHER_API_KEY")
            if not api_key:
                print("[Weather] API key not found")
                return
            url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
            response = requests.get(url)
            data = response.json()
            if data.get("main"):
                temp = int(data["main"]["temp"])
                desc = data["weather"][0]["description"].capitalize()
                humidity = data["main"]["humidity"]
                precipitation = data.get("rain", {}).get("1h", 0) or data.get("snow", {}).get("1h", 0) or 0
                aqi = "42"  # Placeholder
                self.temperature_label.configure(text=f"{temp}°C")
                self.condition_label.configure(text=desc)
                self.humidity_label.configure(text=f"Humidity {humidity}%")
                self.precip_label.configure(text=f"Precipitation {precipitation} mm")
                self.aqi_label.configure(text=f"AQI {aqi}")
            else:
                self.temperature_label.configure(text="--°C")
                self.condition_label.configure(text="Not found")
                self.humidity_label.configure(text="Humidity --%")
                self.precip_label.configure(text="Precipitation --")
                self.aqi_label.configure(text="AQI --")
        except Exception as e:
            print(f"[Weather] update error: {e}")
            self.temperature_label.configure(text="Error")
            self.condition_label.configure(text="Error")
            self.humidity_label.configure(text="Humidity --%")
            self.precip_label.configure(text="Precipitation --")
            self.aqi_label.configure(text="AQI --")

    

    def show_about_popup(self):
        popup = ctk.CTkToplevel(self)
        popup.title("About")
        popup.geometry("320x150")
        popup.resizable(False, False)

        # Optional: dark/light matching bg
        popup.configure(fg_color="#2a2a2a" if ctk.get_appearance_mode() == "Dark" else "#f0f0f0")

        heading = ctk.CTkLabel(
            popup,
            text="About This Assistant",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        heading.pack(pady=(15, 5))

        # Link: Your GitHub
        my_link = ctk.CTkLabel(
            popup,
            text="My GitHub",
            font=ctk.CTkFont(size=14, underline=True),
            text_color="#1e90ff",
            cursor="hand2"
        )
        my_link.pack(pady=(20, 5))
        my_link.bind("<Button-1>", lambda e: webbrowser.open_new("https://github.com/dheeraj-srma"))

        # Link: Collaborator GitHub
        collaborator_link = ctk.CTkLabel(
            popup,
            text="Collaborator GitHub",
            font=ctk.CTkFont(size=14, underline=True),
            text_color="#1e90ff",
            cursor="hand2"
        )
        collaborator_link.pack(pady=5)
        collaborator_link.bind("<Button-1>", lambda e: webbrowser.open_new("https://github.com/nikita0109balwada"))

        close_btn = ctk.CTkButton(popup, text="Close", command=popup.destroy)
        close_btn.pack(pady=(5, 10))


    def change_location_callback(self):
        popup = ctk.CTkToplevel(self)
        popup.title("Change Location")
        popup.geometry("300x100")
        entry = ctk.CTkEntry(popup, placeholder_text="Enter new city name")
        entry.pack(pady=10, padx=10)
        entry.bind("<Return>", lambda e: self.save_new_location(popup, entry))
        ctk.CTkButton(popup, text="Update", command=lambda: self.save_new_location(popup, entry)).pack(pady=5)
        entry.focus()

    def save_new_location(self, popup, entry):
        new_city = entry.get().strip()
        if new_city:
            self.location_name_var.set(new_city)
            backend.save_location_preference(new_city)
            self.update_weather(new_city)
        popup.destroy()

        
        
