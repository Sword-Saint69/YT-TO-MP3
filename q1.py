import os
import re
import requests
import tkinter as tk
from tkinter import messagebox, filedialog, ttk
from threading import Thread

# Replace with your actual RapidAPI key (use environment variables for security)
RAPIDAPI_KEY = os.getenv('RAPIDAPI_KEY', '703cbef966mshe75a704d906e8c2p13829djsn0a2a4330afaa')

# API endpoint for YouTube to MP3 conversion
API_URL = "https://youtube-mp36.p.rapidapi.com/dl"

def extract_video_id(url_or_id):
    """
    Extracts the video ID from a YouTube URL or returns the ID if it's already provided.
    Supports both full URLs and direct video IDs.
    """
    youtube_regex = (
        r'(?:https?:\/\/)?(?:www\.)?'
        r'(?:youtube\.com\/(?:watch\?v=|embed\/|v\/)|youtu\.be\/)'
        r'([a-zA-Z0-9_-]{11})'
    )

    match = re.search(youtube_regex, url_or_id)
    if match:
        return match.group(1)  # Return the extracted video ID
    elif len(url_or_id) == 11:
        return url_or_id
    else:
        raise ValueError("Invalid YouTube URL or ID")

def download_youtube_mp3(video_url_or_id, output_dir, status_label, progress_bar):
    try:
        # Extract the video ID from the input (URL or direct ID)
        video_id = extract_video_id(video_url_or_id)

        # Query parameters: YouTube video ID
        querystring = {"id": video_id}

        # Headers for the API request
        headers = {
            "x-rapidapi-host": "youtube-mp36.p.rapidapi.com",
            "x-rapidapi-key": RAPIDAPI_KEY
        }

        # Send a GET request to the API
        response = requests.get(API_URL, headers=headers, params=querystring)
        response.raise_for_status()  # Raise an error for bad status codes

        # Parse the JSON response
        data = response.json()

        if data.get('status') == 'ok':
            # Extract the download link for the MP3 file
            mp3_url = data['link']
            title = data['title']

            # Download the MP3 file
            status_label.config(text=f"Downloading: {title}.mp3")
            progress_bar.start()  # Start the progress bar animation

            mp3_response = requests.get(mp3_url, stream=True)
            total_size = int(mp3_response.headers.get('content-length', 0))
            block_size = 1024  # 1 KB
            downloaded = 0

            # Save the MP3 file locally
            file_path = os.path.join(output_dir, f"{title}.mp3")
            with open(file_path, 'wb') as f:
                for data in mp3_response.iter_content(block_size):
                    downloaded += len(data)
                    f.write(data)
                    progress = (downloaded / total_size) * 100
                    progress_bar['value'] = progress
                    root.update_idletasks()  # Update the GUI

            progress_bar.stop()  # Stop the progress bar animation
            status_label.config(text=f"Download completed: {title}.mp3")
            messagebox.showinfo("Success", f"MP3 downloaded successfully: {file_path}")
        else:
            status_label.config(text="Error: Unable to fetch MP3 link.")
            messagebox.showerror("Error", data.get('msg', 'Unknown error'))

    except requests.exceptions.RequestException as e:
        status_label.config(text=f"An error occurred: {e}")
        messagebox.showerror("Error", str(e))
    except ValueError as ve:
        status_label.config(text=f"Invalid input: {ve}")
        messagebox.showerror("Error", str(ve))

def start_download(url_or_id, output_dir, status_label, progress_bar):
    """
    Starts the download process in a separate thread to avoid freezing the GUI.
    """
    Thread(target=download_youtube_mp3, args=(url_or_id, output_dir, status_label, progress_bar)).start()

def select_output_directory(output_dir):
    """
    Opens a dialog to select the output directory for saving the MP3 file.
    """
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        output_dir.set(folder_selected)

def main():
    global root  # Make root accessible to other functions
    # Create the main application window
    root = tk.Tk()
    root.title("YouTube to MP3 Downloader")
    root.geometry("600x400")
    root.resizable(False, False)
    root.configure(bg="#f0f0f0")  # Set background color

    # Variables
    url_or_id = tk.StringVar()
    output_dir = tk.StringVar(value=os.getcwd())  # Default to current working directory

    # Title Label
    tk.Label(root, text="YouTube to MP3 Downloader", font=("Arial", 20, "bold"), bg="#f0f0f0").pack(pady=10)

    # Input Frame
    input_frame = tk.Frame(root, bg="#f0f0f0")
    input_frame.pack(pady=10)

    tk.Label(input_frame, text="YouTube URL or ID:", font=("Arial", 12), bg="#f0f0f0").grid(row=0, column=0, padx=5, pady=5, sticky="w")
    tk.Entry(input_frame, textvariable=url_or_id, width=50, font=("Arial", 12)).grid(row=0, column=1, padx=5, pady=5)

    # Output Directory Frame
    output_frame = tk.Frame(root, bg="#f0f0f0")
    output_frame.pack(pady=10)

    tk.Label(output_frame, text="Output Directory:", font=("Arial", 12), bg="#f0f0f0").grid(row=0, column=0, padx=5, pady=5, sticky="w")
    tk.Entry(output_frame, textvariable=output_dir, width=50, font=("Arial", 12), state='readonly').grid(row=0, column=1, padx=5, pady=5)
    tk.Button(output_frame, text="Browse", font=("Arial", 10), command=lambda: select_output_directory(output_dir)).grid(row=0, column=2, padx=5, pady=5)

    # Progress Bar
    progress_bar = ttk.Progressbar(root, orient="horizontal", length=500, mode="determinate")
    progress_bar.pack(pady=10)

    # Status Label
    status_label = tk.Label(root, text="", font=("Arial", 12), fg="green", bg="#f0f0f0")
    status_label.pack(pady=10)

    # Download Button
    tk.Button(root, text="Download MP3", font=("Arial", 14, "bold"), bg="#4CAF50", fg="white", command=lambda: start_download(url_or_id.get(), output_dir.get(), status_label, progress_bar)).pack(pady=20)

    # Run the application
    root.mainloop()

if __name__ == "__main__":
    main()
