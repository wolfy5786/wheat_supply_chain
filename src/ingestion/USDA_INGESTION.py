import pandas as pd
import os
from dotenv import load_dotenv
import common_ingestion

#USDA dataset comprises of Wheat Export data from Unitedt States to various Partner Countries
def load_esr_data(base_url = "https://api.fas.usda.gov"):
    commodiy_code = 107     #       'All Wheat' refer notebooks for exploring APIs, measured in metric Tons
    load_dotenv(dotenv_path=".env")
    USDA_PSD_API_KEY = os.getenv("USDA_PSD_API_KEY")
    headers = {
    "X-Api-Key" : USDA_PSD_API_KEY
    }
    #first we fetch the partner Countries
    query = "/api/esr/countries"
    url = base_url + query
    country_data = common_ingestion.fetch_data(url=url, headers= headers)
    if country_data == "":
        print("some unexpected error occured")
        return
    #the fetched data is an array of objects in JSON format, refer Exploring APIs
    country_data = pd.DataFrame(country_data)

    #We are performing analysis from 2012 to 2024
    query = "/api/esr/exports/commodityCode/107/allCountries/marketYear/20"
    
    for i in range(2,24):
        if i<=10:
            j = i + 10
        else:
            j = i
        squery = query + str(j)
        url = base_url + squery
        data = common_ingestion.fetch_data(url=url, headers= headers)
        if data == "":
            print("some error occured")
            return
        if i==2:
            wheat_exports = pd.DataFrame(data)
        
        wheat_exports = pd.concat([wheat_exports, pd.DataFrame(data)],ignore_index=True, axis=0)
    
    print(country_data.head())
    print(wheat_exports.head(),wheat_exports.tail())

    file_path_country_codes = "data/raw/USDA_ESR_countryCodes.csv"
    file_path_wheat_exports = "data/raw/USDA_ESR_wheatExports.csv"
    country_data.to_csv(file_path_country_codes, index=False)
    
    #save in batchess
    batch_size = 10000  # rows per batch
    for i in range(0, len(wheat_exports), batch_size):
        batch = wheat_exports.iloc[i:i + batch_size]
        
        batch.to_csv(
            file_path_wheat_exports,
            mode='w' if i == 0 else 'a',  # overwrite first, append rest
            header=(i == 0),
            index=False
        )

#the Gats Dataset comprises of Import, Export & Ree\Export Data of various commodities
def load_GATS_data(base_url = "https://api.fas.usda.gov"):
    load_dotenv(dotenv_path=".env")
    USDA_PSD_API_KEY = os.getenv("USDA_PSD_API_KEY")
    header = {
    "X-Api-Key" : USDA_PSD_API_KEY
    }

    #hs10 Commodities
    query = "/api/gats/commodities"
    url = base_url + query
    df = common_ingestion.fetch_data(url=url, headers=header)
    #the df contain various commodities we must filter out wheat
    #many wheat commodities start with 1001 refer API explorations
    wheat_df = df[df["hS10Code"].astype(str).str.startswith("1001")]

    query = "/api/gats/unitsOfMeasure"
    url = base_url + query
    unit_of_measure = common_ingestion.fetch_data(url=url, headers=header)
    unit_of_measure = pd.DataFrame(unit_of_measure)

    #for import, export and re-export, we need to to call the for each country! 
     