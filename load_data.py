import json
import pandas as pd
import os
from sys import platform

# Find the path based on the system (only tested on windows and ubuntu)
seperator = "/"
if platform == "win32":
    seperator = "\\"

file_path = os.path.realpath(__file__)
local_path = seperator.join(file_path.split(seperator)[:-1]) + seperator

# Load election data
valg_raw = pd.read_csv(local_path+'Dataset' + seperator + "Election_raw.csv")
valg_percent = pd.read_csv(local_path + 'Dataset' + seperator + 'Election_percentage.csv')

# Load data
car_data = pd.read_csv(local_path + 'Dataset' + seperator + 'Biler.csv')
population_data = pd.read_csv(local_path + 'Dataset' + seperator + 'BefolkningsTilvækst.csv')
education_data = pd.read_csv(local_path + 'Dataset' + seperator + 'Education.csv')
salary_data = pd.read_csv(f"{local_path}Dataset{seperator}Salary.csv")
unemployment_data = pd.read_csv(f"{local_path}Dataset{seperator}Unemployed.csv")
crime_data = pd.read_csv(f"{local_path}Dataset{seperator}Crime.csv")
alder_data = pd.read_csv(f"{local_path}Dataset{seperator}Alder.csv")

# Load geoJSON
kommuner_path = local_path + "Dataset" + seperator + "kommuner_geojson.json"
kommuner_geojson = json.load(open(kommuner_path, 'r', encoding='utf-8'))

carto_path = local_path + "Dataset" + seperator + "cartogram.json"
carto_geojson = json.load(open(carto_path, 'r', encoding='utf-8'))

# Load age data
