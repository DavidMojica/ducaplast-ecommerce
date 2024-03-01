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

datos_vacios = []
precios_0 = []
datos_extranos = []
acentos_rem = []

logRoute = "C:\\Users\\swan5\\Desktop\\universidad\\projects\\works\\Ducaplast\\extras\\productosETL\\log.txt"
data_vacia = 0

precios_en_0 = 0

descripciones_extranas = 0
referencias_extranas = 0

acentos_removidos = 0

def tryParse(dato, tipo_dato):
    #dato = dato.replace('"','') <----Eliminar '"' no es necesario ahora que construimos un programa para exportar
    try:
        return tipo_dato(dato), True
    except (ValueError, TypeError):
        return dato, False


#Elimina las letra que contengan acentos
def eliminar_acentos(palabra, contador):
    acentos = {"á": "a", "é": "e", "í": "i", "ó": "o", "ú": "u", "Á": "A", "É": "E", "Í": "I", "Ó":"O", "Ú":"U"}
    palabra_nueva = ""
    ban = False
    removidos = []
    for letra in palabra:
        if letra in acentos:
            palabra_nueva += acentos[letra]
            removidos.append(letra)
            ban = True
        else:
            palabra_nueva+=letra
    
    if ban:
        acentos_rem.append(f"ACENTO ELIMINADO de {palabra} : {removidos}. Fila: {contador+1}")
        global acentos_removidos
        acentos_removidos+=1
    return palabra_nueva
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
#Cargar tabla
#--------------------------------------------------------------------------------------------------------------- 
def cargarTablaProductos(connection, cursor, contador, descripcion, referencia_fabrica ,precio):
    print(f"Cargando producto... -> {descripcion} registro #{contador+1}")
    cantidad = 0
    try:
        command = '''INSERT INTO main_producto(descripcion, referencia_fabrica, precio, cantidad) VALUES(%s, %s, %s, %s)'''
        cursor.execute(command, (descripcion, referencia_fabrica, precio, cantidad))
        connection.commit()
    except(Exception) as error:
        print(f"Error cargando la tabla: {error}, {contador}, {descripcion}, {referencia_fabrica}, {precio}")

#---------------------------------------------------------------------------------------------------------------
#Limpieza de tablas 
#---------------------------------------------------------------------------------------------------------------
command = '''TRUNCATE main_producto CASCADE'''
cursor.execute(command)
command = '''ALTER SEQUENCE main_producto_id_seq RESTART WITH 1'''
cursor.execute(command)

#---------------------------------------------------------------------------------------------------------------
#Abrir el archivo CSV de los datos
#---------------------------------------------------------------------------------------------------------------
try:
    archivo = "C:\\Users\\swan5\\Desktop\\universidad\\projects\\works\\Ducaplast\\extras\\productosETL\\productos_final.csv"
    with io.open(archivo, encoding=('utf-8')) as File:
        reader = csv.reader(File, delimiter='|', quotechar=(','), quoting=csv.QUOTE_MINIMAL)
        contador = 0
        registro = 0
        for row in reader:
            descripcion = row[0].strip()
            referencia_fabrica = row[1].strip()
            precio = row[2].strip()
            if precio.endswith('.0'):
                precio = precio[:-2]  # Eliminar los dos últimos caracteres

            
            #Verificar espacios vacíos
            if descripcion == "" or referencia_fabrica == "" or precio == "":
                datos_vacios.append(f"Datos vacíos en fila {registro+1}")
                data_vacia += 1
            else:
                #Verificar que el precio no sea 0
                if precio == 0 or precio == "0":
                    precios_0.append(f"PRECAUCION: El precio es 0 en fila {registro+1}")
                    precios_en_0 += 1

                #Remover acentos
                eliminar_acentos(descripcion, registro+1)
                eliminar_acentos(referencia_fabrica, registro+1)
                #Datos extraños.Nombres que son numeros
                descripcion, result = tryParse(descripcion, float)
                if result:
                    datos_extranos.append(f"CUIDADO: La descripción es un número, no una descripcion. Fila {registro+1}")
                    descripciones_extranas += 1
                referencia_fabrica, result = tryParse(referencia_fabrica, float)
                if result:
                    datos_extranos.append(f"CUIDADO: La referencia de fabrica es un numero. Fila {registro+1}")
                    referencias_extranas += 1
                    
                cargarTablaProductos(connection, cursor, contador, descripcion, referencia_fabrica, precio)
                contador += 1

            registro += 1
except (Exception) as error:
    print(f"Error leyendo el archivo csv ------------> {error}")
finally:
    if(connection):
        connection.close()
        print(f"Conexion con la base de datos {v_database} cerrada.")
        
with open(logRoute, "w", encoding='utf-8') as File:
    File.write("")
    File.write(f"|-------------------ANALISIS RESULTANTE DE LA EXTRACCION DE DATOS--------------|\nDescripciones vacías: {data_vacia}\nPrecios en 0: {precios_en_0}\nDescripciones extrañas: {descripciones_extranas}\nReferencias extrañas: {referencias_extranas}\nAcentos removidos: {acentos_removidos}")
    File.write("\n"+"---------FILAS VACIAS-------"+"\n")
    for vacio in datos_vacios:
        File.write(vacio +"\n")
    
    File.write("---------PRECIOS EN 0-------"+"\n")
    for precio in precios_0:
        File.write(precio +"\n")
        
    File.write("---------DATOS EXTRAÑOS-------"+"\n")
    for dato in datos_extranos:
        File.write(dato +"\n")

    File.write("---------Acentos retirados-------"+"\n")
    for acento in acentos_rem:
        File.write(acento +"\n")
    File.write("Fin del reporte")
    
tiempo_final = time.time()
tiempo_total_transcurrido = tiempo_final - tiempo_inicial
tiempo_dos_decimales = round(tiempo_total_transcurrido, 2)

print(f"Fin del proceso ETL.\nTiempo de ejecucion: {tiempo_dos_decimales} segundos.")