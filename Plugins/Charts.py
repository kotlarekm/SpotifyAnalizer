import pandas as pd
import os
import plotly.express as px
from Plugins.DataProcess import WrappedDataPrepare
from Plugins.DataLoad import ImportFromLocalPlugin
from wordcloud import WordCloud #potrzebne do wizualizacji chmury słow
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from collections import Counter
from pathlib import Path
import ast
import itertools


def przygotuj_dane_tagow(df, tag_number=7):

    all_tags = []
    for tags_list in df['Tags']:
        if isinstance(tags_list, str) and pd.notna(tags_list):
            tags = tags_list.split(',')
            all_tags.extend([tag.strip(" []'\"") for tag in tags])

    tag_counts = pd.Series(all_tags).value_counts(normalize=True) * 100

    # Najpopularniejsze tagi
    top_tags = tag_counts.head(tag_number)
    other_tags = tag_counts[tag_number:]

    if not other_tags.empty:
        top_tags["Inne"] = other_tags.sum()

    tag_df = top_tags.reset_index()
    tag_df.columns = ['Tag', 'Percentage']

    # Lista 3 najpopularniejszych tagów
    top_3 = tag_counts.head(3).index.tolist()

    return tag_df, top_3

def wykres_pie(df, tag_number):
    tag_df, _ = przygotuj_dane_tagow(df, tag_number)
    if tag_df.empty:
        fig = px.pie(values=[100], names=["Brak tagów"], title="Brak danych")
    else:
        pull_values = [0.1 if i == 0 else 0 for i in range(len(tag_df))]
        fig = px.pie(
            tag_df,
            values='Percentage',
            names='Tag',
            title=f"Udział tagów",
            color_discrete_sequence=px.colors.qualitative.Pastel,
            hole=0.3  # efekt "donut"
        )
        fig.update_traces(
            textinfo='percent+label',
            pull=pull_values,
            texttemplate='%{percent:.0%}',
            marker_line_width=0
        )
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)'
        )
    return fig

def najpopularniejsze_tag(df):
    _, top_3 = przygotuj_dane_tagow(df)
    if top_3:
        return f"Najczęściej słuchasz {', '.join(top_3)}"
    else:
        return "Brak danych o tagach."

def wykres_dekady(df):
    df = df.dropna(subset=['Spotify Release Year'])
    df['Decade'] = (df['Spotify Release Year'] // 10 * 10).astype(int).astype(str) + "s"
  
    decade_counts = df['Decade'].value_counts(normalize=True) * 100
    decade_df = decade_counts.reset_index()
    decade_df.columns = ['Decade', 'Percentage']
    decade_df = decade_df.sort_values("Decade")

    if decade_df.empty:
        fig = px.bar(x=["Brak danych"], y=[100], title="Brak danych o dekadach")
    else:
        fig = px.bar(
            decade_df,
            x='Decade',
            y='Percentage',
            title=f"Udział dekad",
            labels={'Percentage': 'Procent (%)', 'Decade': 'Dekada'},
            text='Percentage',
            color='Decade',
            color_discrete_sequence=px.colors.qualitative.Pastel
        )

        fig.update_traces(
            texttemplate='%{text:.1f}%',
            textposition='outside',
            marker_line_width=0
        )
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            yaxis=dict(
                title='Procent (%)',
                ticksuffix='%'
            ),
            bargap=0.2
        )

    return fig


# Funkcja generująca hover text dla wykresów
def make_hover_text(row):
    '''
    Funkcja generująca hover text dla wykresów
    '''
    parts = []
    if pd.notnull(row.get("Artist name")):
        parts.append(f'Artysta: {row["Artist name"]}')
    if pd.notnull(row.get("Album")):
        parts.append(f'Album: {row["Album"]}')
    if pd.notnull(row.get("Track name")):
        parts.append(f'Utwór: {row["Track name"]}')
    if pd.notnull(row.get("Spotify Release Year")):
        parts.append(f'Rok: {int(row["Spotify Release Year"])}')
    if pd.notnull(row.get("Spotify Popularity")):
        parts.append(f'Popularność: {int(row["Spotify Popularity"])}')
    if pd.notnull(row.get("bpm")):
        parts.append(f'BPM: {int(row["bpm"])}')
    if pd.notnull(row.get("energy")):
        parts.append(f'Energia: {row["energy"]:.2f}')
    return "<br>".join(parts)

# Funkcja generująca wykresy
def generate_plots_for_user(df):
# Wybierz top 10 utworów według popularności
    df_top10 = df.sort_values(by="Spotify Popularity", ascending=False).head(10)

# Histogram tempa tylko dla top 10
    fig1 = sns.histplot(df_top10['bpm'], kde=True)
    fig1.set_title("Histogram tempa utworów (Top 10 wg popularności)", fontsize=14, y=1.0)
    

    # Wykres 3: Tree Map Artystów i Albumów
    # Wyświetla interaktywną mapę z artystami i albumami na podstawie popularności
    df["hover_text"] = df.apply(make_hover_text, axis=1)
    tree_map_plot = px.treemap(df, path=["Artist name", "Album"], values="Spotify Popularity", hover_name="hover_text", title="Tree Map – Artysta i album z opisem")

    # Wykres 4: Popularność utworów
    # Prezentuje słupkowy wykres popularności różnych utworów
    fig4 = sns.barplot(data=df, x="Track name", y="Spotify Popularity", hue="Spotify Popularity", palette="coolwarm")
    fig4.set_title("Popularność utworów", fontsize=14, y=1.0)


    # Wykres 8: BPM vs Energia
    # Pokazuje związek między BPM a energią utworów
    fig8 = sns.scatterplot(data=df, x="bpm", y="energy", hue="Spotify Popularity")
    fig8.set_title("BPM vs Energia")

    # Wykres 9: Histogram popularności utworów
    # Pokazuje histogram popularności utworów
    df_top10 = df.sort_values(by="Spotify Popularity", ascending=False).head(100)
    popularity_histogram, ax9 = plt.subplots()
    sns.histplot(df_top10["Spotify Popularity"], kde=True, ax=ax9)
    ax9.set_title("Histogram popularności utworów", fontsize=14, y=1.0)
    ax9.set_ylabel("Liczba utworów")
    ax9.set_xlabel("Popularność (skala od 0 do 100)")
    # Przezroczystość tła dla wykresu 9
    ax9.set_facecolor((1, 1, 1, 0.3))
    popularity_histogram.patch.set_alpha(0.3)

    return {
        "fig1": fig1,
        "fig4": fig4,
        "fig8": fig8,
    }

def generate_histogram(df, column):
    fig, ax = plt.subplots()  # Tworzy nową figurę, unikając konfliktów
    sns.histplot(df[column], kde=True, bins=10, color="skyblue", ax=ax)
    ax.set_xlabel(column)
    ax.set_ylabel("Liczba utworów")
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    return fig

def generate_fig6(df):
    df = df.sort_values(by="Spotify Popularity", ascending=False)
    
    # Tworzymy nową figurę i osie
    fig, ax = plt.subplots()

    # Przezroczystość tła całej figury
    fig.patch.set_alpha(0.3)

    # Przezroczystość tła samego wykresu
    ax.patch.set_alpha(0.3)
    fig = sns.barplot(data=df.head(10), x="Spotify Popularity", y="Track name", hue="Track name", palette="viridis")
    fig.set_title("Popularność utworów - Top 10", fontsize=14, y=1.0)
    ax.set_ylabel("Nazwa utworu")
    ax.set_yticks([])
    ax.set_yticklabels([])
    ax.set_xlabel("Popularność (skala od 0 do 100)")
    top10 = df.head(10)
    for i, (popularity, title) in enumerate(zip(df["Spotify Popularity"], df["Track name"])):
        ax.text(popularity / 2, i, title, ha="center", va="center", color="white", fontsize=14, fontweight="bold", clip_on=True)
 
    return fig  # Shiny wymaga zwrotu całej figury, a nie samej osi


def generate_fig8(df):

    fig, ax = plt.subplots()
    fig.patch.set_alpha(0.3)
    ax.patch.set_alpha(0.3)

    # Znane mapowania (częściowe)
    base_palette = {
        "neutral": "blue",
        "energetic": "orange",
        "bright": "red"
    }

    base_markers = {
        "neutral": "o",       # kółko
        "energetic": "X",     # krzyżyk
        "bright": "P",        # plus w kwadracie
        "unknown": "s"        # kwadrat
    }


    # Wszystkie unikalne wartości mood z danych
    moods_in_data = df["mood"].unique()

    # Uzupełnij brakujące nastroje domyślnymi kolorami/markerami
    available_colors = itertools.cycle(sns.color_palette("husl", 10))
    available_markers = itertools.cycle(["^", "v", "<", ">", "P", "X"])
    full_palette = base_palette.copy()
    full_markers = base_markers.copy()

    for mood in moods_in_data:
        if mood not in full_palette:
            full_palette[mood] = next(available_colors)
        if mood not in full_markers:
            full_markers[mood] = next(available_markers)

    sns.scatterplot(
        data=df,
        x="energy",
        y="danceability",
        hue="mood",
        style="mood",
        palette=full_palette,
        markers=full_markers,
        s=100,
        ax=ax
    )

    ax.set_title("Energia vs taneczność z podziałem na nastrój", fontsize=14, y=1.0)
    ax.set_xlabel("Energia")
    ax.set_ylabel("Taneczność")
    ax.legend(title="Nastrój")

    return fig



def generate_fig10(df):

    def safe_literal_eval(val):
        try:
            if isinstance(val, str):
                return ast.literal_eval(val)
            return [] if pd.isna(val) else val
        except:
            return []

    df["Genres"] = df["Genres"].apply(safe_literal_eval)
    df["Main Genre"] = df["Genres"].apply(lambda g: g[0] if isinstance(g, list) and g else "Brak")
    df = df.sort_values(by="Spotify Popularity", ascending=False)

    # Raport
    grid = sns.lmplot(
        data=df.head(40),
        x='energy',
        y='Spotify Popularity',
        hue="Main Genre",
        height=3,
        aspect=2,
        scatter_kws={'alpha': 0.6}
    )

    # Przezroczystość tła
    grid.fig.patch.set_alpha(0.3)
    for ax in grid.axes.flatten():
        ax.patch.set_alpha(0.3)

        # Ustawienia etykiet osi
        ax.set_xlabel("Energia")
        ax.set_ylabel("Popularność (w skali 0–100)")

    # Tytuł
    grid.fig.suptitle("Energia vs popularność wg gatunku", fontsize=14, y=1.0)

    return grid.fig



def generate_fig11(df):

    def safe_literal_eval(val):
        try:
            if isinstance(val, str):
                return ast.literal_eval(val)
            return [] if pd.isna(val) else val
        except:
            return []

    df["Genres"] = df["Genres"].apply(safe_literal_eval)

    genre_counts = Counter([genre for genres in df["Genres"] for genre in genres])
    genre_df = pd.DataFrame(genre_counts.items(), columns=["Gatunek", "Liczba"]).sort_values("Liczba", ascending=False)

    if genre_df.empty:
        print("Brak gatunków do wyświetlenia.")
        return None

    # Figurę i oś
    fig, ax = plt.subplots(figsize=(8, 6))

    # Tło przezroczyste
    fig.patch.set_alpha(0.3)
    ax.patch.set_alpha(0.3)

    sns.barplot(data=genre_df.head(15), x="Liczba", y="Gatunek", hue="Gatunek", palette="coolwarm", ax=ax)

    ax.set_title("Najczęściej występujące gatunki", fontsize=14, y=1.0)
    ax.set_xlabel("Liczba utworów")
    ax.set_ylabel("Gatunek")

    return fig



# def generate_fig_track_bpm(df):
#     fig, ax = plt.subplots()  # Tworzy nową figurę, unikając konfliktów
#     sns.histplot(df["bpm"], kde=True, bins=10, color="skyblue", ax=ax)
#     ax.set_xlabel("BPM")
#     ax.set_ylabel("Liczba utworów")
    
#     return fig




def generate_fig13(df):

    def safe_literal_eval(val):
        try:
            if isinstance(val, str):
                return ast.literal_eval(val)
            return [] if pd.isna(val) else val
        except:
            return []

    df["Genres"] = df["Genres"].apply(safe_literal_eval)
    df_exploded = df.explode("Genres").dropna(subset=["Genres", "Spotify Popularity"])

    pop_by_genre = df_exploded.groupby("Genres")['Spotify Popularity'].mean().reset_index()
    pop_by_genre.columns = ["Gatunek", "Średnia popularność"]
    pop_by_genre = pop_by_genre.sort_values("Średnia popularność", ascending=False).head(15)

    fig, ax = plt.subplots(figsize=(12, 6))

    # Przezroczystość tła osi 
    ax.set_facecolor((1, 1, 1, 0.3))  # biały z przezroczystością 0.3
    # Przezroczystość całej figury
    fig.patch.set_alpha(0.3)

    sns.barplot(
        data=pop_by_genre,
        x='Gatunek',
        y='Średnia popularność',
        hue='Średnia popularność',
        palette='pastel',
        legend=False,
        ax=ax
    )
    
    ax.set_title("Średnia popularności utworów wg gatunku", fontsize=14, y=1.0)
    ax.tick_params(axis='x', rotation=45)
    plt.tight_layout()
    
    return fig




def generate_fig14(df):

    df["Popularity"] = pd.to_numeric(df["Spotify Popularity"], errors='coerce')
    df["bpm"] = pd.to_numeric(df["bpm"], errors='coerce')

    # Tworzenie jointplot
    fig = sns.jointplot(data=df, x="bpm", y="Popularity", kind="kde", height=5, fill=True)

    # Ustawianie przezroczystości tła
    fig.ax_joint.set_facecolor((1, 1, 1, 0.3))  # tło głównego wykresu
    fig.ax_marg_x.set_facecolor((1, 1, 1, 0.3))  # tło górnego marginesu
    fig.ax_marg_y.set_facecolor((1, 1, 1, 0.3))  # tło bocznego marginesu

    # Przezroczystość całej figury (usuwa białą ramkę)
    fig.fig.patch.set_alpha(0.3)

    # Dodanie tytułu
    fig.fig.suptitle("Zależność między tempem utworu (BPM) a popularnością", fontsize=14, y=1.0)
    fig.fig.tight_layout()
    fig.fig.subplots_adjust(top=0.95)  # miejsce na tytuł

    # Dodanie etykiet osi
    fig.ax_joint.set_xlabel("Tempo utworu (BPM)", fontsize=12)
    fig.ax_joint.set_ylabel("Popularność (Spotify)", fontsize=12)

    return fig


def generate_popularity_boxplot_both(df, df_top):

    # nazwy osi
    df_user_pop = df[["Spotify Popularity"]].dropna().rename(columns={"Spotify Popularity": "Popularność"})
    df_user_pop["Źródło"] = "Użytkownik bazowy"

    df_global_pop = df_top[["Spotify Popularity"]].dropna().rename(columns={"Spotify Popularity": "Popularność"})
    df_global_pop["Źródło"] = "Użytkownik porównawczy"

    pop_df = pd.concat([df_user_pop, df_global_pop])
    # Raport i przezroczystość tła
    fig, ax = plt.subplots()
    fig.patch.set_alpha(0.3)  # Przezroczystość całego tła figury
    ax.set_facecolor((1, 1, 1, 0.3))  # Przezroczystość tła wykresu

    sns.boxplot(data=pop_df, x="Źródło", y="Popularność", ax=ax)
    # Tytuł wykresu
    ax.set_title("Porównanie popularności utworów", fontsize=14, y=1.0)
    return fig


# Trzeba dodać odpowiednią ścieżkę pliku global // parent.parent 
def generate_bpm_histogram_both(df, df_top, save=False):

    # raport
    user_bpm = pd.to_numeric(df["bpm"], errors="coerce").dropna()
    global_bpm = pd.to_numeric(df_top["bpm"], errors="coerce").dropna()
    bpm_df = pd.DataFrame({
        "BPM": list(user_bpm) + list(global_bpm),
        "Źródło": ["Użytkownik bazowy"] * len(user_bpm) + ["Użytkownik porównawczy"] * len(global_bpm)
    })

    # Utwórz figurę i oś ręcznie, by mieć pełną kontrolę
    fig, ax = plt.subplots(figsize=(10, 6))

    # Przezroczystość tła wykresu i figury
    ax.set_facecolor((1, 1, 1, 0.3))  # przezroczystość osi
    fig.patch.set_alpha(0.3)         # przezroczystość całej figury

    # Rysowanie wykresu
    sns.histplot(
        data=bpm_df,
        x="BPM", 
        stat='percent', 
        common_norm=False, 
        hue="Źródło", 
        kde=True, 
        bins=20, 
        multiple="dodge", 
        ax=ax)

    # Tytuł (opcjonalnie)
    ax.set_title("Porównanie rozkładu BPM", fontsize=14, y=1.0)
    ax.set_ylabel("Procent utworów")
    ax.set_xlabel("BPM")
    # Zapis z przezroczystym tłem (opcjonalnie)
    if save:
        fig.savefig("fig15.png", transparent=True)

    return fig



# Funkcja do generowania wykresu Tree Map
def generate_tree_map(df):
    # <- MODIFIED to return fig directly, not save as image
    # Tworzymy kolumnę hover_text do pokazania danych po najechaniu na element
    df["hover_text"] = df.apply(make_hover_text, axis=1)
    
    # Generujemy wykres Tree Map
    tree_map_fig = px.treemap(
        df,
        path=["Artist name", "Album"],  # Hierarchia
        values="Spotify Popularity",  # Wartość do wielkości prostokątów
        hover_name="hover_text",  # Tekst, który się pojawi po najechaniu
    )

    # Zapisz wykres do pliku PNG (musisz podać pełną ścieżkę do folderu, w którym chcesz zapisać)
    output_path = "output_tree_map.png"  # Ścieżka zapisu wykresu
    
    return tree_map_fig  # <- Now returns the plotly figure

    #Generowanie chmury tagów

def generate_wordcloud(df):
    all_genres = []

    for item in df["Genres"].dropna():
        try:
            parsed = ast.literal_eval(item)
        except Exception:
            parsed = item

        # tuple lub lista
        if isinstance(parsed, (tuple, list)):
            for genre in parsed:
                all_genres.append(genre.lower())
        else:
            # pojedynczy string
            all_genres.append(parsed.lower())

    text = " ".join(all_genres)
    wc = WordCloud(width=500, height=300, background_color="white").generate(text)

    return wc

    # all_genres = []
    # for item in df["Genres"].dropna():
    #     try:
    #         genres = ast.literal_eval(item)
    #         for genre in genres:
    #             parts = genre.lower().split()
    #             all_genres.extend(parts)
    #     except Exception:
    #         continue
    # text = " ".join(all_genres)
    # wc = WordCloud(width=500, height=300, background_color="white").generate(text)
    # return wc
