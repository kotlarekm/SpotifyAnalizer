# 1.2 Importowanie bibliotek i modułów niezbędnych do stworzenia aplikacji i analizy danych
from shiny import ui, App, reactive, render # potrzebne do stworzenia aplikacji
from htmltools import css # potrzebne do stylizacji
import pandas as pd # potrzebne do pracy z danymi
import numpy as np # potrzebne do pracy z danymi
from pathlib import Path # potrzebne do pracy z plikami
from sklearn.metrics.pairwise import cosine_similarity # potrzebne do porównywania wektorów
import os # potrzebne do pracy z plikami
from faicons import icon_svg as icon # potrzebne do ikon
import plotly.express as px # potrzebne do wizualizacji
from shinywidgets import output_widget, render_plotly # potrzebne do wizualizacji 
import ast # potrzebne do konwersji stringów do list
from wordcloud import WordCloud #potrzebne do wizualizacji chmury słow
import matplotlib.pyplot as plt #potrzebne do wizualizacji chmury słow
from Plugins.DataProcess import WrappedDataPrepare # potrzebne do przygotowania danych
from Plugins.DataLoad import ImportFromLocalPlugin # potrzebne do wczytywania danych
from Plugins.DataSummary import WrappedSummaryPlugin # potrzebne do podsumowania danych
from Plugins.DataSummary import RecommendationPlugin

# 2. Przygotowanie danych, zmiennych i funkcji
# 2.1. Odczytywanie nazwy plikow csv
folder_path_wrapped = Path(__file__).resolve().parent.parent / "Data"   # ścieżka do folderu z plikami które są wybierane w lewym panelu  
user_files = [   # lista plików csv, wraz z filtrami
    os.path.splitext(file)[0]
    for file in os.listdir(folder_path_wrapped)
    if file.endswith(".csv") and "Wrapped" in file and "result" not in file
]  

# 2.2 Budowa słownika który umożliwia identyfikację, który użytkownik jest główny, a który służy do porównywania. { "User1": "User1", ... } 
users_dict = {user: user for user in user_files}      

# 2.3 Lista plików csv z filtrem 'TOP' i 'HIT' 
folder_path_top = Path(__file__).resolve().parent.parent / "DataCompare"   # ścieżka do folderu z plikami które są wybierane w lewym panelu  
top_files = [
    os.path.splitext(file)[0] for file in os.listdir(folder_path_top)
    if file.endswith(".csv") and ("top" in file.lower() or "hit" in file.lower()) and "result" not in file.lower()
]
top_files_dict = {file: file for file in top_files}

# Layout

def layout():
    return ui.page_fluid(
        ui.h3("Dane wejściowe"),
        ui.input_select("base_user", "Wybierz użytkownika bazowego (plik):", users_dict),
        ui.input_select("compare_user", "Wybierz użytkownika do porównania (plik):", users_dict, selected='WrappedMarcin2024'),# selected=list(users_dict.items()[1][0])),
        ui.input_select("top_user", "Wybierz plik do porównania:", top_files_dict)
    )

def server(input, output, session):
    pass