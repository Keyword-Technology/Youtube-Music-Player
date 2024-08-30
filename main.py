import configparser
# import youtube_dl
import yt_dlp
import youtube_dl
import os
import logging
import vlc
import asyncio
import threading
import time

import tkinter as tk
from tkinter import Tk, Text, Listbox, StringVar, Menu, Toplevel
from tkinter.font import Font
from tkinter import WORD, END, BOTH, N, W, E, S, NW, NE, SW, SE, TOP, BOTTOM, LEFT, RIGHT
from tkinter import ttk
from tkinter import messagebox
import tkinter.filedialog as tkfile
from ttkbootstrap import Style


#TODO: winget install "FFmpeg (Essentials Build)"

logging.basicConfig(format='[%(asctime)s][%(levelname)s] - %(message)s', level=logging.INFO)


class music_manager:

    def __init__(self):
        self.playlist = None
        self.playlist_order = None

        # Create a new instance of the ConfigParser class
        self.config = configparser.ConfigParser()

        if not self.config.read('config.ini'):
            # Add sections and options to the config file
            self.config['General'] = {
                'playlist link': 'https://',
                'output folder': '.',
                'refresh rate': '3600',
                'download': 'True'
            }

            # Write the config file to disk
            with open('config.ini', 'w') as configfile:
                self.config.write(configfile)

        # Define the YouTube playlist URL
        self.playlist_url = self.config['General']['playlist link']
        # Create a YouTubeDL object
        ydl_opts = {
            'outtmpl': self.config['General']['output folder'] + '/%(title)s.%(ext)s',
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }

        self.ydl = yt_dlp.YoutubeDL(ydl_opts)
        self.ydl_search = youtube_dl.YoutubeDL()


    def get_music(self, download="Config"):
        with self.ydl_search:
            playlist_info = self.ydl_search.extract_info(self.playlist_url, download=False)

        try:
            if ((download == "Config") and (self.config['General']['download'] == 'True')) or download == 'True':
                for video in playlist_info["entries"]:
                    song_name = video["title"]
                    song_path = self.config['General']['output folder'] + '/' + song_name + '.mp3'
                    if not os.path.exists(song_path):
                        logging.info(f"Downloading {song_name}...")
                        self.ydl.download([video["webpage_url"]])
                        logging.info(f"Downloaded {song_name} successfully.")
                    else:
                        logging.info(f"{song_name} already exists. Skipping download.")

                    with open('playlist.txt', 'w') as f:
                        for song in self.playlist_order:
                            f.write(song + '\n')

            return playlist_info
        except Exception as e:
            logging.error(f"Error downloading music: {e}")
            return None
      
    def get_order(self, playlist_data=None):
        if playlist_data is None:
            playlist_data = self.get_music(download=False)
        order = []
        for video in playlist_data["entries"]:
            order.append(video["title"])
        return order

    def delete_missing(self, playlist_data):
        files = os.listdir(self.config['General']['output folder'])
        songs = []
        for video in playlist_data["entries"]:
            song_name = video["title"]
            song_path = self.config['General']['output folder'] + '/' + song_name + '.mp3'
            songs.append(song_path)

        for file in files:
            file_path = self.config['General']['output folder'] + '/' + file
            if file_path not in songs:
                logging.info(f"Removing {file_path}")
                try:
                    os.remove(file_path)
                except Exception as e:
                    logging.error(f"Error removing {file_path}: {e}")
        
    def update_background(self):
        self.playlist = self.get_music()
        self.playlist_order = self.get_order(playlist_data=self.playlist)
        with open('playlist.txt', 'w') as f:
            for song in self.playlist_order:
                f.write(song + '\n')
        self.delete_missing(self.playlist)

    def update(self):
        if not os.path.exists('playlist.txt'):
            self.update_background()
        else:
            with open('playlist.txt', 'r') as f:
                songs = f.readlines()
                songs = [song.strip() for song in songs]

            self.playlist_order = songs

            threading.Thread(target=self.update_background).start()
        
        return self.playlist_order
    
    def player_manager(self):
        self.update()
        # Create a VLC media player instance
        self.player = vlc.MediaPlayer()

        # Create a media list player instance
        self.list_player = vlc.MediaListPlayer()

        # Create a media list instance
        self.media_list = vlc.MediaList()

        # Add the MP3 files to the media list
        for song_name in self.playlist_order:
            song_path = self.config['General']['output folder'] + '/' + song_name + '.mp3'
            media = vlc.Media(song_path)
            self.media_list.add_media(media)

        # Set the media list to the media list player
        self.list_player.set_media_list(self.media_list)

        # Set the player mode to loop
        self.list_player.set_playback_mode(vlc.PlaybackMode.loop)

        # Set the media list player to the player instance
        self.list_player.set_media_player(self.player)

        # Start playing the media list
        self.list_player.play()

    def refresh_playlist(self):
        self.player.stop()
        try:
            self.playlist_order = self.update_background()
        except Exception as e:
            logging.error(f"Error updating playlist: {e}")
        self.player_manager()
        return self.playlist, self.playlist_order
    
    def stop(self):
        self.player.stop()
    
    def pause(self):
        self.player.pause()

    def resume(self):
        self.player.play()

    def next(self):
        self.player.next()

    def previous(self):
        self.player.previous()

    def set_volume(self, volume):
        self.player.audio_set_volume(volume)

    def get_volume(self):
        return self.player.audio_get_volume()
    
    def get_time(self):
        return self.player.get_time()
    
    def set_time(self, time):
        self.player.set_time(time)
    
    def get_length(self):
        return self.player.get_length()
    
    def get_playlist(self):
        return self.playlist_order

    def get_current_song(self):
        return self.playlist_order[self.player.audio_get_track()]
    

class MusicApp(tk.Tk):
    def __init__(self, loop, interval=1 / 60, theme="darkly"):
        super().__init__()
        self.loop = loop
        self.protocol("WM_DELETE_WINDOW", self.close)
        self.update_idletasks()
        self.title("Mimosa Music Player")
        self.geometry("800x600")
        self.theme = theme

        # style = Style(theme='darkly')
        self.style = Style(theme=self.theme)

        self.tasks = []


        self.music = music_manager()
        self.music.player_manager()

        self.main()

        self.tasks.append(loop.create_task(self.updater(interval)))
        self.tasks.append(loop.create_task(self.update_per_minute()))
        # self.tasks.append(loop.create_task(self.music_updater(interval)))
        # self.after(10, self.animate)

    def set_volume(self, volume):
        self.music.set_volume(int(float(volume)))

    def main(self):
        print(f"DISPLAYING {'='*80}")
        # Create a label to display the currently playing song
        self.current_song_label = ttk.Label(self, text="Currently Playing: ")
        self.current_song_label.place(x=0, y=0)

        # Create a label to display the current volume
        self.volume_label = ttk.Label(self, text="Volume: ")
        self.volume_label.place(x=0, y=60)

        # Create a scale widget to control the volume
        self.volume_scale = ttk.Scale(self, from_=0, to=100, orient="horizontal", command=self.set_volume)
        self.volume_scale.set(self.music.get_volume())
        self.volume_scale.place(x=100, y=60)

        # Create a progress bar to display the current song progress
        self.progress_bar = ttk.Progressbar(self, orient="horizontal", length=450, mode="determinate")
        self.progress_bar.place(x=0, y=25)

        self.progress_bar_label = ttk.Label(self, text="Progress: ")
        self.progress_bar_label.place(x=0, y=40)

        # Update the progress bar value based on the current song progress
        def update_progress():
            try:
                current_time = self.music.get_time() / 1000
                song_length = self.music.get_length() / 1000

                progress = (current_time / song_length) * 100
                self.progress_bar["value"] = progress

                song_minutes = int(current_time // 60)
                song_seconds = int(current_time % 60)
                duration_minutes = int(song_length // 60)
                duration_seconds = int(song_length % 60)

                progress_text = f"{song_minutes}:{song_seconds:02d} / {duration_minutes}:{duration_seconds:02d} seconds"
                self.progress_bar_label.config(text=f"Progress: {progress_text}")
            except Exception as e:
                logging.error(f"Error updating progress bar: {e}")
            self.after(100, update_progress)

        # Start updating the progress bar
        update_progress()

    
        # # Create a button to play the next song
        # self.next_button = ttk.Button(self, text="Next", command=self.music.next)
        # self.next_button.place(x=2, y=1)

        # # Create a button to play the previous song
        # self.previous_button = ttk.Button(self, text="Previous", command=self.music.previous)
        # self.previous_button.place(x=3, y=1)

        # Create a button to pause the music
        self.pause_button = ttk.Button(self, text="Pause", command=self.music.pause, style="TButton.Success")
        self.pause_button.place(x=0, y=85)

        # Create a button to resume the music
        self.resume_button = ttk.Button(self, text="Resume", command=self.music.resume, style="TButton.Success")
        self.resume_button.place(x=100, y=85)

        def run_refresh():
            self.loop.create_task(self.refresh_music())

        self.force_refresh_button = ttk.Button(self, text="Force Refresh. This will stop the music", command=run_refresh, style="TButton.Warning")
        self.force_refresh_button.place(x=0, y=125)

        # Create a listbox to display the songs in the queue
        self.queue_listbox = Listbox(self, selectbackground=self.style.colors.primary, selectforeground=self.style.colors.light, font=Font(family="Arial", size=12))
        self.queue_listbox.place(x=0, y=150, width=400, height=400)

        # Get the playlist from the music manager
        playlist = self.music.get_playlist()

        # Add the songs to the listbox
        for song in playlist:
            self.queue_listbox.insert(END, song)


    
    # async def updater(self):
    #     while True:
    #         print(f"Currently Playing: {self.music.current_song()}")
    #         # self.current_song_label.config(text=f"Currently Playing: {self.music.current_song()}")

    #         await asyncio.sleep(0.1)

    async def updater(self, interval):
        while True:
            self.update()
            self.animate()
            # plt.show()
            # plt.show(block = False)
            await asyncio.sleep(interval)

    async def music_updater(self, interval):
        while True:
            
            
            await asyncio.sleep(interval)

    async def refresh_music(self):
        self.music.refresh_playlist()
        self.queue_listbox.delete(0, END)
        for song in self.music.get_playlist():
            self.queue_listbox.insert(END, song)

    async def update_per_minute(self):
        while True:
            self.queue_listbox.delete(0, END)
            # Add the songs to the listbox
            for song in self.music.get_playlist():
                self.queue_listbox.insert(END, song)
            await asyncio.sleep(60)
            # self.music.refresh_playlist()

    def animate(self):
        current_song = self.music.get_current_song()
        self.current_song_label.config(text=f"Currently Playing: {current_song}")
        self.volume_label.config(text=f"Volume: {self.music.get_volume()}%")

        # Get the index of the current song in the playlist
        current_song_index = self.music.get_playlist().index(current_song)
        # Set the background color of the current song in the listbox to red
        self.queue_listbox.itemconfig(current_song_index, bg="red")


    def close(self):
        for task in self.tasks:
            task.cancel()
        self.loop.stop()
        self.destroy()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    app = MusicApp(loop)
    loop.run_forever()
    loop.close()

# if __name__ == '__main__':
#     music = music_manager()
#     music.player_manager()
#     print(music.get_volume())
    
#     while True:
#         print("\n"*20)
#         print("="*80)
#         print(music.get_time()/1000)
#         print(music.get_length()/1000)
#         print("="*80)
#         time.sleep(1)



