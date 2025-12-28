from dotenv import load_dotenv

import pandas as pd
import numpy as np

from Plugins.Utils import create_track_artist_column


load_dotenv("log_data.env")

class WrappedSummaryPlugin:
    '''
    Klasa do podsumowania obrobionych danych
    '''
    def __init__(self):
        pass

    def prepare_df(self):
        self.df_results = pd.DataFrame(
        {
            "Top albums": pd.Series(dtype="str"),
            "Top genres": pd.Series(dtype="str"),
            "Top artists": pd.Series(dtype="str"),
            "Most popular": pd.Series(dtype="str"),
            "Least popular": pd.Series(dtype="str"),
            "Popularity avg": pd.Series(dtype="int64"),
            "Bpm avg" : pd.Series(dtype="float"),
            "Energy avg": pd.Series(dtype="int64"),
            "Danceability avg": pd.Series(dtype="float"),
            "Top mood": pd.Series(dtype="str"),
            "Top tags": pd.Series(dtype="str"),
            "Oldest track":pd.Series(dtype="str"),
            "Youngest track":pd.Series(dtype="str"),
            "Age avg":pd.Series(dtype="int64"),
        }
        )

        return self.df_results

    def calc_averages(self, df):
        '''
        oblicza średnie paramtery  bpm, energy, danceability
        '''

        Bpm = pd.to_numeric(df['bpm'], errors='coerce')
        self.df_results.at[0,"Bpm avg"] = np.mean(Bpm)      

        Energy = pd.to_numeric(df['energy'], errors='coerce')
        self.df_results.at[0,"Energy avg"] = np.mean(Energy) 

        Danceability = pd.to_numeric(df['danceability'], errors='coerce')
        self.df_results.at[0,"Danceability avg"] = np.mean(Danceability)

        return self.df_results
    
    def search_top(self, df):
        '''
        Wyciąga "topki" - gatunków, nastrojów, itp.
        '''
        Moods = df["mood"]
        self.df_results.at[0,"Top mood"] = Moods.value_counts().keys()[0]

        Albums = df["Album"]
        Album_top = Albums.value_counts()
        self.df_results.at[0,"Top albums"] = ", ".join(Album_top.head().keys().to_list())

        Artists = df["Artist name"]
        Artist_top = Artists.value_counts()
        Artist_top.head()
        self.df_results.at[0,"Top artists"] = ", ".join(Artist_top.head().keys().to_list())

        all_genres = []
        for genres_list in df['Genres']:
            if isinstance(genres_list, str) and pd.notna(genres_list):
                genres = genres_list.split(',')
                all_genres.extend([genre.strip() for genre in genres])
        genre_top_separate = pd.Series(all_genres).value_counts()
        genre_top_separate.head(10)
        self.df_results.at[0,"Top genres"] = ", ".join(genre_top_separate.head(10).keys().to_list())

        all_tags = []
        for tags_list in df['Tags']:
            if isinstance(tags_list, str) and pd.notna(tags_list):
                tags = tags_list.strip('[]')
                tags = tags.split(',')
                all_tags.extend([tag.strip() for tag in tags])
        Tag_top_separate = pd.Series(all_tags).value_counts()
        Tag_top_separate.head(10)
        self.df_results.at[0,"Top tags"] = ", ".join(Tag_top_separate.head(10).keys().to_list())

        return self.df_results
    
    def age_analysis(self, df):
        '''
        Analizuje wiek - średni, najstarszy i najmłodszy utwór
        '''
        Track_age = pd.to_numeric(df['Track Age'], errors='coerce')
        self.df_results.at[0,"Age avg"] = np.mean(Track_age)
        self.df_results.at[0,"Age median"] = np.median(Track_age)

        sorted_df = df.sort_values(by="Spotify Release Date")
        last_index = sorted_df["Track name"].count()-1
        self.df_results.at[0, "Oldest track"] = sorted_df["Track name"].iloc[0] + " : " + sorted_df["Artist name"].iloc[0]
        self.df_results.at[0, "Youngest track"] = sorted_df["Track name"].iloc[last_index] + " : " + sorted_df["Artist name"].iloc[last_index]

        return self.df_results

    def popularity_analysis(self, df):
        '''
        Analizuje popularność utworów, średnią, najpopularniejszy i najmniej popularny
        '''
        Popularity = pd.to_numeric(df['Spotify Popularity'], errors='coerce')
        self.df_results.at[0,"Popularity avg"] = np.mean(Popularity)

        sorted_df = df.sort_values(by="Spotify Popularity")
        last_index = sorted_df["Track name"].count()-1
        self.df_results.at[0, "Least popular"] = sorted_df["Track name"].iloc[0] + " : " + sorted_df["Artist name"].iloc[0]
        self.df_results.at[0, "Most popular"] = sorted_df["Track name"].iloc[last_index] + " : " + sorted_df["Artist name"].iloc[last_index]
        
        return self.df_results
    
    def full_analysis(self, df):
        '''
        Wykonuje pełną analizę - wszystkie po kolei
        '''
        self.prepare_df()
        self.df_results = self.calc_averages(df)
        self.df_results = self.search_top(df)
        self.df_results = self.age_analysis(df)
        self.df_results = self.popularity_analysis(df)

        return self.df_results
    

class RecommendationPlugin:
    '''
    Klasa do rekomendacji pioseneke pomiędzy dwoma ramkami danych
    '''
    def __init__(self):
        pass

    def tag_list(self, df):
        '''
        Wyciągamy listę tagów danego df
        '''
        all_tags = []
        for tags_list in df['Tags']:
            if isinstance(tags_list, str) and pd.notna(tags_list) and tags_list.strip():
                tags = tags_list.strip("[]")
                tags = tags.split(',')
                all_tags.extend([tag.strip() for tag in tags if tag.strip()])
        tag_top_separate = pd.Series(all_tags).value_counts()
        df_tags = tag_top_separate.reset_index()
        df_tags.columns = ['Tag','Count']
        #tag_top_separate.head(10)
        #df_results.at[0,"Top tags"] = ", ".join(Tag_top_separate.head(10).keys().to_list())

        return df_tags
    
    def joint_tag_list(self, df_base, df_compare):
        '''
        Wycigąmy wspólną listę tagów dla dwóch ramek danych
        '''
        df_tags_base = self.tag_list(df_base)
        df_tags_compare = self.tag_list(df_compare)

        df_joint_tags = pd.merge(df_tags_base, df_tags_compare,
                      how='inner', on='Tag')
        df_joint_tags = df_joint_tags.assign(Common=lambda df: df.apply(lambda row: min(row['Count_x'], row['Count_y']), axis=1))
        df_joint_tags = df_joint_tags.sort_values('Common', ascending=False).drop(columns=['Count_x','Count_y'])

        return df_joint_tags
    
    def sum_common_tag(self, df, df_joint_tags):
        '''
        Sumuje wspólne tagi w utworach
        '''        
        df['Common Tag Sum'] = None
        # df['Spotify Release Date'] = None
        # unique_tracks = df[track_name_column].size

        for index, row in df.iterrows():
            tags_list = row['Tags']
            total = 0

            if isinstance(tags_list, str) and pd.notna(tags_list) and tags_list.strip():
                tags = tags_list.strip("[]").split(',')

                for tag in tags:
                    tag = tag.strip().strip("'\"") 
                    try:
                        value = df_joint_tags.query(f"Tag == \"'{tag}'\"")['Common'].values[0]
                        total = total + value
                    except:
                        value = 0       
            df.at[index, 'Common Tag Sum'] = total
        
        df = df.sort_values('Common Tag Sum', ascending=False)
        return df

    def show_recommendation(self, df_base, df_compare, numer_of_recommended=10):
        '''
        Pokazuje rekomendacje między dwoma ramkami danych
        '''
        df_joint_tags = self.joint_tag_list(df_base=df_base, df_compare=df_compare)
        
        df_base = self.sum_common_tag(df_base, df_joint_tags)
        df_compare = self.sum_common_tag(df_compare, df_joint_tags)

        df_base = create_track_artist_column(df_base)
        df_compare = create_track_artist_column(df_compare)

        # Usuń z df_base artystów, którzy są w df_compare
        df_base_recommended = df_base[~df_base['Track Artist'].isin(df_compare['Track Artist'])].head(10)
        # Usuń z df_compare artystów, którzy są w df_base
        df_compare_recommended = df_compare[~df_compare['Track Artist'].isin(df_base['Track Artist'])].head(10)

        return df_base_recommended, df_compare_recommended

