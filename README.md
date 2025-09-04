AI Assistant GUI

A modern Python AI assistant GUI built with CustomTkinter. Features a beautiful top bar showing: 🕓 Clock & date 🌤️ Dynamic weather details (temperature, humidity, AQI, precipitation, condition, location) 📊 Live system info (CPU, RAM, Disk with sparkline graphs, uptime, battery, IP) 🤖 AI status with animated dots: “Listening...”, “Thinking...”, “Generating...” etc.

Screenshot: (add your screenshot path here)

✨ Features:

✅ Beautiful top bar layout (left: app name & AI status; middle: system stats; right: weather) ✅ Animated AI status label ✅ Dynamic sparkline graphs for real-time CPU, RAM, and Disk usage ✅ Weather section with large temperature, icons, and matrix of details ✅ Responsive design: resizes smoothly on window resize ✅ Custom fonts & icon support ✅ Modular, clean code (TopBar as a custom CTkFrame)

📦 Installation:

Clone the repository: git clone Clone the repository: git clone https://github.com/nikita0109balwada/AURA_ASSISTANT.git cd AURA_ASSISTANT

Install dependencies: pip install -r requirements.txt

Required packages include:

customtkinter
psutil
matplotlib
(Optional) pynvml if you plan to add GPU usage
pillow (if using image icons)
🛠 Usage:

Make sure your fonts and icons are in the correct folders:

/fonts ├─ DAGGERSQUARE.ttf ├─ Bord Demo.ttf └─ ... others

/icons ├─ weather.png ├─ location.png └─ ...

Run the main file: python Main.py

The top bar will appear showing live system stats, current weather, and AI status.

📌 Structure:

Main.py (Main application file) top_bar.py (Custom TopBar class with weather & system info) backend.py file with all backend logic /fonts (Custom fonts) /icons (Icons for weather, location, etc.) README.md requirements.txt

✏️ Customization:

Change fonts by editing fonts dictionary and loading with CTkFont
Replace emoji placeholders with your icon images (use CTkImage)
Adjust sparkline colors and background in create_sparkline
Modify AI status text & animation speed in animate_status
🚀 Example AI status usage: topbar.set_status("Listening") topbar.set_status("Generating") topbar.set_status("Thinking")

📸 Screenshots: 
<img width="750" height="135" alt="Aura4" src="https://github.com/user-attachments/assets/a12dccdc-a247-4504-9e3a-73ea631f399e" />
<img width="1919" height="1079" alt="Aura3" src="https://github.com/user-attachments/assets/6fbdaf67-c80a-4273-b921-e2e590b22c3d" />
<img width="1121" height="853" alt="Aura2" src="https://github.com/user-attachments/assets/948e262c-12b3-4789-97d7-2befac323b33" />
<img width="1120" height="847" alt="Aura1" src="https://github.com/user-attachments/assets/42ef1747-3ef3-4d4c-bc72-e9fd09906253" />



📝 License: MIT License. Feel free to use, modify, and share!
