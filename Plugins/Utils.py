from sklearn.metrics.pairwise import cosine_similarity # potrzebne do porównywania wektorów

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