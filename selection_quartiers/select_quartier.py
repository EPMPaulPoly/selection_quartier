import psycopg2 as pg2
from sqlalchemy import create_engine,text
import pandas as pd
import geopandas as gpd
import tkinter as tk
from tkinter import simpledialog,messagebox



def select_quartier(option:int,id_column:str,description_column:str,input_option:int = 1,**kwargs)->int:
    '''# select_quartier
        Fonction qui permet de choisir un quartier\\
        Inputs:\\
            - option: permet de donner une option sur quel type d'input est fourni\\
            - id_column: colonne contenant l'identifiant du quartier\\
            - description_column: column name containing the relevant description of the analysis zone \\
            - input_option: 1: command line 2: tkinter window\\
        kwargs option 1:\\
            - db_login: string de login de la base de données\\
            - db_table_name: nom de la table de la base de données à lire pour les quartiers d'analyse \\
            - db_schema: schema in which table is located\\
        kwargs option 2:\\
            - geojson_file_location: geojson file to open in case of file based information
    '''
    db_login = kwargs.get("db_login",None)
    db_table_name = kwargs.get("table_name",None)
    db_schema = kwargs.get("schema_name","public")
    geojson_file_location = kwargs.get("geojson_location",None)
    
    match option:
        case 1:
            #option 1 on va le chercher dans la base de données
            command = f'SELECT "{id_column}", "{description_column}", geometry FROM {db_schema}.{db_table_name}'
            engine = create_engine(db_login)
            with engine.connect() as con:
                data:gpd.GeoDataFrame = gpd.read_postgis(command,con=engine,geom_col="geometry")
        case 2: 
            data:gpd.GeoDataFrame = gpd.read_file(geojson_file_location)
    
    valid_ids = data[id_column].unique().tolist()
    string = "Liste des quartiers dans la selection\n"
    for _,row in data.iterrows():
        string = f"{string}ID = {row[id_column]:2d} - Quartier = {row[description_column]}\n"
    if input_option == 1:
        print(string)
        invalid_answer = True
        while invalid_answer:   
            region_to_analyse = int(input("Quel quartier voulez vous analyser?"))
            if region_to_analyse in valid_ids:
                string2 = f'Vous avez choisi: ID = {data.loc[data[id_column] == region_to_analyse,id_column].values[0]:2d} - Quartier = {data.loc[data[id_column] == region_to_analyse,description_column].values[0]} '
                print(string2)
                print("Entrée valide - fin de la selection")
                invalid_answer = False
            else:
                print("Entrée invalide veuillez rentrer un quartier valide")
    elif input_option ==2:
        string =f'{string}Quel quartier voulez vous analyser?'
        ROOT = tk.Tk()
        ROOT.withdraw()
        # the input dialog
        invalid_answer = True
        while invalid_answer: 
            try:
                region_to_analyse = int(simpledialog.askstring(title="Choix de ville",prompt=string))
            except:
                messagebox.showerror("Erreur", "Entrez une ville valide")
                continue
            if region_to_analyse in valid_ids:
                string2 = f'Vous avez choisi: ID = {data.loc[data[id_column] == region_to_analyse,id_column].values[0]:2d} - Quartier = {data.loc[data[id_column] == region_to_analyse,description_column].values[0]} '
                messagebox.showinfo('Sélection complétée',string2)
                invalid_answer = False
            else:
                messagebox.showerror("Erreur", "Entrez une ville valide")
    return region_to_analyse

if __name__ =="__main__":
    #variables a modifier:
    pg_host = 'localhost' #defaut localhost
    pg_port = '5432' #defaut 5432
    pg_dbname = 'parking_regs_test'# specifique a l'application
    pg_username = 'postgres' # defaut postgres
    pg_password = 'admin' # specifique a l'application
    pg_schemaname = 'public' #defaut public
    pg_bin_path = '/Applications/Postgres.app/Contents/Versions/13/bin/' # specifique a l'application
    pg_srid = '32187' #defaut 32188
    #variables derivees
    pg_string = 'postgresql://' + pg_username + ':'  + pg_password + '@'  + pg_host + ':'  + pg_port + '/'  + pg_dbname
    entier_a_renvoyer = select_quartier(1,"ID","NOM",2,db_login=pg_string,db_schema="public",table_name="sec_analyse")
    print(entier_a_renvoyer)


 