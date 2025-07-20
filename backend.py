import speech_recognition as sr
from groq import Groq
from gtts import gTTS
import random
import os
from langdetect import detect, LangDetectException
from langcodes import Language
import tkinter as tk
from tkinter import filedialog
from fpdf import FPDF
import re
import time
import replicate
from PIL import Image
import requests
from io import BytesIO
from dotenv import load_dotenv
import json
import pygame

import requests
from requests.auth import HTTPBasicAuth

import os
import json

SETTINGS_FILE = "settings.json"

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
    return "Delhi"  # default if none saved

def save_location_preference(city_name):
    try:
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, "r") as f:
                settings = json.load(f)
        else:
            settings = {}
        settings["city"] = city_name
        with open(SETTINGS_FILE, "w") as f:
            json.dump(settings, f)
        print(f"[Settings] Saved city: {city_name}")
    except Exception as e:
        print(f"[Settings] Error saving city: {e}")



display_message_callback = None
def display_message(text, sender):
    print(f"[Backend] display_message: {sender}: {text}")
    if display_message_callback and callable(display_message_callback):
        display_message_callback(text, sender)


load_dotenv()
topbar_status_callback = None
def set_topbar_status(status):
    if topbar_status_callback and callable(topbar_status_callback):
        topbar_status_callback(status)


GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    print("Error: GROQ_API_KEY not set. Please set the key in your environment variables or .env file.")
    exit()

REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")
if not REPLICATE_API_TOKEN:
    print("Error: REPLICATE_API_TOKEN not set. Please set the key in your environment variables or .env file.")
    exit()
os.environ["REPLICATE_API_TOKEN"] = REPLICATE_API_TOKEN  

IMG_BB_API_KEY = os.getenv("IMG_BB_API_KEY")
if not IMG_BB_API_KEY:
    print("Warning: IMG_BB_API_KEY not set. Image upload functionality might be limited.")

client = Groq(api_key=GROQ_API_KEY)
r = sr.Recognizer()

# --- Global Settings ---
interaction_mode = None
speak_enabled = None
conversation_history = []
last_generated_text = None

# --- Dynamic Greetings ---
GREETINGS = [
    "Hello! How can I assist you today?",
    "Hi there! What can I do for you?",
    "Greetings! Ready for your requests.",
    "Hello! What's on your mind?",
    "Good to see you! How can I help?",
]

# --- Core Functions ---

# --- Image Captioning ---

def upload_image_to_imgbb(image_path, api_key=None):
    """Upload a local image to imgbb.com and get a public URL."""
    if not api_key:
        print("Error: IMG_BB_API_KEY is required to upload images.")
        return None
    try:
        with open(image_path, 'rb') as img_file:
            response = requests.post(
                'https://api.imgbb.com/1/upload', 
                data={'key': api_key}, 
                files={'image': img_file})
        if response.status_code == 200:
            return response.json()['data']['url']
        else:
            print("Error uploading image:", response.json())
            return None
    except Exception as e:
        print(f"Error uploading image: {e}")
        return None

IMAGGA_API_KEY = os.getenv("IMAGGA_API_KEY")
IMAGGA_API_SECRET = os.getenv("IMAGGA_API_SECRET")

def describe_image_with_imagga(image_url):
    """Use Imagga to get tags and build a short description"""
    try:
        response = requests.get(
            "https://api.imagga.com/v2/tags",
            params={"image_url": image_url},
            auth=HTTPBasicAuth(IMAGGA_API_KEY, IMAGGA_API_SECRET)
        )
        data = response.json()
        print("[Backend] Imagga raw response:", data)
        if "result" in data and "tags" in data["result"]:
            tags = [t["tag"]["en"] for t in data["result"]["tags"][:5]]
            description = "This image might contain: " + ", ".join(tags)
            return description
        else:
            return "Could not get tags from Imagga."
    except Exception as e:
        print(f"[Backend] Imagga error: {e}")
        return "Sorry, I couldn't analyze the image."

def select_local_image():
    """Open dialog box to select an image."""
    root = tk.Tk()
    root.withdraw()  
    root.lift() 
    root.attributes('-topmost', True) 
    file_path = filedialog.askopenfilename(
        title="Select an Image",
        filetypes=[("Image Files", "*.png *.jpg *.jpeg *.gif *.bmp *.webp")]
    )
    root.destroy()  
    return file_path


def get_image_description_from_path(image_path):
    """Analyze an image given by user, update topbar status dynamically."""
    try:
        set_topbar_status("Analyzing")
        print(f"[Backend] Starting analysis for: {image_path}")

        if IMG_BB_API_KEY:
            print("[Backend] Uploading image to get public URL...")
            image_url = upload_image_to_imgbb(image_path, IMG_BB_API_KEY)
            print(f"[Backend] image_url = {image_url}")
            if image_url:
                description = describe_image_with_imagga(image_url)
                print("[Backend] Got description:", description)
                display_message(description, "assistant")
                
            else:
                print("[Backend] Failed to upload image")
                
        else:
            print("[Backend] Analyzing locally...")
            description = describe_image_with_imagga(image_path)
            print("[Backend] Got description:", description)
            if display_message_callback:
                display_message_callback(description, "assistant")

            

    except Exception as e:
        print(f"[Backend] Error during image analysis: {e}")
        display_message("❌ Failed to analyze the image.", "assistant")
    finally:
        set_topbar_status("Idle")



def get_image_description():
    """Handles the process of getting an image description."""
    # speak_text("Please select an image you want me to analyze.", lang='en')
    image_path = select_local_image()  

    if image_path: 
        print(f"Image selected: {image_path}")
        try:
            set_topbar_status("Analyzing")
            if IMG_BB_API_KEY:
                print("Uploading image to get public URL...")
                image_url = upload_image_to_imgbb(image_path, IMG_BB_API_KEY)
                if image_url:
                    print(f"Image uploaded successfully: {image_url}")
                    description = describe_image_with_imagga(image_url)
                    print("Image Description:", description)
                    speak_text(description)
                else:
                    speak_text("Failed to upload the image for analysis.", lang='en')
            else:
                speak_text("Image upload is not configured. Analyzing locally.", lang='en')
                description = describe_image_with_imagga(image_path)
                print("Image Description:", description)
                speak_text(description)
        finally:
            set_topbar_status("Idle")
    else:
        speak_text("No image was selected.", lang='en')


# --- Image Generation ---

def generate_image(prompt):
    """Generates an image based on the given prompt using Replicate."""
    try:
        output = replicate.run(
            "stability-ai/sdxl:db21e45a3d465e36eaa1a02a7585e8b5c4e1eeb26e245cd72c3b70d3b9b5b9d4",
            input={"prompt": prompt}
        )
        if output:
            print("Generated Image URL:", output[0])
            return output[0]
        else:
            print("No output generated.")
            return None
    except Exception as e:
        print(f"Image generation failed: {e}")
        return None

def show_generated_image(url):
    """Displays the generated image from a URL."""
    try:
        response = requests.get(url)
        img = Image.open(BytesIO(response.content))
        img.show()
    except Exception as e:
        print(f"Couldn't display image: {e}")

def is_image_generation_request(text):
    """Checks if the user input is a request for image generation."""
    keywords = ["generate", "create", "draw", "make"]
    return any(word in text.lower() for word in keywords) and "image" in text.lower()

def handle_image_generation(user_input):
    """Handles the image generation process."""
    print("Aura: Generating image, please wait...")
    try:
        output_url = replicate.run(
            "stability-ai/sdxl:db21e45a3d465e36eaa1a02a7585e8b5c4e1eeb26e245cd72c3b70d3b9b5b9d4",
            input={
                "prompt": user_input,
                "num_outputs": 1,  # 1 image
                "width": 1024,
                "height": 1024,
                "guidance_scale": 7.5,
                "num_inference_steps": 30
            }
        )
        if output_url:
            print(f"Aura: Image generated successfully! Here is the URL:\n{output_url[0]}")
            speak_text("Here’s the image I created based on your prompt.", lang="en")
            show_generated_image(output_url[0])
        else:
            print("Aura: Failed to generate the image.")
            speak_text("Sorry, I couldn't generate the image.", lang="en")
    except Exception as e:
        print(f"Image generation failed: {e}")
        print("Aura: Failed to generate the image.")
        speak_text("Sorry, I encountered an error during image generation.", lang='en')

# --- Speak Function Using GTTS---

def speak_text(text, lang='en'):
    """Speaks the given text using GTTS and plays it with pygame."""
    if not speak_enabled:
        print(f"(Aura speaking disabled): {text}")
        return
    try:
        if not os.path.exists("temp_audio"):
            os.makedirs("temp_audio")
        file_name = f"temp_audio/response_{random.randint(10000, 99999)}.mp3"
        tts = gTTS(text=text, lang=lang, slow = False)
        tts.save(file_name)

        pygame.mixer.init()
        pygame.mixer.music.load(file_name)
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            time.sleep(0.3)

        pygame.mixer.quit()

        try:
            os.remove(file_name)
        except Exception as e:
            print(f"Failed to delete the file: {file_name}. Error: {e}")

    except Exception as e:
        print(f"Error speaking text: {e}")

def record_audio(ask=""):
    """Records audio from the microphone and returns the recognized text."""
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source, duration=0.5) 
        print("Listening...") 
        if ask:
            
            speak_text(ask, lang='en')
            time.sleep(0.5)

        try:
            audio = r.listen(source, timeout=5, phrase_time_limit=10)
            voice_data = r.recognize_google(audio)
            print(f"You said: {voice_data}")
            return voice_data.lower()
        except sr.WaitTimeoutError:
            print("[DEBUG] WaitTimeoutError: No speech detected within the time limit.")
            speak_text("Sorry, I didn't hear anything.", lang='en')
            return ""
        except sr.UnknownValueError:
            print("[DEBUG] UnknownValueError: Speech was unintelligible.")
            speak_text("Sorry, I didn't quite catch that.", lang='en')
            return ""
        except sr.RequestError:
            print("[DEBUG] RequestError: Could not request results from Google Speech Recognition service.")
            speak_text("Sorry, my speech service is currently unavailable.", lang='en')
            return ""
        except Exception as e:
            print(f"[DEBUG] Exception: An error occurred during recording: {e}")
            speak_text("Sorry, an error occurred while trying to listen.", lang='en')
            return ""

def get_text_input(ask=""):
    """Gets text input from the user via the console."""
    if ask:
        print(f"Aura: {ask}") 
    return input("You: ")

def get_user_input(ask=""):
    """Gets input from the user based on the interaction_mode."""
    if interaction_mode == "voice":
        return record_audio(ask)
    else: # Assumes text mode
        return get_text_input(ask)

def detect_language(text):
    """Detects the language (primarily English or Hindi)."""
    try:
        if not text or text.isspace():
            return 'en' 

        detected_lang = detect(text)
        return 'hi' if detected_lang == 'hi' else 'en'

    except LangDetectException:
        return 'en'
    except Exception:
        return 'en'

def update_conversation_history(user_input, bot_response):
    """Adds the user input and bot response to the conversation history."""
    conversation_history.append({"role": "user", "content": user_input})
    conversation_history.append({"role": "assistant", "content": bot_response})
   
def split_response_and_followup(ai_reply):
    """
    Splits an AI reply into the main response and an optional follow-up question.
    Handles variations in capitalization and whitespace for "Follow-up:".
    Uses Regex for robustness.
    """
    if not ai_reply:
        return "", None

    follow_up_match = re.search(r"(?:^|\n)\s*Follow-up:(.*)", ai_reply, re.IGNORECASE | re.DOTALL)

    main_response = ai_reply
    follow_up = None

    if follow_up_match:
        main_response = ai_reply[:follow_up_match.start()]
        follow_up = follow_up_match.group(1).strip()

    main_response = re.sub(r"^\s*Response:", "", main_response, count=1, flags=re.IGNORECASE).strip()

    if follow_up == "":
        follow_up = None

    return main_response, follow_up


def get_ai_response(user_input, lang_code='en'):
    """Gets an AI response from Groq, considering conversation history."""
    global last_generated_text 
    try:
        set_topbar_status("Thinking")
        model = "llama-3.3-70b-versatile"  # Use the appropriate model for your needs

        # Determine language instruction 
        language_name = Language.get(lang_code).display_name() if lang_code == 'hi' else 'English'
        language_instruction = f"Respond clearly and naturally in {language_name}."

        # Simplified system prompt 
        system_prompt = f"""
You are Aura, a helpful, friendly, and concise AI assistant.
{language_instruction}
Keep the following conversation history in mind to provide relevant responses.
If asked to perform an action you cannot do, politely explain the limitation in the appropriate language ({language_name}).
You can save pdf from the text generated summary.
You can generate images .
You can also analyze images if provided.Ask the user to select an image.
If appropriate, you can include a natural follow-up question to encourage conversation, but don't force it.
Do not write two different responses at same time, if possible include both responses in one message.
If user asks you to analyze images, then accept images directly by opening a dialog box to select image.
If no follow-up is needed, just provide the response:
Response: <your main response in the correct language/script>
"""
        messages_to_send = [
            {"role": "system", "content": system_prompt}
        ] + conversation_history + [
            {"role": "user", "content": user_input}
        ]

        response = client.chat.completions.create(
            model=model,
            messages=messages_to_send,
            temperature=0.7,
            max_tokens=1024,
            timeout=15
        )
        ai_full_response = response.choices[0].message.content.strip()

        # Split response here
        main_response, follow_up = split_response_and_followup(ai_full_response)

        # Update last generated text 
        if main_response:
            last_generated_text = main_response
            update_conversation_history(user_input, main_response) 
            if follow_up:
                update_conversation_history("Aura", follow_up) 

        return main_response, follow_up 

    except Exception as e:
        print(f"Aura: Sorry, I encountered an error trying to process that request. ({e})")
        speak_text("Sorry, I encountered an error trying to process that request.", lang='en')
        last_generated_text = None 
        return None, None
    finally:
        print("Finally block running")

        set_topbar_status("Idle") 

def save_pdf_dialog(text, lang='en'):
    """Opens a save file dialog and saves the given text as a PDF."""
    if not text:
        print("[PDF Save Info] No text provided to save.") 
        speak_text("There doesn't seem to be anything to save.", lang=lang)
        return

    speak_text("Okay, where would you like to save the PDF?", lang='en')

    try:
        set_topbar_status("Saving")
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            title="Save your draft as PDF"
        )
        root.destroy()

        print(f"File path chosen: {file_path}")  

        if file_path:
            if not file_path.endswith('.pdf'):
                file_path += '.pdf'

            pdf = FPDF()
            pdf.add_page()
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.set_font("Arial", size=12)

            try:
                cleaned_text = text.encode('latin-1', 'replace').decode('latin-1')
            except Exception:
                cleaned_text = text

            print(f"Cleaned text: {cleaned_text}")  

            pdf.multi_cell(0, 10, cleaned_text)
            pdf.output(file_path)

            speak_text("I've saved the draft as a PDF.", lang=lang)

        else:
            speak_text("Okay, I didn't save the draft.", lang=lang)

    except ImportError:
        print("Error: tkinter library (needed for save dialog) not found or failed.")
        speak_text("Sorry, I'm missing some tools needed to save PDFs.", lang='en')
    except Exception as e:
        print(f"Error: Could not save PDF ({e})")
        speak_text("Sorry, I encountered an error while trying to save the PDF.", lang='en')
    finally:
        set_topbar_status("Idle")

def detect_intent(user_input):
    """
    Detects user intent, focusing on save actions.
    Returns: dict {"intent": "chat" | "save_previous" | "chat_and_save", "query": "..."}
    """
    text = user_input.lower()

    # Image generation intent
    if any(word in text for word in ["generate", "create", "draw", "make"]) and "image" in text:
        return {"intent": "image_generation", "query": text}


    save_previous_keywords = ["save that", "save the last one", "save previous", "save the draft", "isko save karo", "save it"]
    save_current_keywords = ["and save", "and save it", "save as pdf", "save it as pdf", "aur save karo"]

    # Check for saving the previous response first
    if any(keyword in text for keyword in save_previous_keywords):
        if len(text.split()) <= 3:
            return {"intent": "save_previous", "query": user_input}

    # Check if the request includes saving the *current* action's result
    if any(keyword in text for keyword in save_current_keywords):
        if not any(prev_keyword in text for prev_keyword in save_previous_keywords if len(prev_keyword) > 6): # Avoid short overlaps like "save it"
            return {"intent": "chat_and_save", "query": user_input}

    # Default to chat
    return {"intent": "chat", "query": user_input}

def save_chat_history(filepath):
    """Saves the conversation history to a JSON file."""
    try:
        with open(filepath, 'w') as f:
            json.dump(conversation_history, f, indent=4)
        print(f"Chat history saved to {filepath}")
        speak_text(f"Chat history saved.", lang='en')
    except Exception as e:
        print(f"Error saving chat history: {e}")
        speak_text(f"Error saving chat history.", lang='en')

def load_chat_history(filepath):
    """Loads the conversation history from a JSON file."""
    try:
        with open(filepath, 'r') as f:
            loaded_history = json.load(f)
        print(f"Chat history loaded from {filepath}")
        speak_text(f"Chat history loaded.", lang='en')
        return loaded_history
    except FileNotFoundError:
        print("No previous chat history found.")
        return []
    except Exception as e:
        print(f"Error loading chat history: {e}")
        speak_text(f"Error loading chat history.", lang='en')
        return []

# --- Main Execution ---
if __name__ == "__main__":
    print("Initializing...")

    speak_enabled = False
    # 1. Dynamic Greeting
    greeting = random.choice(GREETINGS)
    print(f"Aura: {greeting}")
    speak_enabled = True
    

    
    # 3. Main Interaction Loop
    while True:
        user_input = get_user_input() # Get input based on selected mode

        if not user_input:
            continue

        # Basic Exit Command Check
        exit_keywords = ["exit", "quit", "stop", "goodbye", "bye bye", "band karo", "bas karo", "alvida"]
        if any(exit_word in user_input for exit_word in exit_keywords):
            goodbye_message = "Goodbye! Have a great day."
            print(f"Aura: {goodbye_message}")
            if speak_enabled:
                speak_text(goodbye_message, lang='en')
            break

        # --- Process Request ---
        lang_code = detect_language(user_input)
        intent_data = detect_intent(user_input)
        intent = intent_data.get("intent")
        query = intent_data.get("query")

        if "describe image" in user_input.lower() or "analyze image" in user_input.lower() or "image description" in user_input.lower():
            get_image_description()
            continue # Skip to the next iteration after image description

        if is_image_generation_request(user_input):
            handle_image_generation(user_input)
            continue # Skip to the next iteration after image generation

        if intent == "save_previous":
            if last_generated_text:
                save_pdf_dialog(last_generated_text, lang_code)
            else:
                no_prev_text_msg = "There doesn't seem to be a recent response for me to save."
                print(f"Aura: {no_prev_text_msg}")
                if speak_enabled:
                    speak_text(no_prev_text_msg, lang=lang_code)

        elif intent == "chat" or intent == "chat_and_save":
            main_response, follow_up = get_ai_response(query, lang_code)

            # Output the main response (print and speak)
            if main_response:
                print(f"Aura: {main_response}")
                if speak_enabled:
                    speak_text(main_response, lang=lang_code)
            # If no main response but there's a follow-up 
            elif follow_up and not main_response:
                print(f"Aura: {follow_up}")
                if speak_enabled:
                    speak_text(follow_up, lang=lang_code)
            # Handle case where AI failed to respond entirely
            elif not main_response and not follow_up:
                print(f"Aura: (No response generated)")
                if speak_enabled:
                    speak_text("Sorry, I couldn't generate a response.", lang='en')

            # Automatic Save Logic (if requested in the *same* command)
            if intent == "chat_and_save" and main_response:
                save_pdf_dialog(main_response, lang_code) 

            # Handle follow-up 
            if follow_up:
                # Print follow-up for both modes
                print(f"Aura: {follow_up}")
                # Speak follow-up 
                if speak_enabled:
                    speak_text(follow_up, lang=lang_code)

        else:
            # Fallback for any unexpected intent results
            fallback_message = "Sorry, I'm not sure how to handle that specific request."
            print(f"Aura: {fallback_message}")
            if speak_enabled:
                speak_text(fallback_message, lang='en') # Use English for generic fallback

   