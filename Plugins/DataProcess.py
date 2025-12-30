#Import libraries
import os
import pandas as pd
import re
from datetime import datetime

#Import plugins
from Plugins.DataLoad import SpotipyPlugin
from Plugins.DataLoad import LastFMPlugin
from Plugins.DataLoad import YouTubeAnalyzerPlugin
from Plugins.DataLoad import ImportFromLocalPlugin
from Plugins.DataSummary import WrappedSummaryPlugin

from pathlib import Path

analyser_path = Path(os.getcwd()).resolve()

class WrappedDataPrepare:
    '''
    Wczytanie i przygotowanie pliku z wrapped spotify
    '''
    def __init__(self):
        pass

    def file_load(self, file_path):
        if os.path.exists(file_path):
            print(f"Odczytano plik: {file_path}")
            df = pd.read_csv(file_path)
        else:
            print("Plik nie istnieje w podanej lokalizacji.")

        return df
    
    def year_from_name(self, file_name):
        match = re.search(r'\d+', file_name)  # Szuka ciągu cyfr w stringu
        wrapped_year = int(match.group())  # Konwertuje znalezioną cyfrę na int
        if match:
            return wrapped_year
        return None

    def prepare_columns(self, df):
        if "Artist Name(s)" in df.columns:
            df = df.rename(columns={"Artist Name(s)":"Artist name"})
            df["Artist name"] = df["Artist name"].apply(lambda x: x.split(",")[0])

        if "Track Name" in df.columns:
            df = df.rename(columns={"Track Name":"Track name"})

        if "Album Name" in df.columns:
            df = df.rename(columns={"Album Name":"Album"})    

        df = df[["Track name","Artist name","Album"]] #ogranicznie ilości kolumn

        return df

    def wykres_dekady(self, df_wrapped, analyser_path):
        df = self.prepare_columns(df_wrapped)
        local_path = os.path.join(analyser_path, "LocalDB", "LocalValues.csv")
        df_local = pd.read_csv(local_path, index_col="Unnamed: 0")

        import_local = ImportFromLocalPlugin()
        df = import_local.import_from_local_csv(df_wrapped, df_local)

        df = df.dropna(subset=['Spotify Release Year'])
        df['Decade'] = (df['Spotify Release Year'] // 10 * 10).astype(int).astype(str) + "s"
        # reszta kodu funkcji pozostaje bez zmian


class WrappedListProcess:
    '''
    Wczytuje dane, obrabia plik, tworzy wyniki i  aktualizuje loklaną bazę lub csv
    '''
    def __init__(self):
        pass

    def open_prepare(self, data_path, input_path, file_name):
        '''
        Wczytanie pliku i przygotowanie kolumn
        '''
        prepare_file = WrappedDataPrepare()
        print(f"Obróbka pliku: {input_path}\{file_name} ")

        df_wrapped = prepare_file.file_load(data_path/input_path/file_name)
        df_wrapped = prepare_file.prepare_columns(df_wrapped)
        wrapped_year = prepare_file.year_from_name(file_name)

        return df_wrapped, wrapped_year
    
    def local_api_divide(self, df, data_path, local_path):
        '''
        podział na dwie ramki danych
        '''
        import_local = ImportFromLocalPlugin()
        try:
            df_local = pd.read_csv(data_path/local_path, index_col="Unnamed: 0")
        except:
            df_local = pd.read_csv(data_path/local_path)
        df_wrapped = import_local.import_from_local_csv(df, df_local)
        
        df_from_local = df_wrapped[~df_wrapped["Update_date"].isna()].copy()
        df_from_api = df_wrapped[df_wrapped["Update_date"].isna()].copy()

        return df_local, df_from_local, df_from_api
        
    def load_data(self, wrapped_year, df_from_api):
        '''
        Przejście po kolei przez wszystkie api i pobranie muzyki
        '''
        spotipy_search = SpotipyPlugin()
        df_spotify = spotipy_search.update_dataframe_with_spotify_info(df=df_from_api, track_name_column='Track name', artist_name_column='Artist name')
        df_spotify = spotipy_search.update_release_year_age(df_spotify, wrapped_year)

        last_fm_search = LastFMPlugin()
        df_lastfm = last_fm_search.update_dataframe_with_track_tags(df=df_spotify,track_column= 'Track name', artist_column= 'Artist name')
        df_lastfm = last_fm_search.genres_from_tags(df_lastfm)

        youtube_search = YouTubeAnalyzerPlugin()
        df_youtube = youtube_search.update_dataframe(df_lastfm, 'Track name', 'Artist name')

        date_now = datetime.now().strftime("%Y/%m/%d")
        df_youtube["Update_date"] = date_now

        df_from_api = df_youtube
        return df_youtube

    def combine_and_save(self, df_from_api, df_from_local, df_local, data_path, output_path, local_path, file_name):
        '''
        Łączy dwie ramki danych i zapisuje pliki
        '''
        df_combined = pd.concat([df_from_local,df_from_api]).sort_index()

        SpotifySummary = WrappedSummaryPlugin()
        df_results = SpotifySummary.full_analysis(df_combined)

        #Wykomentowujemy zapis plikow, w obecnej wersji nie jest potrzebne
        # wrapped_name = file_name.split(".")[0]
        
        # print(f"Zapis plików: {data_path}/{output_path}/{wrapped_name}.csv oraz {wrapped_name}result.csv oraz")
        # df_combined.to_csv(data_path/ output_path/ (wrapped_name + ".csv"), index= False)
        # df_results.to_csv(data_path/ output_path/ (wrapped_name+"result.csv"), index= False)

        #aktualizacja lokalnego csv

        if not df_from_api.empty:
            print("Aktualizacja lokalnej bazy danych")
            df_local = pd.concat([df_local,df_from_api], ignore_index=True)
            df_local.to_csv(data_path/ local_path, index= False)
        else:
            print("Lokalna baza aktualna")

        return df_combined, df_results
    
   
    def process_list(self, file_name, data_path, local_path = "LocalDB/LocalValues.csv", output_path = "DataOutput", input_path = "NewData"):
        '''
        Wykonuje pełny proces obróbki
        '''
        df_wrapped, wrapped_year = self.open_prepare(data_path, input_path, file_name)
        df_local, df_from_local, df_from_api = self.local_api_divide(df_wrapped, data_path, local_path)
        df_from_api = self.load_data(wrapped_year, df_from_api)
        df_combined, df_results = self.combine_and_save(df_from_api, df_from_local, df_local, data_path, output_path, local_path, file_name)

        return df_combined, df_results
    
    #wczytanie df'a
def load_user_file(path, filename):

    wrapped_list = WrappedListProcess()
    full_name = f"{filename}.csv"
    print(f"Odczytuję plik: {path}\{full_name}")
    return wrapped_list.process_list(
        file_name=full_name,
        data_path=analyser_path,
        input_path=path
        )