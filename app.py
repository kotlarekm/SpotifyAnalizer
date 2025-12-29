# 1. Kroki wstępne
# 1.1 Instalowanie bibliotek i modułów niezbędnych do stworzenia aplikacji i analizy danych
# Ctrl + Shift + P - wybierz python 3.11
# Instalacja biblioterk porzez plik pip install requirements.txt
## instal Python VSCode extension https://shiny.posit.co/py/docs/install-create-run.html#:~:text=Python%20VSCode%20extension
#  instal shiny extensions https://marketplace.visualstudio.com/items?itemName=posit.shiny

# 1.2 Importowanie bibliotek i modułów niezbędnych do stworzenia aplikacji i analizy danych
from shiny import ui, App, reactive, module  # potrzebne do stworzenia aplikacji
from htmltools import css # potrzebne do stylizacji
from pages import singleUser, twoUsers, userGlobal, globalAnalize, fileSelection
from Plugins.Utils import load_user_file
from pathlib import Path # potrzebne do pracy z plikami

folder_path_wrapped = Path(__file__).resolve().parent / "Data"   # ścieżka do folderu z plikami które są wybierane w lewym panelu  
folder_path_top = Path(__file__).resolve().parent / "DataCompare"   # ścieżka do folderu z plikami które są wybierane w lewym panelu  

# 2. Tworzymy interfejs użytkownika (UI)
app_ui = ui.page_fluid(
    ui.include_css("www/styles.css"),
    ui.h2("Analizator muzycznych preferencji użytkowników Spotify"),  # Nagłówek
    ui.layout_columns(
        ui.panel_well(
            fileSelection.layout()
        ),
        ui.panel_well(
            ui.navset_tab(
                ui.nav_panel("Raport użytkownika", 
                    singleUser.layout()

                ),
                ui.nav_panel("Porównanie gustów użytkowników", 
                    twoUsers.layout()
                ),
                ui.nav_panel(
                    "Porównanie z danymi globlanymi",
                   userGlobal.layout()
                ),
                ui.nav_panel(
                    "Analiza danych globalnych",
                   globalAnalize.layout()
                )
            )
        ),
        col_widths=[2, 10]
    ),
    title="Analizator muzycznych preferencji użytkowników Spotify", # Tytuł aplikacji - nazwa na pasku przeglądarki
    style=css(
    background_image="url('https://www.stilfon.com/wp-content/uploads/2022/02/B56.jpg')",
    background_repeat="repeat",
    background_size="cover",
    background_position="center center",
    ),
)


# 3. Tworzymy funkcje serwera (co ma się dziać po stronie logiki)


def server(input, output, session):

    # #Wczytanie ramek danych
    
    @reactive.calc
    def base_data(): 
        df, df_results = load_user_file(folder_path_wrapped, input.base_user()) 
        return df, df_results
    
    @reactive.calc
    def compare_data():
        df, df_results = load_user_file(folder_path_wrapped, input.compare_user()) 
        return df, df_results

    @reactive.calc
    def top_data():
        df, df_results = load_user_file(folder_path_top, input.top_user())
        return df, df_results   

    fileSelection.server(input, output, session)    
    singleUser.server(input, output, session, base_data)
    twoUsers.server(input, output, session, base_data, compare_data)
    userGlobal.server(input, output, session, base_data, top_data)
    globalAnalize.server(input, output, session, top_data)

# 4. Tworzymy aplikację
app = App(app_ui, server)


## Shiny apps can be launched from Visual Studio Code running with the Shiny extension 
# or the command line (via shiny run). shiny run --reload C:/Users/slepo/OneDrive/Pulpit/studia/Projekt/app.py

## http://127.0.0.1:8000/ lokalnym serwerze na porcie
