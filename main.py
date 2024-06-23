import os
import json
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from pytube import YouTube, Playlist
from PIL import Image, ImageTk
import requests
import importlib.util
import threading  # Import for multithreading

# Path to the language files folder
LANG_FOLDER = "./lang"

# Function to load the language file with a filter
def load_language(language_code):
    try:
        spec = importlib.util.spec_from_file_location(language_code, os.path.join(LANG_FOLDER, f"{language_code}.py"))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Add filter for language file
        if "# Don't show in selection: true" in module.strings.values():
            return None  # If filter condition is met, return None
        
        return module.strings
    except Exception as e:
        print(f"Error loading language file {language_code}: {e}")
        return {}

# Load the default language (English)
strings = load_language("English")

# Function to create folders if they do not exist
def create_folders():
    if not os.path.exists("thumbnails"):
        os.makedirs("thumbnails")
    if not os.path.exists("downloads"):
        os.makedirs("downloads")

# Function to download the YouTube thumbnail
def download_thumbnail(yt, thumbnail_path):
    thumbnail_url = yt.thumbnail_url
    thumbnail_image = Image.open(requests.get(thumbnail_url, stream=True).raw)
    thumbnail_image.save(thumbnail_path)

# Functions to save and load the completed downloads list
def save_downloads_to_json(downloads):
    with open("downloads.json", "w") as file:
        json.dump(downloads, file)

def load_downloads_from_json():
    if not os.path.exists("downloads.json"):
        return []
    with open("downloads.json", "r") as file:
        return json.load(file)

# Function to update the completed downloads list in the UI
def update_completed_downloads():
    completed_listbox.delete(0, tk.END)
    for download in completed_downloads:
        thumbnail_image = Image.open(download["thumbnail_path"])
        thumbnail_image.thumbnail((100, 100))
        thumbnail = ImageTk.PhotoImage(thumbnail_image)
        video_title = download["video_title"]
        channel = download["channel"]

        completed_listbox.insert(tk.END, f"{video_title} - {channel}")

# Function to download a playlist
def download_playlist(playlist_url):
    playlist = Playlist(playlist_url)
    for video_url in playlist.video_urls:
        download_video(video_url)

# Function to download a video
def download_video(video_url):
    try:
        yt = YouTube(video_url)
        
        # Create folders if they do not exist
        create_folders()
        
        thumbnail_path = os.path.join(os.getcwd(), "thumbnails", yt.video_id + ".jpg")
        download_thumbnail(yt, thumbnail_path)

        if download_type_var.get() == strings["video_option"]:
            # Download as video
            file_path = os.path.join(os.getcwd(), "downloads", yt.title + ".mp4")
            stream = get_selected_stream(yt)
            stream.download(output_path=file_path)
        elif download_type_var.get() == strings["mp3_option"]:
            # Download as MP3
            file_path = os.path.join(os.getcwd(), "downloads", yt.title + ".mp3")
            stream = yt.streams.filter(only_audio=True).first()
            stream.download(output_path=os.path.join(os.getcwd(), "downloads"))
            # The downloaded video now has a .mp4 extension,
            # so we rename the file to .mp3
            os.rename(os.path.join(os.getcwd(), "downloads", yt.title + ".mp4"), file_path)

        # Update the download queue
        completed_downloads.append({
            "thumbnail_path": thumbnail_path,
            "video_title": yt.title,
            "channel": yt.author,
            "file_path": file_path,
        })
        save_downloads_to_json(completed_downloads)

        # Update the completed downloads list in the UI
        window.after(0, update_completed_downloads)  # Call UI update in the main thread

        status_label.config(text=strings["download_success"])
    except Exception as e:
        status_label.config(text=strings["download_error"] + str(e))

# Function to select the stream quality
def get_selected_stream(yt):
    selected_quality = quality_var.get()
    if selected_quality == strings["highest_resolution"]:
        return yt.streams.get_highest_resolution()
    elif selected_quality == strings["lowest_resolution"]:
        return yt.streams.get_lowest_resolution()
    elif selected_quality == strings["video_audio_separate"]:
        return yt.streams.filter(progressive=True, file_extension='mp4').first()
    else:
        return yt.streams.first()  # Fallback to the first available quality

# Function to start the download (depending on whether a playlist or a video URL is entered)
def start_download():
    url = entry.get()
    if "playlist?list=" in url:
        threading.Thread(target=download_playlist, args=(url,)).start()
    else:
        threading.Thread(target=download_video, args=(url,)).start()

# Function to change the language
def change_language(event=None):
    global strings
    language_code = language_var.get()
    strings = load_language(language_code)
    update_ui_language()

# Function to update the UI texts after changing the language
def update_ui_language():
    window.title(strings["window_title"])
    label.config(text=strings["enter_url_label"])
    download_type_menu.config(values=[strings["video_option"], strings["mp3_option"]])
    quality_menu.config(values=[strings["highest_resolution"], strings["lowest_resolution"], strings["video_audio_separate"]])
    download_button.config(text=strings["download_button"])
    status_label.config(text="")
    queue_label.config(text=strings["queue_label"])
    completed_label.config(text=strings["completed_label"])

    # Update the last selected option in the dropdown menu after changing the language
    current_download_type = download_type_var.get()
    download_type_menu.set(current_download_type)

# Create the GUI
window = tk.Tk()
window.title(strings["window_title"])
window.geometry("800x800")

# Load the available language files and apply the filter
available_languages = []
for file in os.listdir(LANG_FOLDER):
    if file.endswith(".py"):
        language_code = file.split(".")[0]
        filtered_strings = load_language(language_code)
        if filtered_strings is not None:
            available_languages.append(language_code)

# Dropdown menu for language selection (moved to the top left)
language_var = tk.StringVar()
language_var.set("English")  # Default language
language_menu = ttk.Combobox(window, textvariable=language_var, values=available_languages, state="readonly", width=10)
language_menu.place(relx=0.02, rely=0.02, anchor=tk.NW)  # Position moved to the top left
language_menu.bind("<<ComboboxSelected>>", change_language)

label = tk.Label(window, text=strings["enter_url_label"])
label.pack()

entry = tk.Entry(window, width=50)
entry.pack()

# Dropdown menu for download type (video or MP3)
download_type_var = tk.StringVar()
download_type_var.set(strings["video_option"])
download_type_menu = ttk.Combobox(window, textvariable=download_type_var, values=[strings["video_option"], strings["mp3_option"]], state="readonly")
download_type_menu.pack()

# Dropdown menu for quality selection
quality_var = tk.StringVar()
quality_var.set(strings["highest_resolution"])
quality_menu = ttk.Combobox(window, textvariable=quality_var, values=[strings["highest_resolution"], strings["lowest_resolution"], strings["video_audio_separate"]], state="readonly")
quality_menu.pack()

download_button = tk.Button(window, text=strings["download_button"], command=start_download)
download_button.pack()

status_label = tk.Label(window, text="")
status_label.pack()

# Download queue as a scrollbar list
queue_label = tk.Label(window, text=strings["queue_label"])
queue_label.pack()

queue_listbox = tk.Listbox(window, width=50, height=10)
queue_listbox.pack()

# Completed downloads as a scrollbar list
completed_label = tk.Label(window, text=strings["completed_label"])
completed_label.pack()

completed_listbox = tk.Listbox(window, width=50, height=10)
completed_listbox.pack()

# Initialize the completed downloads list and load the saved downloads
completed_downloads = load_downloads_from_json()
update_completed_downloads()

# Initialize the UI language
update_ui_language()

window.mainloop()
