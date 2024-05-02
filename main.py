import configparser
# import youtube_dl
import yt_dlp as youtube_dl
import os
import logging
# import playsound

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
ydl = youtube_dl.YoutubeDL(ydl_opts)


retries = 0
def get_music(retries=None, download="Config"):
    if retries is None:
        retries = 0
    try:
        # Extract the playlist information
        with ydl:
            if download == "Config":
                playlist_info = ydl.extract_info(playlist_url, download=(config['General']['download'] == 'True'))
            else:
                playlist_info = ydl.extract_info(playlist_url, download=download)

        return playlist_info
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        retries += 1
        if retries < 5:
            get_music(retries)
        else:
            logging.error("Failed to download the playlist.")
            return None
        
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
            print(f"Removing {file_path}")
            # os.remove(file_path)
        


def convert_mp4_to_mp3(playlist_data):
    for video in playlist_data["entries"]:
        song_name = video["title"]
        song_path = config['General']['output folder'] + '/' + song_name + '.mp3'

        # logging.info(f"Converting {song_name} to MP3...")
        # logging.info(f"Song Path: {song_path}")
        # logging.info()

        # Check if FFmpeg is installed
        if not os.path.exists('ffmpeg'):
            logging.error("FFmpeg is not installed. Please install FFmpeg to convert MP4 to MP3.")
        else:
            # Convert MP4 to MP3 using FFmpeg
            mp3_path = config['General']['output folder'] + '/' + song_name + '.mp3'
            os.system(f'ffmpeg -i {song_path} {mp3_path}')
            logging.info(f"Converted {song_name} to MP3 successfully.")

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
