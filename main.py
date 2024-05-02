import configparser
import youtube_dl


# Import the configparser module

# Create a new instance of the ConfigParser class
config = configparser.ConfigParser()

if not config.read('config.ini'):
    # Add sections and options to the config file
    config['General'] = {
        'playlist link': 'https://'
    }

    # Write the config file to disk
    with open('config.ini', 'w') as configfile:
        config.write(configfile)



# Define the YouTube playlist URL
playlist_url = ""

# Create a YouTubeDL object
ydl = youtube_dl.YoutubeDL({})

# Extract the playlist information
with ydl:
    playlist_info = ydl.extract_info(playlist_url, download=False)

# Iterate over each video in the playlist
for video in playlist_info["entries"]:
    # Extract the song name and link
    song_name = video["title"]
    song_link = video["webpage_url"]
    
    # Print the song name and link
    print(f"Song Name: {song_name}")
    print(f"Song Link: {song_link}")
    print()