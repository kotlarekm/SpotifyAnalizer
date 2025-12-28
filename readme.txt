Wymagania: 
1. Instalacja bibliotek z pliku requirements - pierwszy kod z pliku data_conversion
2. Pracowałem na pythonie 3.11 - nie potrafiłem zainstalować dotenv na 3.13 - choć powinien niby działać
3. Trzeba stworzyć konta deveoperskie na https://developer.spotify.com/ oraz https://www.last.fm/api
Tam do wyciągnięcia mamy klucze - trzeba stworzyć w folderze projektu plik log_data.env o treści:

ANALYSER_PATH = <WASZA ŚCIEŻKA PROJEKTU> - np. D:\AnalizaDanych\0_SpotifyAnalyser
SPOTIPY_ID = <TWÓJ KLUCZ>
SPOTIPY_KEY = <TWÓJ KLUCZ>
LAST_FM_KEY = <TWÓJ KLUCZ>
LAST_FM_URL = 'http://ws.audioscrobbler.com/2.0/'

5. Pobierz:
https://github.com/BtbN/FFmpeg-Builds/releases
np.: https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl-shared.zip
rozpakuj do wybranego folderu (ja dałem do C:\Users\marci\AppData\Local\mpeg) i dodaj ścieżkę do PATH systemowego

6. zaktualizuj "cookies.txt'
Pobierz rozszerzenie chrome do pobeirania plikow cookies
pobierz je i dodaj do projektu