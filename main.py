import configparser
# import youtube_dl
import yt_dlp
import youtube_dl
import os
import logging
# import playsound

#TODO: winget install "FFmpeg (Essentials Build)"

logging.basicConfig(format='[%(asctime)s][%(levelname)s] - %(message)s', level=logging.INFO)

# Create a new instance of the ConfigParser class
config = configparser.ConfigParser()

if not config.read('config.ini'):
    # Add sections and options to the config file
    config['General'] = {
        'playlist link': 'https://',
        'output folder': '.',
        'refresh rate': '3600',
        'download': 'True'
    }

    # Write the config file to disk
    with open('config.ini', 'w') as configfile:
        config.write(configfile)


# Define the YouTube playlist URL
playlist_url = config['General']['playlist link']
# Create a YouTubeDL object
ydl_opts = {
    'outtmpl': config['General']['output folder'] + '/%(title)s.%(ext)s',
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
}

ydl = yt_dlp.YoutubeDL(ydl_opts)
ydl_search = youtube_dl.YoutubeDL()


retries = 0
def get_music(download="Config"):
    with ydl:
        playlist_info = ydl_search.extract_info(playlist_url, download=False)

    if ((download == "Config") and (config['General']['download'] == 'True')) or download == 'True':
        for video in playlist_info["entries"]:
            song_name = video["title"]
            song_path = config['General']['output folder'] + '/' + song_name + '.mp3'
            if not os.path.exists(song_path):
                logging.info(f"Downloading {song_name}...")
                ydl.download([video["webpage_url"]])
                logging.info(f"Downloaded {song_name} successfully.")
            else:
                logging.info(f"{song_name} already exists. Skipping download.")

    return playlist_info
      
def get_order(playlist_data=None):
    if playlist_data is None:
        playlist_data = get_music(download=False)
    order = []
    for video in playlist_data["entries"]:
        order.append(video["title"])
    return order

def delete_missing(playlist_data):
    files = os.listdir(config['General']['output folder'])
    songs = []
    for video in playlist_data["entries"]:
        song_name = video["title"]
        song_path = config['General']['output folder'] + '/' + song_name + '.mp3'
        songs.append(song_path)

    for file in files:
        file_path = config['General']['output folder'] + '/' + file
        if file_path not in songs:
            logging.info(f"Removing {file_path}")
            os.remove(file_path)
        

def init():
    
    playlist = get_music()
    playlist_order = get_order(playlist_data=playlist)
    if playlist is not None:
        logging.info("="*80)
        logging.info("Playlist downloaded successfully.")
        logging.info(f"Playlist Title: {playlist['title']}")
        logging.info(f"Number of Videos: {len(playlist['entries'])}")
        logging.info("="*80)
    else:
        logging.error("Failed to download the playlist.")

    # convert_mp4_to_mp3(playlist)
    delete_missing(playlist)

    logging.info(f"Done Initializing/Updating Playlist")
    logging.info("="*80)

    return playlist, playlist_order

playlist, playlist_order = init()

# Iterate over each video in the playlist
for video in playlist["entries"]:
    # Extract the song name and link
    song_name = video["title"]
    song_link = video["webpage_url"]
    
    # logging.info(f"Song Name: {song_name}")
    # logging.info(f"Song Path: {song_path}")
    # logging.info()

    # Play the audio of the MP4



# # Iterate over each video in the playlist
# for video in playlist["entries"]:
#     # Extract the song name and link
#     song_name = video["title"]
#     song_link = video["webpage_url"]
    
#     # logging.info(f"Song Name: {song_name}")
#     # logging.info(f"Song Link: {song_link}")
#     # logging.info()
