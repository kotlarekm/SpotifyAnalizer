import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

from dotenv import load_dotenv
import os

import pandas as pd
import requests
import numpy as np

import seaborn as sns
import matplotlib.pyplot as plt
import scipy.stats as sps

import json
from openai import OpenAI
import re

import tempfile
import librosa
import yt_dlp

from datetime import datetime
from pathlib import Path

from Plugins.Utils import create_track_artist_column

load_dotenv("log_data.env")

class OpenAIPlugin:
    '''
    Klasa do zapytań OpenAI
    '''
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=self.api_key)

    def askOpenAI(self, prompt, model = "gpt-4.1-nano", temperature = 0.7):
        try:       
            response = self.client.chat.completions.create(
                model= model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_completion_tokens=700
            )

            result = response.choices[0].message.content
        except Exception as e:
            result =f"error: " + str(e)

        return result

    def SingleUserQuestion(self, df):

        json_data = df.to_json(orient="records", force_ascii=False)

        prompt =(
            "Jesteś krytykiem muzycznym i analitykiem gustu muzycznego."

            "Na podstawie danych użytkownika (historia odsłuchów / preferencje),"
            "napisz krótki komentarz (3–5 zdań) opisujący jego gust muzyczny."

            "Skup się na:"
            "- dominujących gatunkach i nastrojach"
            "- stopniu mainstreamowości vs alternatywy"
            "- energii / emocjach"
            "- ewentualnych kontrastach w gustach"

            "Dane (JSON):"
            f"{json_data}"
            "Nie opisuj danych wprost."
            "Wyciągaj wnioski i uogólnienia."
        )

        result = self.askOpenAI(prompt=prompt)

        return result
    
    def TwoUsersQuestion(self, df, df_compare):

        json_data_base = df.to_json(orient="records", force_ascii=False)
        json_data_compare = df_compare.to_json(orient="records", force_ascii=False)
        prompt =(
            "Jesteś krytykiem muzycznym i analitykiem gustu muzycznego."

            "Na podstawie danych dwóch użytkowników (historia odsłuchów / preferencje),"
            "napisz krótki komentarz (3–5 zdań) porównujący ich gust muzyczny."

            "Skup się na:"
            "- dominujących gatunkach i nastrojach"
            "- stopniu mainstreamowości vs alternatywy"
            "- energii / emocjach"
            "- ewentualnych kontrastach w gustach"
            "- Na ile są do siebie podobni"

            "Dane (JSON) pierwszego użytkownika:"
            f"{json_data_base}"

            "Dane (JSON) drugiego użytkownika:"
            f"{json_data_compare}"            
            "Nie opisuj danych wprost."
            "Wyciągaj wnioski i uogólnienia."
        )

        result = self.askOpenAI(prompt=prompt)

        return result

    def UserGlobalQuestion(self, df, df_compare):

        json_data_base = df.to_json(orient="records", force_ascii=False)
        json_data_compare = df_compare.to_json(orient="records", force_ascii=False)
        prompt =(
            "Jesteś krytykiem muzycznym i analitykiem gustu muzycznego."

            "Na podstawie danych (historia odsłuchów / preferencje) użytkownika i preferencji globalnych,"
            "napisz krótki komentarz (3–5 zdań) porównujący gust użytkownika względem ogółu."

            "Skup się na:"
            "- dominujących gatunkach i nastrojach"
            "- stopniu mainstreamowości vs alternatywy"
            "- energii / emocjach"
            "- ewentualnych kontrastach w gustach"
            "- Na ile są do siebie podobni"

            "Dane (JSON) pierwszego użytkownika:"
            f"{json_data_base}"

            "Dane (JSON) globalne:"
            f"{json_data_compare}"  
                      
            "Nie opisuj danych wprost."
            "Wyciągaj wnioski i uogólnienia."
        )

        result = self.askOpenAI(prompt=prompt)

        return result