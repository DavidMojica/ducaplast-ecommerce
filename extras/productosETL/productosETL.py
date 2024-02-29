# -*- coding: utf-8 -*-
import sys
import csv
import time
import psycopg2
import io
# Variables globales
error_con = False
# Parámetros de conexión de la Base de datos local
v_host       = "localhost"
v_port       = "5432"
v_database = "ducaplast"
v_user       = "postgres"
v_password = "12345"

logs_proceso = []
descripciones_vacias = 0
referencias_vacias = 0
precios_vacios = 0
precios_en_0 = 0
#---------------------------------------------------------------------------------------------------------------
#CONEXIÓN A BD
#---------------------------------------------------------------------------------------------------------------
tiempo_inicial = time.time()
try:
    connection = psycopg2.connect(user= v_user, password=v_password, host= v_host,
                                  port= v_port, database= v_database)
    cursor = connection.cursor()
    cursor.execute("SELECT version();")
    record = cursor.fetchone()
    print("Estás conectado a - ", record, "\n")
except (Exception) as error:
    print("Error: ", error)
    error_con = True
finally:
    if (error_con):
        sys.exit("Error de conexión con servidor PostgreSQL")

#---------------------------------------------------------------------------------------------------------------
#Limpieza de tablas 
#---------------------------------------------------------------------------------------------------------------
command = '''TRUNCATE main_producto'''
cursor.execute(command)

#---------------------------------------------------------------------------------------------------------------
#Abrir el archivo CSV de los datos
#---------------------------------------------------------------------------------------------------------------
try:
    archivo = "C:\\Users\\swan5\\Desktop\\universidad\\projects\\works\\Ducaplast\\extras\\productosETL\\productos_final.csv"
    with io.open(archivo, encoding=('utf-8')) as File:
        reader = csv.reader(File, delimiter='|', quotechar=(','), quoting=csv.QUOTE_MINIMAL)
        contador = 0
        for row in reader:
            descripcion = row[0].strip()
            referencia_fabrica = row[1].strip()
            precio = row[2].strip()
            
            #Verificar espacios vacíos
            if descripcion == "":
                logs_proceso.append(f"Descripcion vacía en la fila {contador+1}")
                descripciones_vacias += 1
            if referencia_fabrica == "":
                logs_proceso.append(f"Referencia de fábrica vacía en la fila {contador+1}")
                referencias_vacias += 1
            if precio == "":
                logs_proceso.append(f"Precio está vacío en la fila {contador+1}")
                precios_vacios += 1

            #Verificar que el precio no sea 0
            if precio == 0 or precio == "0":
                logs_proceso.append(f"PRECAUCION: El precio es 0 en fila {contador+1}")
                precios_en_0 += 1

            


except (Exception) as error:
    print(f"Error leyendo el archivo csv ------------> {error}")
finally:
    if(connection):
        connection.close()
        print(f"Conexion con la base de datos {v_database} cerrada.")