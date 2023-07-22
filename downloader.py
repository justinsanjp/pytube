import os
import json
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from pytube import YouTube
from PIL import Image, ImageTk
import requests 

# Funktion zum Herunterladen des YouTube-Thumbnails
def download_thumbnail(yt, thumbnail_path):
    thumbnail_url = yt.thumbnail_url
    thumbnail_image = Image.open(requests.get(thumbnail_url, stream=True).raw)
    thumbnail_image.save(thumbnail_path)

# Funktionen zum Speichern und Laden der Abgeschlossen-Liste
def save_downloads_to_json(downloads):
    with open("downloads.json", "w") as file:
        json.dump(downloads, file)

def load_downloads_from_json():
    if not os.path.exists("downloads.json"):
        return []
    with open("downloads.json", "r") as file:
        return json.load(file)

# Funktion zum Aktualisieren der Abgeschlossen-Liste in der UI
def update_completed_downloads():
    for download in completed_downloads:
        thumbnail_image = Image.open(download["thumbnail_path"])
        thumbnail_image.thumbnail((100, 100))
        thumbnail = ImageTk.PhotoImage(thumbnail_image)
        video_title = download["video_title"]
        channel = download["channel"]

        completed_listbox.insert(tk.END, f"{video_title} - {channel}")

# Funktion zum Herunterladen des Videos
def download_video():
    video_url = entry.get()
    download_type = download_type_var.get()

    try:
        yt = YouTube(video_url)
        thumbnail_path = os.path.join(os.getcwd(), "thumbnails", yt.video_id + ".jpg")
        download_thumbnail(yt, thumbnail_path)

        # Hier den Code zum Herunterladen des Videos oder des Audios einfügen ...
        if download_type == "Video":
            # Download als Video
            file_path = os.path.join(os.getcwd(), "downloads", yt.title + ".mp4")
            stream = yt.streams.get_highest_resolution()
            stream.download(output_path=file_path)
        elif download_type == "MP3":
            # Download als MP3
            file_path = os.path.join(os.getcwd(), "downloads", yt.title + ".mp3")
            stream = yt.streams.filter(only_audio=True).first()
            stream.download(output_path=os.path.join(os.getcwd(), "downloads"))

            # Das heruntergeladene Video hat jetzt eine .mp4-Erweiterung,
            # also ändern wir den Dateinamen in .mp3
            os.rename(os.path.join(os.getcwd(), "downloads", yt.title + ".mp4"), file_path)

        # Download-Warteschlange aktualisieren
        completed_downloads.append({
            "thumbnail_path": thumbnail_path,
            "video_title": yt.title,
            "channel": yt.author,
            "file_path": file_path,
        })
        save_downloads_to_json(completed_downloads)

        # Aktualisiere die Abgeschlossen-Liste in der UI
        completed_listbox.delete(0, tk.END)
        update_completed_downloads()

        status_label.config(text="Video wurde erfolgreich heruntergeladen!")
    except Exception as e:
        status_label.config(text="Fehler beim Herunterladen des Videos: " + str(e))

# GUI erstellen
window = tk.Tk()
window.title("YouTube Video Downloader")
window.geometry("800x800")

label = tk.Label(window, text="Gib den YouTube Video-Link ein:")
label.pack()

entry = tk.Entry(window, width=50)
entry.pack()

# Dropdown-Menü für den Download-Typ (Video oder MP3)
download_type_var = tk.StringVar()
download_type_var.set("Video")
download_type_menu = ttk.Combobox(window, textvariable=download_type_var, values=["Video", "MP3"])
download_type_menu.pack()

download_button = tk.Button(window, text="Herunterladen", command=download_video)
download_button.pack()

status_label = tk.Label(window, text="")
status_label.pack()

# Download-Warteschlange als Scrollbar-Liste
queue_label = tk.Label(window, text="Download Warteschlange")
queue_label.pack()

queue_listbox = tk.Listbox(window, width=50, height=10)
queue_listbox.pack()

# Abgeschlossene Downloads als Scrollbar-Liste
completed_label = tk.Label(window, text="Abgeschlossen")
completed_label.pack()

completed_listbox = tk.Listbox(window, width=50, height=10)
completed_listbox.pack()

# Initialisiere die Abgeschlossen-Liste und lade die gespeicherten Downloads
completed_downloads = load_downloads_from_json()
update_completed_downloads()

window.mainloop()
