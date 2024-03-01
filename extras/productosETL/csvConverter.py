import pandas as pd

ruta_archivo_xlsx = "C:\\Users\\swan5\\Desktop\\universidad\\projects\\works\\Ducaplast\\extras\\productosETL\\prod.xlsx"
ruta_archivo_csv = "C:\\Users\\swan5\\Desktop\\universidad\\projects\\works\\Ducaplast\\extras\\productosETL\\productos_final.csv"

converters = {
    "DESCRIPCIÓN": lambda x: x.replace("'", "").replace('"', ''),
    "REFERENCIA DE FÁBRICA": lambda x: x.replace("'", "").replace('"', '')
}
data_frame = pd.read_excel(ruta_archivo_xlsx,converters=converters)

data_frame = data_frame.applymap(lambda x: ' '.join(x.split()) if isinstance(x, str) else x)

data_frame.to_csv(ruta_archivo_csv, sep='|', index=False, header=False)
print("Hecho!")
