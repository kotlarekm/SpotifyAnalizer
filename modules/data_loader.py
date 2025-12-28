import pandas as pd
from Plugins.DataProcess import WrappedListProcess
from dotenv import load_dotenv
import os
from datetime import datetime
import pandas as pd

from pathlib import Path

analyser_path = Path(os.getcwd()).resolve()

def load_user_file(path, filename):
    wrapped_list = WrappedListProcess()
    full_name = f"{filename}.csv"
    print(f"odczytuje plik {path} {filename}")
    return wrapped_list.process_list(
        file_name=full_name,
        data_path=analyser_path,
        input_path=path
        )

