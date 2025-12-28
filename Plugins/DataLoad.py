import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

from dotenv import load_dotenv
import os

import pandas as pd
import requests
import numpy as np

import tempfile
import librosa
import yt_dlp

from pathlib import Path
from Plugins.Utils import cut_brackets

load_dotenv("log_data.env")

class SpotipyPlugin:
    '''
    Plugin do wczytania z biblioteki spotipy
    '''
    def __init__(self):
        self.spotipy_key = os.getenv("SPOTIPY_KEY")
        self.spotipy_id = os.getenv("SPOTIPY_ID")

        self.auth_manager = SpotifyClientCredentials(client_id=self.spotipy_id, client_secret=self.spotipy_key)
        self.sp = spotipy.Spotify(auth_manager=self.auth_manager)

    def search_song(self, song_name, artist_name):
        q="track:"+str(song_name)+" artist:"+str(artist_name)
        results = self.sp.search(q=q, type='track', limit=1)
        if results['tracks']['items']:
            track = results['tracks']['items'][0]
            artist_id = track['artists'][0]['id']

            # Pobranie informacji o artyście, w tym gatunkach muzycznych
            artist_info = self.sp.artist(artist_id)

            return {
                'spotify_popularity': track['popularity'],
                'spotify_release_date': track['album']['release_date'],
                #'energy': features['energy']
            }
        else:
            print(f"brak rezultatów dla wyszukania: {song_name} - {artist_name}, szukam samej piosenki")
            q="track:"+str(song_name)
            results = self.sp.search(q=q, type='track', limit=1)
            if results['tracks']['items']:
                track = results['tracks']['items'][0]
                artist_id = track['artists'][0]['id']

                # Pobranie informacji o artyście, w tym gatunkach muzycznych
                artist_info = self.sp.artist(artist_id)

                return {
                    'spotify_popularity': track['popularity'],
                    'spotify_release_date': track['album']['release_date'],
                    #'energy': features['energy']
                }

            else:
                print("Nie znaleziono piosenki.")
                return {
                    'spotify_popularity': None,
                    'spotify_release_date': None
                }

    def update_dataframe_with_spotify_info(self, df, track_name_column, artist_name_column):
        if 'Spotify Popularity' not in df.columns:
            df['Spotify Popularity'] = None

        if 'Spotify Release Date' not in df.columns:    
            df['Spotify Release Date'] = None

        unique_tracks = df[track_name_column].size

        i = 1
        for _, row in df.iterrows():
            real_index = row.name
            print(f"Analiza Spotipy: {i}/{unique_tracks}")
            song_info = self.search_song(song_name=row[track_name_column], artist_name=row[artist_name_column] )
            df.at[real_index, 'Spotify Popularity'] = song_info['spotify_popularity']
            df.at[real_index, 'Spotify Release Date'] = song_info['spotify_release_date']
            i = i+1

        return df

    def update_release_year_age(self, df, wrapped_year):
        '''
        Updates data frame with release date and age of the track
        '''
        if 'Spotify Release Year' not in df.columns: 
            df['Spotify Release Year'] = None

        if 'Track Age' not in df.columns:    
            df['Track Age'] = None

        df['Spotify Release Year'] = (
            df['Spotify Release Date']
            .str[:4]
            .where(df['Spotify Release Date'].notna())
            .astype(int)
        )

        df['Track Age'] = df['Spotify Release Year'].apply(
            lambda x: wrapped_year - x if (wrapped_year > x) else 0
        )        

        return df
   

class LastFMPlugin:
    '''
    Klasa wyciągania danych z LastFM
    '''
    def __init__(self):
        self.last_fm_key = os.getenv("LAST_FM_KEY")
        self.last_fm_url = os.getenv("LAST_FM_URL")
        self.analyser_path = Path(os.getcwd()).resolve()

    def search_artist_tag(self, artist_name):
        '''
        Wyszukiwanie tagow z last fm api
        '''
        params = {
            'method': 'artist.getInfo',
            'artist': artist_name,
            'user': 'RJ',   # czemu tu jest RJ to nie wiem
            'api_key': self.last_fm_key,
            'format': 'json'
        }

        response = requests.get(self.last_fm_url, params=params)

        if response.status_code == 200:
            data = response.json()
            tags = data['artist']['tags']['tag']
            tag_list = [tag['name'] for tag in tags]
            #for tag in tags:
            #   print(f"Nazwa: {tag['name']}, URL: {tag['url']}")
        else:
            tag_list = []
            print(f"Błąd: {response.status_code}")

        return tag_list


    def update_dataframe_with_artist_tags(self, df, artist_column="Artist name"):
        '''
        Wyciągamy tagi:
        1. stwórz listę unikalnych wykonawców
        2. wyciągnij tagi z api
        3. left join do pierwotnego df
        '''

        unique_artist = df[artist_column].unique()
        df_unique = pd.DataFrame({artist_column:unique_artist})
        artists_count = unique_artist.size
        df_unique['Tags'] = None

        i = 1
        for _, row in df_unique.iterrows():
            real_index = row.name
            print(f"Analiza LastFM: {i}/{artists_count}")
            tag_list = self.search_artist_tag(row[artist_column])
            df_unique.at[real_index, 'Tags'] = tag_list
            i = i+1

        df = pd.merge(df, df_unique, on=artist_column, how="left")
        print("Data merged")

        return df
    
    def search_track_tag(self, artist_name, track_name):
        '''
        Wyszukiwanie tagow z last fm api
        '''
        params = {
            'method': 'track.getInfo',
            'artist' : artist_name,
            'track': track_name,
            #'user': 'RJ',   # czemu tu jest RJ to nie wiem
            'api_key': self.last_fm_key,
            'format': 'json'
        }

        response = requests.get(self.last_fm_url, params=params)

        if response.status_code == 200:
            try:
                data = response.json()
                tags = data['track']['toptags']['tag']
                tag_list = [tag['name'] for tag in tags]
            except:
                tag_list = []
                print(f"Błąd: {response.status_code}")                  

        else:
            tag_list = []
            print(f"Błąd: {response.status_code}")

        return tag_list

    def search_artist_tag(self, artist_name):
        '''
        Wyszukiwanie tagow z last fm api z artystow
        '''
        params = {
            'method': 'artist.getInfo',
            'artist' : artist_name,
            #'user': 'RJ',   # czemu tu jest RJ to nie wiem
            'api_key': self.last_fm_key,
            'format': 'json'
        }

        response = requests.get(self.last_fm_url, params=params)

        if response.status_code == 200:
            try:
                data = response.json()
                tags = data['artist']['tags']['tag']
                tag_list = [tag['name'] for tag in tags]
            except:
                tag_list = []
                print(f"Błąd: {response.status_code}")                  

        else:
            tag_list = []
            print(f"Błąd: {response.status_code}")

        return tag_list

    def update_dataframe_with_track_tags(self, df, artist_column='Artist name', track_column='Track name'):
        '''
        Wyciągamy tagi z piosenek
        '''
        track_count = df[track_column].size
        df['Tags'] = None

        i=1
        for _, row in df.iterrows():
            real_index = row.name
            print(f"Analiza LastFM: {i}/{track_count}")
            tag_list = self.search_track_tag(track_name= row[track_column] ,artist_name=row[artist_column])
            if len(tag_list) == 0:
                print("Brak tagów na ścieżce, szukam w artyście")
                tag_list = self.search_artist_tag(artist_name=row[artist_column])
            df.at[real_index, 'Tags'] = tag_list
            i = i+1

        return df

    def genres_from_tags(self, df):
        ''' 
        Wyciągamy gatunki z tagów
        '''
        full_path = self.analyser_path / "LocalDB" / "Genres.csv" 
        df_genres = pd.read_csv(full_path)
        if 'Genres' not in df.columns: 
            df["Genres"] = None
        df["Genres"] = df["Tags"].apply(lambda x: [element for element in x if element.lower() in map(str.lower, df_genres["Genres"].tolist())])

            # do przeniesienia do pluginu
        df["Genres"] = df["Genres"].apply(lambda x: str(x))
        df["Tags"] = df["Tags"].apply(lambda x: str(x))

        df["Genres"] = df["Genres"].apply(lambda x: cut_brackets(x))
        df["Tags"] = df["Tags"].apply(lambda x: cut_brackets(x))

        return df   

class YouTubeAnalyzerPlugin:
    def __init__(self):
        pass

    def enrich(self, query):
        title = query.get("title")
        artist = query.get("artist")
        if not title or not artist:
            return {"youtube_audio": []}

        search_query = f"ytsearch1:{artist} - {title}"
        results = []

        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                output_path = os.path.join(tmpdir, "audio.wav")
                print(f"[YouTubeAudio] Searching and downloading: {search_query}")

                ydl_opts = {
                    'format': 'bestaudio/best',
                    'outtmpl': os.path.join(tmpdir, 'audio.%(ext)s'),
                    'proxy': None,
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'wav',
                        'preferredquality': '192',
                    }],
                    'cookies' : 'cookies.txt',
                    'quiet': True,
                    'default_search': 'ytsearch',
                    'noplaylist': True,
                    'extract_flat': False,
                    'skip_download': False,
                }

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info_dict = ydl.extract_info(search_query, download=True)
                    video_title = info_dict['title']
                    video_url = f"https://www.youtube.com/watch?v={info_dict['id']}"

                print(f"[YouTubeAudio] Downloaded: {video_title} ({video_url})")

                y, sr = librosa.load(output_path, sr=None)
                print(f"[YouTubeAudio] Loaded audio: {len(y)} samples @ {sr} Hz")

                # --- ANALIZA ---
                try:
                    bpm = float(round(librosa.feature.tempo(y=y, sr=sr)[0]))
                except Exception as e:
                    print(f"[YouTubeAudio] bpm error: {e}")
                    bpm = None

                try:
                    energy = float(np.mean(librosa.feature.rms(y=y)))
                except Exception as e:
                    print(f"[YouTubeAudio] energy error: {e}")
                    energy = None

                try:
                    danceability = float(np.mean(librosa.onset.onset_strength(y=y, sr=sr)))
                except Exception as e:
                    print(f"[YouTubeAudio] danceability error: {e}")
                    danceability = None

                try:
                    spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)
                    spectral_centroid_mean = float(np.mean(spectral_centroid))
                except Exception as e:
                    print(f"[YouTubeAudio] spectral centroid error: {e}")
                    spectral_centroid_mean = None

                try:
                    mood = self._estimate_mood(bpm, energy, danceability, spectral_centroid_mean)
                except Exception as e:
                    print(f"[YouTubeAudio] mood estimation error: {e}")
                    mood = "unknown"

                results.append({
                    "title": video_title,
                    "youtube_url": video_url,
                    "bpm": round(bpm) if bpm is not None else None,
                    "energy": round(energy, 4) if energy is not None else None,
                    "danceability": round(danceability, 4) if danceability is not None else None,
                    "mood": mood
                })

        except Exception as e:
            print(f"[YouTubeAudio] FATAL ERROR: {e}")
            results.append({"error": str(e)})

        return {"youtube_audio": results}

    def _estimate_mood(self, bpm, energy, danceability, brightness):
        if None in (bpm, energy, danceability, brightness):
            return "unknown"
        if bpm > 120 and energy > 0.05 and danceability > 0.05:
            return "energetic"
        elif brightness < 2000 and danceability < 0.03:
            return "melancholic"
        elif brightness > 3000:
            return "bright"
        else:
            return "neutral"
        
    def update_dataframe(self, df, track_name_column, artist_column):
        '''
        Update with estimated values 
        '''
        if 'bpm' not in df.columns:
            df['bpm'] = None

        if 'energy' not in df.columns:    
            df['energy'] = None

        if 'danceability' not in df.columns:    
            df['danceability'] = None

        if 'mood' not in df.columns:    
            df['mood'] = None
        unique_tracks = df[track_name_column].size

        i = 1
        for _, row in df.iterrows():
            real_index = row.name
            print(f"Progress: {i}/{unique_tracks}")
            query = {
                "title": row[track_name_column],
                "artist": row[artist_column],
                "limit": 1
            }    
            song_analyse = self.enrich(query=query)
            print(song_analyse)
            if 'error' not in song_analyse["youtube_audio"][0].keys():
                song_info = song_analyse['youtube_audio'][0]
                df.at[real_index, 'bpm'] = song_info['bpm']
                df.at[real_index, 'energy'] = song_info['energy']
                df.at[real_index, 'danceability'] = song_info['danceability']
                df.at[real_index, 'mood'] = song_info['mood']

            i = i+1

        return df
    
class ImportFromLocalPlugin:
    '''
    Importujemy dane z lokalnego pliku csv do którego uprzednio zapisaliśmy wyniki z różnych api
    '''
    def __init__(self):
        pass

    def create_track_artist_column(self, df):
        '''
        łączy kolumnę track i artist w jedną
        '''
        df.loc[:,"Track Artist"] = df.loc[:,"Track name"] +" "+ df.loc[:,"Artist name"]
        return df

    def import_from_local_csv(self, df_wrapped, df_local):
        df_local = self.create_track_artist_column(df_local)
        df_wrapped = self.create_track_artist_column(df_wrapped)

        df_local = df_local.drop(columns=["Track name","Artist name","Album"])
        df_from_local = pd.merge(df_wrapped, df_local, how="left", on="Track Artist")
        df_from_local = df_from_local.drop(columns=["Track Artist"])

        return df_from_local
