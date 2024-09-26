import json
from pprint import pprint
import requests
import tqdm

har_file = r"loveworldworship.com.har"
save_path = r"downloads"

class Song:
    def __init__(self, url, name, log_data=None):
        self.url = url
        self.name = name
        self.log_data = log_data

        self.name = self.name.replace('+', ' ')
        self.url = requests.utils.unquote(self.url)

    def download(self, save_path=save_path):
        response = requests.get(self.url)
        if response.status_code == 200:
            file_path = f"{save_path}/{self.name}.mp3"
            with open(file_path, "wb") as f:
                total_size = int(response.headers.get('content-length', 0))
                block_size = 1024
                progress_bar = tqdm.tqdm(total=total_size, unit='B', unit_scale=True)
                for data in response.iter_content(block_size):
                    progress_bar.update(len(data))
                    f.write(data)
                progress_bar.close()
                # print(f"Downloaded {self.name}.mp3")
        else:
            print(f"Failed to download {self.name}.mp3")

    def __repr__(self):
        return f"{self.name}"

class ReadSongs:
    def __init__(self, har_file):
        self.har_file = har_file
        self.songs = []

        with open(self.har_file, 'r') as f:
            self.har = json.load(f)

        for entry in self.har['log']['entries']:
            
            if 'endpoints/add-queue' in entry['request']['url']:
                # print(entry)
                # pprint(entry)

                for param in entry['request']['postData']['params']:
                    if param['name'] == 'qdata%5Bname%5D':
                        song_name = param['value']
                    if param['name'] == 'qdata%5Burl%5D':
                        song_url = param['value']
                song = Song(song_url, song_name, entry)
                self.songs.append(song)

    def download_songs(self):
        for song in self.songs:
            print(f"Downloading {song.name}")
            song.download(save_path=save_path)

if __name__ == '__main__':
    read_songs = ReadSongs(har_file)

    print(f"{'='*20} Downloading the following {'='*20}")
    for i, song in enumerate(read_songs.songs):
        print(f"{i+1}. {song.name}")
    print(f"{'='*68}")
    # print(read_songs.songs)

    read_songs.download_songs()

    # print(read_songs.har)