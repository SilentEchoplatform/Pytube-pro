import os
import threading
from pytube import YouTube
import customtkinter as ctk
from tkinter import filedialog, messagebox
from tkinter.ttk import Progressbar
import re

# Setup GUI appearance
ctk.set_appearance_mode("System")  # System theme (light/dark)
ctk.set_default_color_theme("blue")  # Color theme

class YouTubeDownloaderApp:
    def __init__(self, master):
        self.master = master
        master.title("YouTube Video Downloader Pro")
        master.geometry("720x520")
        master.resizable(False, False)
        
        # Try to set window icon (ensure icon.ico exists in same folder)
        try:
            master.iconbitmap("icon.ico")
        except:
            pass
        
        # Create all GUI widgets
        self.create_widgets()
    
    def create_widgets(self):
        # Title frame
        title_frame = ctk.CTkFrame(self.master, corner_radius=10)
        title_frame.pack(pady=20, padx=20, fill="x")
        
        # Application title
        title_label = ctk.CTkLabel(
            title_frame, 
            text="YouTube Video Downloader Pro",
            font=("Arial", 20, "bold")
        )
        title_label.pack(pady=10)
        
        # URL input frame
        url_frame = ctk.CTkFrame(self.master, corner_radius=10)
        url_frame.pack(pady=10, padx=20, fill="x")
        
        # URL label and entry
        url_label = ctk.CTkLabel(
            url_frame, 
            text="Enter YouTube Video URL:",
            font=("Arial", 12)
        )
        url_label.pack(pady=(10, 5), anchor="w", padx=10)
        
        self.url_entry = ctk.CTkEntry(
            url_frame, 
            width=500,
            placeholder_text="Example: https://www.youtube.com/watch?v=...",
            font=("Arial", 12)
        )
        self.url_entry.pack(pady=5, padx=10, fill="x")
        
        # Download options frame
        options_frame = ctk.CTkFrame(self.master, corner_radius=10)
        options_frame.pack(pady=10, padx=20, fill="x")
        
        # Video quality label
        quality_label = ctk.CTkLabel(
            options_frame, 
            text="Video Quality:",
            font=("Arial", 12)
        )
        quality_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        # Video quality options
        self.quality_var = ctk.StringVar(value="720p")
        qualities = ["144p", "240p", "360p", "480p", "720p", "1080p"]
        quality_menu = ctk.CTkOptionMenu(
            options_frame,
            variable=self.quality_var,
            values=qualities
        )
        quality_menu.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        
        # Download format label
        format_label = ctk.CTkLabel(
            options_frame, 
            text="Download Format:",
            font=("Arial", 12)
        )
        format_label.grid(row=1, column=0, padx=10, pady=10, sticky="w")
        
        # Download format options
        self.format_var = ctk.StringVar(value="MP4")
        formats = ["MP4", "MP3"]
        format_menu = ctk.CTkOptionMenu(
            options_frame,
            variable=self.format_var,
            values=formats
        )
        format_menu.grid(row=1, column=1, padx=10, pady=10, sticky="ew")
        
        # Output location frame
        output_frame = ctk.CTkFrame(self.master, corner_radius=10)
        output_frame.pack(pady=10, padx=20, fill="x")
        
        # Output location label and button
        output_label = ctk.CTkLabel(
            output_frame, 
            text="Download Location:",
            font=("Arial", 12)
        )
        output_label.pack(pady=(10, 5), anchor="w", padx=10)
        
        self.output_entry = ctk.CTkEntry(
            output_frame,
            font=("Arial", 12)
        )
        self.output_entry.pack(pady=5, padx=10, fill="x", side="left", expand=True)
        
        browse_button = ctk.CTkButton(
            output_frame,
            text="Browse",
            command=self.browse_directory,
            width=80
        )
        browse_button.pack(pady=5, padx=10, side="right")
        
        # Progress bar
        self.progress = Progressbar(
            self.master,
            orient="horizontal",
            length=680,
            mode="determinate"
        )
        self.progress.pack(pady=20)
        
        # Download button
        download_button = ctk.CTkButton(
            self.master,
            text="Download Video",
            command=self.start_download_thread,
            height=40,
            font=("Arial", 14, "bold")
        )
        download_button.pack(pady=10, padx=20, fill="x")
        
        # Status label
        self.status_label = ctk.CTkLabel(
            self.master,
            text="",
            font=("Arial", 12)
        )
        self.status_label.pack(pady=10)
    
    def browse_directory(self):
        # Open directory dialog and set output path
        directory = filedialog.askdirectory()
        if directory:
            self.output_entry.delete(0, "end")
            self.output_entry.insert(0, directory)
    
    def start_download_thread(self):
        # Start download in a separate thread to prevent GUI freezing
        threading.Thread(target=self.download_video, daemon=True).start()
    
    def download_video(self):
        url = self.url_entry.get()
        output_path = self.output_entry.get()
        
        # Validate inputs
        if not url:
            messagebox.showerror("Error", "Please enter a YouTube URL")
            return
        
        if not output_path:
            messagebox.showerror("Error", "Please select an output directory")
            return
        
        try:
            # Create YouTube object
            yt = YouTube(
                url,
                on_progress_callback=self.progress_function,
                on_complete_callback=self.complete_function
            )
            
            # Update status
            self.status_label.configure(text=f"Downloading: {yt.title[:50]}...")
            
            # Determine download stream based on format
            if self.format_var.get() == "MP4":
                stream = yt.streams.filter(
                    progressive=True,
                    file_extension="mp4",
                    resolution=self.quality_var.get()
                ).first()
                
                if not stream:
                    stream = yt.streams.filter(
                        progressive=True,
                        file_extension="mp4"
                    ).order_by("resolution").desc().first()
            else:  # MP3
                stream = yt.streams.filter(
                    only_audio=True
                ).first()
            
            # Download the video/audio
            if stream:
                # Sanitize filename
                filename = re.sub(r'[\\/*?:"<>|]', "", yt.title)
                if self.format_var.get() == "MP3":
                    filename += ".mp3"
                else:
                    filename += ".mp4"
                
                # Start download
                stream.download(output_path=output_path, filename=filename)
            else:
                messagebox.showerror("Error", "No suitable stream found")
        
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            self.status_label.configure(text="Download failed")
    
    def progress_function(self, stream, chunk, bytes_remaining):
        # Update progress bar
        total_size = stream.filesize
        bytes_downloaded = total_size - bytes_remaining
        percentage = (bytes_downloaded / total_size) * 100
        self.progress["value"] = percentage
        self.master.update_idletasks()
    
    def complete_function(self, stream, file_path):
        # Show completion message
        self.status_label.configure(text="Download completed successfully!")
        messagebox.showinfo("Success", "Download completed successfully!")

# Create and run the application
if __name__ == "__main__":
    app = ctk.CTk()
    YouTubeDownloaderApp(app)
    app.mainloop()