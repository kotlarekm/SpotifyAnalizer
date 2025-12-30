from sklearn.metrics.pairwise import cosine_similarity # potrzebne do porównywania wektorów
import ast

import os


from pathlib import Path

analyser_path = Path(os.getcwd()).resolve()

def create_track_artist_column(df):
    '''
    łączy kolumnę track i artist w jedną
    '''
    df["Track Artist"] = df["Track name"] +" - "+ df["Artist name"]
    return df

def cut_brackets(name):
    '''
    Cut first and last bracket
    '''

    if name[-1:]==']' and name[0:1]=='[':
        name_output = name[1:-1]
    else:
        name_output = name
        print("no brackets found")

    return name_output

def find_similar_songs(base_df, compare_df, top_n=5):
    features = ["bpm", "energy", "danceability"]

    base_features = base_df[features].to_numpy()
    compare_features = compare_df[features].to_numpy()

    sim_matrix = cosine_similarity(compare_features, base_features)
    avg_similarity = sim_matrix.mean(axis=1)

    compare_df = compare_df.copy()
    compare_df["similarity"] = avg_similarity
    return compare_df.sort_values("similarity", ascending=False)

# Ścieżka do plików CSV
def csv_path(folder_path, filename_stem):
    return folder_path / f"{filename_stem}.csv"

# def tagowanie gatunków
def get_unique_genres(df):
    all_genres = set()
    for item in df["Genres"].dropna():
        try:
            genres = ast.literal_eval(item)
            for genre in genres:
                parts = genre.lower().split()
                all_genres.update(parts)
        except Exception:
            continue
    return all_genres

# obliczenie procentu wspólnych gatunków
def genre_overlap_pct(base_df, top_df):
    base_genres = get_unique_genres(base_df)
    compare_genres = get_unique_genres(top_df)

    common_genres = base_genres & compare_genres
    overlap_pct = (len(common_genres) / len(base_genres)) * 100 if base_genres else 0
    return f"{overlap_pct:.1f}%"
