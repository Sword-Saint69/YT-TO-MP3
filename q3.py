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

# Global Variables
download_queue = []
is_paused = False
current_download = None

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

def add_to_queue(url_or_id):
    """
    Adds a video or playlist to the download queue.
    """
    video_id = extract_video_id(url_or_id)
    if not video_id:
        messagebox.showerror("Error", "Invalid YouTube URL or ID.")
        return

    if "playlist" in url_or_id:
        # Handle playlist
        playlist = Playlist(url_or_id)
        for video in playlist.video_urls:
            download_queue.append(video)
    else:
        # Handle single video
        download_queue.append(url_or_id)

    queue_label.config(text=f"Queue: {len(download_queue)} items")
    messagebox.showinfo("Success", "Added to download queue.")

def process_queue():
    """
    Processes the download queue sequentially.
    """
    global current_download
    while download_queue:
        if is_paused:
            status_label.config(text="Download paused.")
            return

        current_download = download_queue.pop(0)
        video_id = extract_video_id(current_download)
        metadata = fetch_video_metadata(video_id)

        if metadata:
            download_youtube_mp3(metadata['link'], output_dir.get(), metadata['title'])
        else:
            messagebox.showerror("Error", "Failed to fetch video metadata.")

    status_label.config(text="All downloads completed.")
    current_download = None

def download_youtube_mp3(mp3_url, output_dir, title):
    """
    Downloads the MP3 file with progress tracking and pause functionality.
    """
    try:
        response = requests.get(mp3_url, stream=True)
        total_size = int(response.headers.get('content-length', 0))
        block_size = 1024  # 1 KB
        downloaded = 0

        file_path = os.path.join(output_dir, f"{title}.mp3")
        with open(file_path, 'wb') as f:
            for data in response.iter_content(block_size):
                if is_paused:
                    status_label.config(text="Download paused.")
                    return

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

def toggle_pause():
    """
    Toggles the pause state of the download.
    """
    global is_paused
    is_paused = not is_paused
    pause_button.config(text="Resume" if is_paused else "Pause")

def toggle_theme():
    """
    Toggles between light and dark themes.
    """
    if root.cget("bg") == "#f0f0f0":
        root.configure(bg="#2d2d2d")
        for widget in root.winfo_children():
            if isinstance(widget, tk.Label):
                widget.config(bg="#2d2d2d", fg="white")
            elif isinstance(widget, tk.Frame):
                widget.config(bg="#2d2d2d")
    else:
        root.configure(bg="#f0f0f0")
        for widget in root.winfo_children():
            if isinstance(widget, tk.Label):
                widget.config(bg="#f0f0f0", fg="black")
            elif isinstance(widget, tk.Frame):
                widget.config(bg="#f0f0f0")

def main():
    global root, preview_label, title_label, status_label, progress_bar, speed_label, queue_label, pause_button

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

    # Load Icons
    play_icon = ImageTk.PhotoImage(Image.open("icons/play.png").resize((20, 20)))
    pause_icon = ImageTk.PhotoImage(Image.open("icons/pause.png").resize((20, 20)))
    theme_icon = ImageTk.PhotoImage(Image.open("icons/theme.png").resize((20, 20)))

    # Variables
    url_or_id = tk.StringVar()
    output_dir = tk.StringVar(value=os.getcwd())

    # Title Label with Gradient Effect
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

    # Hover Effect for Buttons
    def on_hover(button, color):
        button.config(bg=color)

    def on_leave(button, color):
        button.config(bg=color)

    preview_button.bind("<Enter>", lambda e: on_hover(preview_button, "#ff7043"))
    preview_button.bind("<Leave>", lambda e: on_leave(preview_button, "#ff5722"))

    # Output Directory Frame
    output_frame = tk.Frame(root, bg="#f0f0f0")
    output_frame.pack(pady=10)

    tk.Label(output_frame, text="Output Directory:", font=("Arial", 12), bg="#f0f0f0", fg="#333333").grid(row=0, column=0, padx=5, pady=5, sticky="w")
    tk.Entry(output_frame, textvariable=output_dir, width=50, font=("Arial", 12), state='readonly').grid(row=0, column=1, padx=5, pady=5)
    browse_button = tk.Button(output_frame, text="Browse", font=("Arial", 10), bg="#4caf50", fg="white", relief="flat", command=lambda: output_dir.set(filedialog.askdirectory()))
    browse_button.grid(row=0, column=2, padx=5, pady=5)

    browse_button.bind("<Enter>", lambda e: on_hover(browse_button, "#66bb6a"))
    browse_button.bind("<Leave>", lambda e: on_leave(browse_button, "#4caf50"))

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

    # Queue Label
    queue_label = tk.Label(root, text="Queue: 0 items", font=("Arial", 12), bg="#f0f0f0", fg="#333333")
    queue_label.pack(pady=5)

    # Buttons
    button_frame = tk.Frame(root, bg="#f0f0f0")
    button_frame.pack(pady=10)

    add_button = tk.Button(button_frame, text="Add to Queue", font=("Arial", 12), bg="#2196f3", fg="white", relief="flat", command=lambda: add_to_queue(url_or_id.get()))
    add_button.grid(row=0, column=0, padx=10)
    add_button.bind("<Enter>", lambda e: on_hover(add_button, "#42a5f5"))
    add_button.bind("<Leave>", lambda e: on_leave(add_button, "#2196f3"))

    start_button = tk.Button(button_frame, text="Start Queue", font=("Arial", 12), bg="#4caf50", fg="white", relief="flat", command=lambda: threading.Thread(target=process_queue).start())
    start_button.grid(row=0, column=1, padx=10)
    start_button.bind("<Enter>", lambda e: on_hover(start_button, "#66bb6a"))
    start_button.bind("<Leave>", lambda e: on_leave(start_button, "#4caf50"))

    pause_button = tk.Button(button_frame, text="Pause", font=("Arial", 12), bg="#ff5722", fg="white", relief="flat", image=pause_icon, compound="left", command=toggle_pause)
    pause_button.grid(row=0, column=2, padx=10)
    pause_button.bind("<Enter>", lambda e: on_hover(pause_button, "#ff7043"))
    pause_button.bind("<Leave>", lambda e: on_leave(pause_button, "#ff5722"))

    theme_button = tk.Button(button_frame, text="Toggle Theme", font=("Arial", 12), bg="#9c27b0", fg="white", relief="flat", image=theme_icon, compound="left", command=toggle_theme)
    theme_button.grid(row=0, column=3, padx=10)
    theme_button.bind("<Enter>", lambda e: on_hover(theme_button, "#ab47bc"))
    theme_button.bind("<Leave>", lambda e: on_leave(theme_button, "#9c27b0"))

    # Status Label
    status_label = tk.Label(root, text="", font=("Arial", 12), fg="#ff5722", bg="#f0f0f0")
    status_label.pack(pady=10)

    # Run the application
    root.mainloop()

if __name__ == "__main__":
    main()
