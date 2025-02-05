import os
import re
import threading
import requests
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
from pytube import Playlist

# Replace with your actual RapidAPI key (use environment variables for security)
RAPIDAPI_KEY = os.getenv('RAPIDAPI_KEY', '703cbef966mshe75a704d906e8c2p13829djsn0a2a4330afaa')

# API endpoint for YouTube to MP3 conversion
API_URL = "https://youtube-mp36.p.rapidapi.com/dl"

def extract_video_id(url_or_id):
    """
    Extracts the video ID from a YouTube URL or returns the ID if it's already provided.
    """
    youtube_regex = (
        r'(?:https?:\/\/)?(?:www\.)?'
        r'(?:youtube\.com\/(?:watch\?v=|embed\/|v\/)|youtu\.be\/)'
        r'([a-zA-Z0-9_-]{11})'
    )
    match = re.search(youtube_regex, url_or_id)
    return match.group(1) if match else url_or_id if len(url_or_id) == 11 else None

def fetch_video_metadata(video_id):
    """
    Fetches video metadata (title, thumbnail, etc.) using the YouTube Data API or similar service.
    """
    headers = {
        "x-rapidapi-host": "youtube-mp36.p.rapidapi.com",
        "x-rapidapi-key": RAPIDAPI_KEY
    }
    querystring = {"id": video_id}
    response = requests.get(API_URL, headers=headers, params=querystring)
    data = response.json()
    return data if data.get('status') == 'ok' else None

def show_video_preview(video_id):
    """
    Displays the video thumbnail and metadata in the GUI.
    """
    metadata = fetch_video_metadata(video_id)
    if metadata:
        # Update preview label with thumbnail
        thumbnail_url = f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"
        response = requests.get(thumbnail_url, stream=True)
        image = Image.open(response.raw)
        image.thumbnail((200, 200))
        photo = ImageTk.PhotoImage(image)
        preview_label.config(image=photo)
        preview_label.image = photo

        # Update metadata labels
        title_label.config(text=f"Title: {metadata['title']}")
        status_label.config(text="Ready to download.")
    else:
        messagebox.showerror("Error", "Failed to fetch video metadata.")

def download_youtube_mp3(mp3_url, output_dir, title):
    """
    Downloads the MP3 file with progress tracking.
    """
    try:
        response = requests.get(mp3_url, stream=True)
        total_size = int(response.headers.get('content-length', 0))
        block_size = 1024  # 1 KB
        downloaded = 0

        file_path = os.path.join(output_dir, f"{title}.mp3")
        with open(file_path, 'wb') as f:
            for data in response.iter_content(block_size):
                downloaded += len(data)
                f.write(data)
                progress = (downloaded / total_size) * 100
                progress_bar['value'] = progress
                speed = downloaded / (progress / 100) if progress > 0 else 0
                speed_label.config(text=f"Speed: {speed:.2f} KB/s")
                root.update_idletasks()

        save_history(file_path)
        status_label.config(text=f"Download completed: {title}.mp3")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def save_history(file_path):
    """
    Saves download history to a file.
    """
    with open("history.txt", "a") as f:
        f.write(f"{file_path}\n")

def toggle_theme(theme_name):
    """
    Toggles between predefined color themes.
    """
    themes = {
        "Light": {"bg": "#f0f0f0", "fg": "#333333", "button_bg": "#ff5722", "button_fg": "white"},
        "Dark": {"bg": "#2d2d2d", "fg": "white", "button_bg": "#4caf50", "button_fg": "white"},
        "Ocean": {"bg": "#e3f2fd", "fg": "#1565c0", "button_bg": "#1e88e5", "button_fg": "white"},
        "Sunset": {"bg": "#ffebee", "fg": "#d32f2f", "button_bg": "#f44336", "button_fg": "white"},
    }

    theme = themes[theme_name]
    root.configure(bg=theme["bg"])
    for widget in root.winfo_children():
        if isinstance(widget, tk.Label):
            widget.config(bg=theme["bg"], fg=theme["fg"])
        elif isinstance(widget, tk.Frame):
            widget.config(bg=theme["bg"])
        elif isinstance(widget, tk.Button):
            widget.config(bg=theme["button_bg"], fg=theme["button_fg"])

def main():
    global root, preview_label, title_label, status_label, progress_bar, speed_label

    # Enable high DPI awareness
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except:
        pass

    # Create the main application window
    root = tk.Tk()
    root.title("YouTube to MP3 Downloader")
    root.geometry("800x600")
    root.resizable(False, False)
    root.configure(bg="#f0f0f0")

    # Variables
    url_or_id = tk.StringVar()
    output_dir = tk.StringVar(value=os.getcwd())

    # Title Label
    title_frame = tk.Frame(root, bg="#f0f0f0")
    title_frame.pack(pady=10)
    tk.Label(title_frame, text="YouTube to MP3 Downloader", font=("Arial", 24, "bold"), bg="#f0f0f0", fg="#ff5722").pack()

    # Input Frame
    input_frame = tk.Frame(root, bg="#f0f0f0")
    input_frame.pack(pady=10)

    tk.Label(input_frame, text="YouTube URL or ID:", font=("Arial", 12), bg="#f0f0f0", fg="#333333").grid(row=0, column=0, padx=5, pady=5, sticky="w")
    entry = tk.Entry(input_frame, textvariable=url_or_id, width=50, font=("Arial", 12), relief="solid", bd=1)
    entry.grid(row=0, column=1, padx=5, pady=5)
    preview_button = tk.Button(input_frame, text="Preview", font=("Arial", 10), bg="#ff5722", fg="white", relief="flat", command=lambda: show_video_preview(extract_video_id(url_or_id.get())))
    preview_button.grid(row=0, column=2, padx=5, pady=5)

    # Output Directory Frame
    output_frame = tk.Frame(root, bg="#f0f0f0")
    output_frame.pack(pady=10)

    tk.Label(output_frame, text="Output Directory:", font=("Arial", 12), bg="#f0f0f0", fg="#333333").grid(row=0, column=0, padx=5, pady=5, sticky="w")
    tk.Entry(output_frame, textvariable=output_dir, width=50, font=("Arial", 12), state='readonly').grid(row=0, column=1, padx=5, pady=5)
    browse_button = tk.Button(output_frame, text="Browse", font=("Arial", 10), bg="#4caf50", fg="white", relief="flat", command=lambda: output_dir.set(filedialog.askdirectory()))
    browse_button.grid(row=0, column=2, padx=5, pady=5)

    # Video Preview
    preview_frame = tk.Frame(root, bg="#f0f0f0")
    preview_frame.pack(pady=10)

    preview_label = tk.Label(preview_frame, bg="#f0f0f0")
    preview_label.grid(row=0, column=0, padx=10, pady=10)
    title_label = tk.Label(preview_frame, text="Title: N/A", font=("Arial", 12), bg="#f0f0f0", fg="#333333")
    title_label.grid(row=1, column=0, padx=10, pady=5)

    # Progress Bar and Speed Label
    progress_bar = ttk.Progressbar(root, orient="horizontal", length=600, mode="determinate")
    progress_bar.pack(pady=10)

    speed_label = tk.Label(root, text="Speed: 0 KB/s", font=("Arial", 12), bg="#f0f0f0", fg="#333333")
    speed_label.pack(pady=5)

    # Buttons
    button_frame = tk.Frame(root, bg="#f0f0f0")
    button_frame.pack(pady=10)

    download_button = tk.Button(button_frame, text="Download MP3", font=("Arial", 12), bg="#2196f3", fg="white", relief="flat", command=lambda: threading.Thread(target=download_youtube_mp3, args=(fetch_video_metadata(extract_video_id(url_or_id.get()))['link'], output_dir.get(), fetch_video_metadata(extract_video_id(url_or_id.get()))['title'])).start())
    download_button.grid(row=0, column=0, padx=10)

    theme_frame = tk.Frame(root, bg="#f0f0f0")
    theme_frame.pack(pady=10)

    tk.Label(theme_frame, text="Themes:", font=("Arial", 12), bg="#f0f0f0", fg="#333333").grid(row=0, column=0, padx=5, pady=5)
    tk.Button(theme_frame, text="Light", font=("Arial", 10), bg="#ff5722", fg="white", relief="flat", command=lambda: toggle_theme("Light")).grid(row=0, column=1, padx=5, pady=5)
    tk.Button(theme_frame, text="Dark", font=("Arial", 10), bg="#4caf50", fg="white", relief="flat", command=lambda: toggle_theme("Dark")).grid(row=0, column=2, padx=5, pady=5)
    tk.Button(theme_frame, text="Ocean", font=("Arial", 10), bg="#1e88e5", fg="white", relief="flat", command=lambda: toggle_theme("Ocean")).grid(row=0, column=3, padx=5, pady=5)
    tk.Button(theme_frame, text="Sunset", font=("Arial", 10), bg="#f44336", fg="white", relief="flat", command=lambda: toggle_theme("Sunset")).grid(row=0, column=4, padx=5, pady=5)

    # Status Label
    status_label = tk.Label(root, text="", font=("Arial", 12), fg="#ff5722", bg="#f0f0f0")
    status_label.pack(pady=10)

    # Run the application
    root.mainloop()

if __name__ == "__main__":
    main()
