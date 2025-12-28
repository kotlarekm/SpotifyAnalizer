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
from Plugins.Charts import generate_fig6, generate_fig8, generate_fig10, generate_fig11, generate_fig13, generate_fig14, generate_fig15, generate_fig16
import importlib.util
from Plugins.DataSummary import RecommendationPlugin
from modules.data_loader import load_user_file

folder_path_wrapped = Path(__file__).resolve().parent.parent / "Data"   # ścieżka do folderu z plikami które są wybierane w lewym panelu  
folder_path_top = Path(__file__).resolve().parent.parent / "DataCompare"   # ścieżka do folderu z plikami które są wybierane w lewym panelu  
print(folder_path_top)

def layout():
    return ui.page_fluid(
        ui.row(
            ui.column(6,
                ui.output_plot('fig15')),
            ui.column(6,
                ui.output_plot('fig16')),
        ),
        ui.row(
            ui.column(12,
                        ui.h2("Porównanie danych", classes="text-center"))),
        ui.row(
            ui.column(6,
                ui.h3("🧑‍🤝‍🧑 Użytkownik")),
            ui.column(6,
                ui.h3("🎶 Globalne dane"))    ),
        ui.row(
            ui.column(6,
                ui.output_plot("fig6")),
            ui.column(6,
                ui.output_plot("fig6b"))    ),
        ui.row(
            ui.column(6,   
                ui.output_plot("fig8")),
            ui.column(6,   
                ui.output_plot("fig8b"))    ),
        ui.row(        
            ui.column(6,    
                ui.output_plot("fig10")),
            ui.column(6,    
                ui.output_plot("fig10b"))   ),
        ui.row(        
            ui.column(6,    
                ui.output_plot("fig11")),
            ui.column(6,    
                ui.output_plot("fig11b"))   ),
        ui.row(        
            ui.column(6,    
                ui.output_plot("fig13")),
            ui.column(6,    
                ui.output_plot("fig13b"))   ),
        ui.row(        
            ui.column(6,    
                ui.output_plot("fig14")),
            ui.column(6,    
                ui.output_plot("fig14b"))   ),
        )

def server(input, output, session):
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


    @output
    @render.plot  
    def fig11():
        fig = generate_fig11(base_df())
        return fig
    
    @output
    @render.plot  
    def fig11b():
        fig = generate_fig11(top_df())
        return fig

    @output
    @render.plot  
    def fig13():
        fig = generate_fig13(base_df())
        return fig

    @output
    @render.plot  
    def fig13b():
        fig = generate_fig13(top_df())
        return fig
    
    @output
    @render.plot  
    def fig14():
        fig = generate_fig14(base_df())
        return fig
    
    @output
    @render.plot  
    def fig14b():
        fig = generate_fig14(top_df())
        return fig
    
    @output
    @render.plot  
    def fig15():
        fig = generate_fig15(base_df(), top_df())
        return fig

    @output
    @render.plot  
    def fig16():
        fig = generate_fig16(base_df(), top_df())
        return fig

    @output
    @render.plot  
    def fig6():
        # Przykładowy wykres z pluginu
        fig = generate_fig6(base_df())
        return fig
    
    @output
    @render.plot  
    def fig6b():
        # Przykładowy wykres z pluginu
        fig = generate_fig6(top_df())
        return fig

    @output
    @render.plot  
    def fig8():
        fig = generate_fig8(base_df())
        return fig
    
    @output
    @render.plot  
    def fig8b():
        fig = generate_fig8(top_df())
        return fig
            

    @output
    @render.plot  
    def fig10():
        fig = generate_fig10(base_df())
        return fig
    
    @output
    @render.plot  
    def fig10b():
        fig = generate_fig10(top_df())
        return fig