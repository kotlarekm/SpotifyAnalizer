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
from Plugins.Charts import wykres_pie, najpopularniejsze_tag, wykres_dekady, generate_plots_for_user, generate_wordcloud, generate_histogram, generate_popularity_boxplot_both, generate_bpm_histogram_both # potrzebne do wizualizacji
from Plugins.Utils import csv_path, create_track_artist_column, genre_overlap_pct
from Plugins.DataSummary import RecommendationPlugin
from modules.data_loader import load_user_file

folder_path_wrapped = Path(__file__).resolve().parent.parent / "Data"   # ścieżka do folderu z plikami które są wybierane w lewym panelu  
folder_path_top = Path(__file__).resolve().parent.parent / "DataCompare"   # ścieżka do folderu z plikami które są wybierane w lewym panelu  

def layout():
    return ui.page_fluid(

    ui.h3("Podobieństwo gustów użytkowników"),
    ui.row(
    ui.layout_columns(
    ui.value_box(
                title="Wspólne utwory",
                id = "track_overlap_info",            
                showcase=icon("music"),
                value=ui.output_text("track_overlap_user_global")),
    ui.value_box(
                title="Wspólni wykonawcy",
                id = "artists_overlap_info",            
                showcase=icon("microphone"),
                value=ui.output_text("artists_overlap_user_global")),
    ui.value_box(
                title="Wspólne tagi gatunków muzycznych",
                id = "genre_overlap_info",            
                showcase=icon("tags"),
                value=ui.output_text("genre_overlap_user_global")),
    col_widths=(4,4,4),)),

 
    ui.h3("Porównanie parametrów użytkowników - Użytkownik bazowy"),
    ui.output_data_frame("table_compare_user_global"),


    ui.layout_columns(
        ui.panel_well(
            ui.h3("Tagi bazowego użytkownika"),
            ui.output_text("top_tags_base_raport_user_global"),
            ui.output_ui("wykres_base_raport_user_global"),
        ),
        ui.panel_well(
            ui.h3("Tagi użytkownika porównawczego"),
            ui.output_text("top_tags_compare_raport_user_global"),
            ui.output_ui("wykres_compare_raport_user_global"),
        ),
    ),
    ui.layout_columns(
        ui.panel_well(
            ui.h3("Dekady bazowego użytkownika"),
            ui.output_ui("wykres_dekady_base_raport_user_global"),
        ),
        ui.panel_well(
            ui.h3("Dekady użytkownika porównawczego"),
            ui.output_ui("wykres_dekady_compare_raport_user_global"),
        ),
    ),
    ui.h3("🧑‍🤝‍🧑 🎶 Porównanie gatunków muzycznych"),
    ui.row(
        ui.column(6, ui.output_plot("wordcloud_user1_user_global")),
        ui.column(6, ui.output_plot("wordcloud_user2_user_global")),
        ),
    ui.row(
        ui.column(6, ui.output_plot("popularity_histogram_base_user_global")),
        ui.column(6, ui.output_plot("popularity_histogram_compare_user_global")),
        ),

    ui.layout_columns(
        ui.panel_well(
            ui.h3("Porównanie bpm"),
            ui.output_plot('bpm_histogram_both_user_global')),
        
        ui.panel_well(
            ui.h3("Porównanie popularności"),
            ui.output_plot('popularity_boxplot_both_user_global')),
    ),
    ui.row(
        ui.column(4, ui.markdown("### 📀 Wspólne utwory")),
        ui.column(4, ui.markdown("### 🎤 Wspólne wykonawcy")),
        ui.column(4, ui.markdown("### 🎧 Polecane utwory globalne")),
        ),
    ui.row(
        ui.column(4, ui.output_table("common_tracks_user_global")),
        ui.column(4, ui.output_table("common_artist_user_global")),
        ui.column(4, ui.output_table("recommended_tracks_compare_user_global")),
    )
    )

def server(input, output, session):

    #Wczytanie ramek danych
    @reactive.calc
    def base_df():
        df_base, _ = load_user_file(folder_path_wrapped, input.base_user())
        return df_base

    @reactive.calc
    def base_results_df():
        _, df_base_results = load_user_file(folder_path_wrapped, input.base_user())
        return df_base_results

    @reactive.calc
    def top_df():
        df_top, _ = load_user_file(folder_path_top, input.top_user())
        return df_top

    @reactive.calc
    def top_results_df():
        _, df_top_results = load_user_file(folder_path_top, input.top_user())
        return df_top_results

#  % wspólnych utworów
    @output()
    @render.text
    def track_overlap_user_global():
    # Wspólne utwory
        base_tracks = set(base_df()["Track name"].dropna())
        compare_tracks = set(top_df()["Track name"].dropna())
        common_tracks = base_tracks & compare_tracks

    # Procent wspólnych utworów
        track_overlap_pct = (len(common_tracks) / len(base_tracks)) * 100 if base_tracks else 0
    
        return f"{track_overlap_pct:.1f}%"
        
#  % wspólnych artystów
    @output()
    @render.text
    def artists_overlap_user_global():
    # Wspólne utwory
        base_artists = set(base_df()["Artist name"].dropna())
        compare_artists = set(top_df()["Artist name"].dropna())
        common_artists = base_artists & compare_artists

    # Procent wspólnych utworów
        artists_overlap_pct = (len(common_artists) / len(base_artists)) * 100 if base_artists else 0
    
        return f"{artists_overlap_pct:.1f}%"

    # % wspolnych tagów gatunków muzycznych

    @output()
    @render.text
    def genre_overlap_user_global():
        return genre_overlap_pct(base_df(), top_df())
    
    #Porównanie parametrów
    @render.data_frame
    def table_compare_user_global():
        df_base = base_results_df()
        df_compare = top_results_df()

        df_parameters = pd.DataFrame(
            {
                " ": ["Taneczność", "Energiczność", "Tempo", "Wiek utworów", "Popularność", "Najpopularniejszy utwor", "Najmniej popularny utwór", "Najmłodszy utwór", "Najstarszy utwór"],
                "Bazowy":[
                        round(df_base["Danceability avg"][0], 4),
                        round(df_base["Energy avg"][0], 4),
                        round(df_base["Bpm avg"][0], 2),
                        round(df_base["Age median"][0], 2),
                        round(df_base["Popularity avg"][0], 2),
                        df_base["Most popular"][0],
                        df_base["Least popular"][0],
                        df_base["Youngest track"][0],
                        df_base["Oldest track"][0],
                    ],
                "Porównawczy":[
                        round(df_compare["Danceability avg"][0], 4),
                        round(df_compare["Energy avg"][0], 4),
                        round(df_compare["Bpm avg"][0], 2),
                        round(df_compare["Age median"][0], 2),
                        round(df_compare["Popularity avg"][0], 2), 
                        df_compare["Most popular"][0],
                        df_compare["Least popular"][0],
                        df_compare["Youngest track"][0],
                        df_compare["Oldest track"][0],
            ]})
        
        return render.DataTable(df_parameters, width='100%', height=None, styles={"margin-bottom": "0px"})

    #Tagi użytkowników

    @output
    @render.ui
    def wykres_base_raport_user_global():
        return wykres_pie(base_df(), 15)

    @output
    @render.ui
    def wykres_compare_raport_user_global():
        return wykres_pie(top_df(), 15)


    # Porównanie gatunków muzycznych
    @output
    @render.text
    def top_tags_base_raport_user_global():
        return najpopularniejsze_tag(base_df())
   
    # Dekady użytkowników

    @output
    @render.text
    def top_tags_compare_raport_user_global():
        return najpopularniejsze_tag(top_df() )

    @output
    @render.ui
    def wykres_dekady_base_raport_user_global():
        return wykres_dekady(base_df())

    @output
    @render.ui
    def wykres_dekady_compare_raport_user_global():
        return wykres_dekady(top_df())

    # wykreslenie chmury tagow gatunków w zalezosci od uzytkowniaków


    @output()
    @render.plot
    def wordcloud_user1_user_global():
        wc = generate_wordcloud(base_df())
    
        fig = plt.figure(figsize=(6, 4))
        fig.patch.set_alpha(0.3)  # Przezroczystość tła figury

        ax = plt.gca()
        ax.set_facecolor((1, 1, 1, 0.3))  # Przezroczystość tła 
    
        plt.imshow(wc, interpolation="bilinear")
        plt.axis("off")
        plt.title(f"{input.base_user()} - gatunki")
        plt.tight_layout()


    @output()
    @render.plot
    def wordcloud_user2_user_global():
        wc = generate_wordcloud(top_df())
        fig = plt.figure(figsize=(6, 4))
        fig.patch.set_alpha(0.3)  # Przezroczystość tła figury

        ax = plt.gca()
        ax.set_facecolor((1, 1, 1, 0.3))  # Przezroczystość tła 

        plt.imshow(wc, interpolation="bilinear")
        plt.axis("off")
        plt.title(f"{input.compare_user()} - gatunki")
        plt.tight_layout()

    #histogram popularności utworów
    @output
    @render.plot  
    def popularity_histogram_base_user_global():
        return generate_histogram(base_df(), "Spotify Popularity")
    
    @output
    @render.plot  
    def popularity_histogram_compare_user_global():
        return generate_histogram(top_df(), "Spotify Popularity")
    
    @output
    @render.plot  
    def bpm_histogram_both_user_global():
        fig = generate_bpm_histogram_both(base_df(), top_df())
        return fig

    @output
    @render.plot  
    def popularity_boxplot_both_user_global():
        fig = generate_popularity_boxplot_both(base_df(), top_df())
        return fig
    
    # rekomendacje
    #rekomendacje użytkownika 1

    @output
    @render.table
    def recommended_tracks_compare_user_global():

        df_base = base_df()
        df_compare = top_df()

        Recommendation = RecommendationPlugin()
        _, df_compare_recommended = Recommendation.show_recommendation(df_base, df_compare, 10)
        df_compare_recommended = df_compare_recommended.rename(columns = {"Track Artist":"Track"} )

        return pd.DataFrame(df_compare_recommended, columns=["Track"])

   # wspólne utwory
    @output()
    @render.table
    def common_tracks_user_global():
       # Pobierz dane


        base_tracks = set(create_track_artist_column(base_df())["Track Artist"].dropna())
        compare_tracks = set(create_track_artist_column(top_df())["Track Artist"].dropna())
        common = base_tracks & compare_tracks

        
        if not common:
            return pd.DataFrame([["Brak wspólnych artystów"]], columns=["Track Artist"])
        else:
            return pd.DataFrame(sorted(common), columns=["Track"])
    
    # wspólni wykonawcy
    @output()
    @render.table
    def common_artist_user_global():
        base_tracks = set(base_df()["Artist name"].dropna())
        compare_tracks = set(top_df()["Artist name"].dropna())
        common = base_tracks & compare_tracks

        if not common:
            return pd.DataFrame([["Brak wspólnych artystów"]], columns=["Artist name"])
    
        return pd.DataFrame(sorted(common), columns=["Artist name"])



    # unikalne utwory
    # UNIKALNE UTWORY UŻYTKOWNIKA 1
    ### NOT USED
    # @output()
    # @render.table
    # def unique_tracks_user1():
    #     base_tracks = set(base_df()["Track name"].dropna())
    #     compare_tracks = set(top_df()["Track name"].dropna())
    #     unique_user1 = base_tracks - compare_tracks

    #     if not unique_user1:
    #         return pd.DataFrame([["Brak unikalnych utworów"]], columns=["Track name"])
    
    #     return pd.DataFrame(sorted(unique_user1), columns=["Track name"]).head(10)
    

    # # UNIKALNE UTWORY UŻYTKOWNIKA 2
    # @output()
    # @render.table
    # def unique_tracks_user2():
    #     base_tracks = set(base_df()["Track name"].dropna())
    #     compare_tracks = set(top_df()["Track name"].dropna())
    #     unique_user2 = compare_tracks - base_tracks

    #     if not unique_user2:
    #         return pd.DataFrame([["Brak unikalnych utworów"]], columns=["Track name"])

    #     return pd.DataFrame(sorted(unique_user2), columns=["Track name"]).head(10)
