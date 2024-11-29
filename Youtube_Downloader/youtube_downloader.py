import customtkinter as ctk
from pytubefix import YouTube
from threading import Thread
import os
from tkinter import filedialog, messagebox

# Function to handle the video download process
def download_video():
	# Get the selected resolution
	resolution = resolution_var.get()
	if not resolution:
		messagebox.showerror("Error", "Please select a resolution.")
		return
	
	# Ask user to choose download directory
	save_directory = filedialog.askdirectory()
	if not save_directory:
		messagebox.showerror("Error", "Please select a directory to save the video.")
		return none

	# Create YouTube object and get the selected stream
	yt = YouTube(url_entry.get())
	selected_stream = next((s for s in streams if f"{s.resolution} - {s.filesize / 1024 / 1024:.2f} MB" == resolution), None)
	
	if not selected_stream:
		messagebox.showerror("Error", "Selected stream not found.")
		return

	# Prepare file path for download
	file_path = os.path.join(save_directory, f"{yt.title}.mp4")

	try:
		# Download the video
		selected_stream.download(output_path=save_directory, filename=f"{yt.title}.mp4")
		messagebox.showinfo("Success", "Download completed!")
	except Exception as e:
		messagebox.showerror("Error", f"Failed to download video: {e}")

# Function to fetch available video streams
def fetch_streams():
	global streams
	try:
		# Create YouTube object and get available streams
		yt = YouTube(url_entry.get())
		streams = yt.streams.filter(file_extension='mp4', progressive=True)

		# Update the option menu with available resolutions
		resolutions = [f"{stream.resolution} - {stream.filesize / 1024 / 1024:.2f} MB" for stream in streams]
		resolution_menu.configure(values=resolutions)
		if resolutions:
			resolution_var.set(resolutions[0])

		# Update video title label
		label_title.configure(text=f"Video Title: {yt.title}")
	except Exception as e:
		messagebox.showerror("Error", f"Failed to fetch streams: {e}")

# Function to start fetching streams in a separate thread
def fetch_streams_thread():
	Thread(target=fetch_streams).start()

# Function to start download in a separate thread
def download_thread():
	Thread(target=download_video).start()

# GUI Setup
ctk.set_appearance_mode("dark")  # Set dark mode
ctk.set_default_color_theme("blue")  # Set color theme

# Create main window
root = ctk.CTk()
root.title("YouTube Downloader")
root.geometry("500x400")  # Set initial window size

# Create and place URL entry field
url_entry = ctk.CTkEntry(root, width=400, placeholder_text="Enter YouTube Video URL")
url_entry.pack(pady=10)

# Create and place "Fetch Video Info" button
fetch_button = ctk.CTkButton(root, text="Fetch Video Info", command=fetch_streams_thread)
fetch_button.pack(pady=10)

# Create and place video title label
label_title = ctk.CTkLabel(root, text="Video Title: ")
label_title.pack(pady=10)

# Create and place resolution selection menu
resolution_var = ctk.StringVar()
resolution_menu = ctk.CTkOptionMenu(root, variable=resolution_var, values=["Select Resolution"])
resolution_menu.pack(pady=10)

# Create and place download button
download_button = ctk.CTkButton(root, text="Download", command=download_thread)
download_button.pack(pady=10)

# Start the GUI event loop
root.mainloop()