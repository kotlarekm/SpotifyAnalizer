# 1.2 Importowanie bibliotek i modułów niezbędnych do stworzenia aplikacji i analizy danych
from shiny import ui, reactive, render # potrzebne do stworzenia aplikacji
from htmltools import css # potrzebne do stylizacji
from pathlib import Path # potrzebne do pracy z plikami
from Plugins.Charts import generate_fig_popularity_tracks, generate_fig_popularity_danceability, generate_fig_energy_popularity, generate_fig_top_genres, generate_fig_genres_popularity, generate_fig_tempo_popularity
from modules.data_loader import load_user_file

folder_path_wrapped = Path(__file__).resolve().parent.parent / "Data"   # ścieżka do folderu z plikami które są wybierane w lewym panelu  
folder_path_top = Path(__file__).resolve().parent.parent / "DataCompare"   # ścieżka do folderu z plikami które są wybierane w lewym panelu  

def layout():
    return ui.page_fluid(

        ui.row(
            ui.column(12,
                ui.h2("Porównanie danych", classes="text-center"))),
        ui.row(
            ui.column(6,
                ui.h3("Popularność utworów"),
                ui.output_plot("fig_popularity_tracks")),

            ui.column(6,
                ui.h3("Energia vs. taneczność"),
                ui.output_plot("fig_popularity_danceability")
                )    ),
        ui.row(
            ui.column(6,
                ui.h3("Energia vs. popularność"),
                ui.output_plot("fig_energy_popularity")),
                
            ui.column(6,
                ui.h3("Najczęściej występujące gatunki"),
                ui.output_plot("fig_top_genres")
                )    ),
        ui.row(
            ui.column(6,
                ui.h3("Średnia popularności gatunków"),
                ui.output_plot("fig_genres_popularity")),
                
            ui.column(6,
                ui.h3("Tempo a popularność"),
                ui.output_plot("fig_tempo_popularity")
                )    ),
        )

def server(input, output, session):

    @reactive.calc
    def top_df():
        df_top, _ = load_user_file(folder_path_top, input.top_user())
        return df_top

    @reactive.calc
    def top_results_df():
        _, df_top_results = load_user_file(folder_path_top, input.top_user())
        return df_top_results
    
    @output
    @render.plot  
    def fig_popularity_tracks():
        # Przykładowy wykres z pluginu
        fig = generate_fig_popularity_tracks(top_df())
        return fig

    @output
    @render.plot  
    def fig_popularity_danceability():
        fig = generate_fig_popularity_danceability(top_df())
        return fig

    @output
    @render.plot  
    def fig_top_genres():
        fig = generate_fig_top_genres(top_df())
        return fig

    @output
    @render.plot  
    def fig_genres_popularity():
        fig = generate_fig_genres_popularity(top_df())
        return fig
        
    @output
    @render.plot  
    def fig_tempo_popularity():
        fig = generate_fig_tempo_popularity(top_df())
        return fig
        
    @output
    @render.plot  
    def fig_energy_popularity():
        fig = generate_fig_energy_popularity(top_df())
        return fig