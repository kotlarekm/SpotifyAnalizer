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
from Plugins.Charts import generate_histogram, generate_tree_map  # potrzebne do wizualizacji
from Plugins.DataSummary import RecommendationPlugin
from modules.data_loader import load_user_file

folder_wrapped = "Data"   

def layout():
    return ui.page_fluid(
        ui.h3("Muzyczny profil użytkownika"),
        ui.row(
            ui.layout_columns(
                ui.value_box(
                    title="Ulubiony wykonawca",
                    id = "top_artist",            
                    showcase=icon("microphone"),
                    value=ui.output_text("top_artist")
                ),
                ui.value_box(
                    title="Ulubiony album",
                    showcase=icon("compact-disc"),
                    value=ui.output_text("top_album"),
                    id = "top_album",   
                ),
                ui.value_box(
                    title="Ulubiony gatunek muzyczny",
                    showcase=icon("tags"),
                    value=ui.output_text("top_gatunek"),
                    id = "top_gatunek",   
                ),
                ui.value_box(
                    title="Ulubiona charakterysta brzmienia",
                    showcase=icon("soundcloud"),
                    value=ui.output_text("top_mood"),
                    id = "top_mood",   
                ),
                col_widths=(3,3,3,3),
            ),
        ),
        ui.h3("Wskaźniki charakterystyki utworów"),
        ui.row(
            ui.layout_columns(
                ui.value_box(
                    title="Średnia wskaźnika taneczności",
                    id = "danceability",            
                    showcase=icon("music"),
                    value=ui.output_text("mean_danceability")
                ),
                ui.value_box(
                    title="Średnia wskaźnika energiczności",
                    id = "energy",            
                    showcase=icon("bolt"),
                    value=ui.output_text("mean_energy")
                ),
                ui.value_box(
                    title="Średnia tempa utworów",
                    id = "bpm",            
                    showcase=icon("fire"),
                    value=ui.output_text("mean_bpm")
                ),
                ui.value_box(
                    title="Mediana wieku utworów (lata)",
                    id = "Mediana_Track_Age",            
                    showcase=icon("hourglass"),
                    value=ui.output_text("median_Track_Age")
                ),
                col_widths=(3,3,3,3),
            ), 
            ),

        ui.h3("Utwory naj-"),
        ui.row(
            ui.layout_columns(
                ui.value_box(
                    title="Najpopularniejszy utwor",
                    id = "most_popular",            
                    showcase=icon("star"),
                    value=ui.output_text("most_popular")
                ),
                ui.value_box(
                    title="Najmniej popularny utwór",
                    id = "least_popular",            
                    showcase=icon("feather"),
                    value=ui.output_text("least_popular")
                ),
                ui.value_box(
                    title="Najmłodszy utwór",
                    id = "youngest_track",            
                    showcase=icon("baby"),
                    value=ui.output_text("youngest_track")
                ),
                ui.value_box(
                    title="Najstarszy utwór",
                    id = "oldest_track",            
                    showcase=icon("clock"),
                    value=ui.output_text("oldest_track")
                ),
                col_widths=(3,3,3,3),
            ), 
            ),           

        ui.h3("Ulubieni wykonawcy i albumy"),
        ui.row(
            ui.column(6, ui.output_plot("chmura20_wykonawcow")),
            ui.column(6, ui.output_plot("chmura_albumow_user1")),
            ),                    
        
        ui.h3("Rozkład tempa utworów"),
        ui.row(
                ui.output_plot("fig_track_bpm", "100%"),
            ),
        ui.h3("Mapa utworów - Artysta i album z opisem"),
        ui.row(
            output_widget("tree_map")
        )
    )

def server(input, output, session):

    @reactive.calc
    def base_df():
        df_base, _ = load_user_file(folder_wrapped, input.base_user())
        return df_base

    @reactive.calc
    def base_results_df():
        _, df_base_results = load_user_file(folder_wrapped, input.base_user())
        return df_base_results

    @output
    @render.text
    def top_artist():
        df = base_results_df()
        try:
            top_artist = df["Top artists"][0].split(",")[0]
            return top_artist
        except:
            return "Brak danych"

    @output
    @render.text
    def top_album():
        df = base_results_df()

        try:
            top_album = df["Top albums"][0].split(",")[0]
            return top_album
        except:
            return "Brak danych"

    @output
    @render.text
    def top_gatunek():
        df = base_results_df()

        try:
            top_genre = df["Top genres"][0].split(",")[0]
            return top_genre
        except:
            return "Brak danych"
    

    # Ulubionq charakterysta brzmienia
 
    @output
    @render.text
    def top_mood():
        df = base_results_df()

        try:
            top_mood = df["Top mood"][0]
            return top_mood
        except:
            return "Brak danych"

  # sredni wskaznik danceability
    @output
    @render.text
    def mean_danceability():  
        df = base_results_df()

        try:
            danceability = round(df["Danceability avg"][0],4)
            return danceability
        except:
            return "Brak danych"


    # mediana tempa utworów

    @output
    @render.text
    def mean_bpm():  
        df = base_results_df()

        try:
            bpm = round(df["Bpm avg"][0],0)
            return bpm
        except:
            return "Brak danych"

  # sredni wskaznik energii

    @output
    @render.text
    def mean_energy():  
        df = base_results_df()

        try:
            energy = round(df["Energy avg"][0],4)
            return energy
        except:
            return "Brak danych"

    # mediana wieku utworów

    @output
    @render.text
    def median_Track_Age(): 
        df = base_results_df()

        try:
            track_age = round(df["Age median"][0],0)
            return track_age
        except:
            return "Brak danych"

    # Utowry naj

    @output
    @render.text
    def most_popular(): 
        df = base_results_df()

        try:
            track = df["Most popular"][0]
            return track
        except:
            return "Brak danych"

    @output
    @render.text
    def least_popular(): 
        df = base_results_df()

        try:
            track = df["Least popular"][0]
            return track
        except:
            return "Brak danych"
        
    @output
    @render.text
    def youngest_track(): 
        df = base_results_df()

        try:
            track = df["Youngest track"][0]
            return track
        except:
            return "Brak danych"       

    @output
    @render.text
    def oldest_track(): 
        df = base_results_df()

        try:
            track = df["Oldest track"][0]
            return track
        except:
            return "Brak danych"  

    #lista base_user top 10 artystów
    @output
    @render.data_frame
    def Top_10_artists_user1():
        df = base_df()

        # Grupowanie i liczenie wystąpień
        artist_counts = df['Artist name'].value_counts()

        # Filtrowanie tylko tych, którzy występują co najmniej 2 razy
        repeated_artists = artist_counts[artist_counts >= 2]

        # Konwersja do DataFrame do wyświetlenia
        result_df = repeated_artists.reset_index()
        result_df.columns = ['Artist name', 'Count']

        # Wybierz tylko top 10 i kolumnę 'Artist name'
        result_df = result_df.head(10)[['Artist name']]

        return render.DataGrid(result_df)
    
    #chmura base_user top 20 artystów
    @output
    @render.plot
    def chmura20_wykonawcow():
        df = base_df()

        # Liczenie wystąpień wykonawców
        artist_counts = df['Artist name'].value_counts()

        # Filtr: tylko wykonawcy z co najmniej 2 utworami
        repeated_artists = artist_counts[artist_counts >= 2]

        # Wybór Top 20
        top_artists = repeated_artists.head(20)

        # Generowanie chmury
        wc = WordCloud(width=800, height=400, background_color="white")
        wc.generate_from_frequencies(top_artists.to_dict())

        # Rysowanie wykresu
        plt.figure(figsize=(10, 5))
        plt.imshow(wc, interpolation="bilinear")
        plt.axis("off")
        plt.title(f"Top 20 wykonawców – {input.base_user()}")
        plt.tight_layout()

 

    #base_user top 10 albumow
    @output
    @render.data_frame
    def Top_10_albumow_user1():
        df = base_df()

        # Grupowanie i liczenie wystąpień
        Album_counts = df['Album'].value_counts()

        # Filtrowanie tylko tych, którzy występują co najmniej 2 razy
        repeated_Album = Album_counts[Album_counts >= 2]

        # Konwersja do DataFrame do wyświetlenia
        result_df = repeated_Album.reset_index()
        result_df.columns = ['Album', 'Count']

        # Wybierz tylko top 10 i kolumnę 'Artist name'
        result_df = result_df.head(10)[['Album']]

        return render.DataGrid(result_df)

#chmura base_user top 20 albumow
    @output
    @render.plot
    def chmura_albumow_user1():
        df = base_df()

        # Liczenie wystąpień albumów
        album_counts = df['Album'].value_counts()

        # Filtr: tylko albumy z co najmniej 2 utworami
        repeated_albums = album_counts[album_counts >= 2]

        # Wybierz Top 20
        top_albums = repeated_albums.head(20)

        # Generowanie chmury
        wc = WordCloud(width=800, height=400, background_color="white")
        wc.generate_from_frequencies(top_albums.to_dict())

        # Rysowanie wykresu
        plt.figure(figsize=(10, 5))
        plt.imshow(wc, interpolation="bilinear")
        plt.axis("off")
        plt.title(f"Top 20 albumów – {input.base_user()}")
        plt.tight_layout()

    @output
    @render.plot  
    def fig_track_bpm():
        return generate_histogram(base_df(), "bpm")

    
    @output
    @render_plotly
    def tree_map():
        df = base_df()

        if df is not None:
            # Generowanie wykresu Tree Map na podstawie danych i zapisanie do pliku
            image_path = generate_tree_map(df)  # Funkcja generująca Tree Map i zapisująca go do pliku PNG
            return image_path  # Zwróć ścieżkę do pliku obrazu
        else:
            return None