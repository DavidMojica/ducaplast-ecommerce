import pandas as pd

ruta_archivo_xlsx = "unificado_sin_cabecera.xlsx"
ruta_archivo_csv = "unificado_final.csv"

data_frame = pd.read_excel(ruta_archivo_xlsx)
data_frame.to_csv(ruta_archivo_csv, sep='|', index=False)
