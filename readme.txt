Wymagania: 
1. Instalacja bibliotek z pliku requirements - pierwszy kod z pliku data_conversion
2. Pracowałem na pythonie 3.11
3. Trzeba stworzyć konta deveoperskie na https://developer.spotify.com/ oraz https://www.last.fm/api
Tam do wyciągnięcia mamy klucze - trzeba stworzyć w folderze projektu plik log_data.env o treści:

SPOTIPY_ID = <TWÓJ KLUCZ>
SPOTIPY_KEY = <TWÓJ KLUCZ>
LAST_FM_KEY = <TWÓJ KLUCZ>
LAST_FM_URL = 'http://ws.audioscrobbler.com/2.0/'
OPENAI_API_KEY = <TWÓJ KLUCZ>Aaaaaaa                       

5. Pobierz:
https://github.com/BtbN/FFmpeg-Builds/releases
np.: https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl-shared.zip
rozpakuj do wybranego folderu (ja dałem do C:\Users\marci\AppData\Local\mpeg) i dodaj ścieżkę do PATH systemowego

6. zaktualizuj "cookies.txt'
Pobierz rozszerzenie chrome do pobeirania plikow cookies
pobierz je i dodaj do projektu

7. venv
Python -m venv env
py -3.11 -m venv env 
pip install -r requirements.txt // instaluje

env\Scripts\activate
shiny run --reload app.py