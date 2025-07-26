import pandas as pd
import os 
from pathlib import Path

input_folder = 'outputs'

def main():
    for f in os.listdir(input_folder):
        output_csv = f'{f}_output.csv'
        if not os.path.exists(output_csv):
            for csv_files in os.listdir(Path(input_folder,f)): 
                input_csv = os.path.join(input_folder, f, csv_files)
                df = pd.read_csv(input_csv)

                df.columns = df.columns.str.strip().str.replace('\r', '').str.replace('\n', '').str.replace('  ', '').str.replace(' ', '').str.strip()
                df['Etablissement'] = df['Etablissement'].str.replace('"', '').str.replace(r'\s+', ' ', regex=True).str.strip()
                df['Filiere'] = df['Filiere'].str.replace('"', '').str.replace(r'\s+', ' ', regex=True).str.strip()
                df['Min1'] = pd.to_numeric(df['Min1'], errors='coerce')
                df['Min2'] = pd.to_numeric(df['Min1'], errors='coerce')
                df['Min3'] = pd.to_numeric(df['Min1'], errors='coerce')
                
                df.drop(df.columns[df.columns.str.contains('unnamed',case = False)],axis=1, inplace=True)
                # If file is new, write header, otherwise skip header
                df.to_csv(output_csv, mode='a', index=False, header=not os.path.exists(output_csv), columns=df.columns)

if __name__ == "__main__":
    main()
