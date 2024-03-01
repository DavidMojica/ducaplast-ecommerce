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
logRoute = "C:\\Users\\swan5\\Desktop\\universidad\\projects\\works\\Ducaplast\\extras\\productosETL\\log.txt"
descripciones_vacias = 0
referencias_vacias = 0
precios_vacios = 0

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
        logs_proceso.append(f"ACENTO ELIMINADO de {palabra} : {removidos}. Fila: {contador+1}")
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
        print("Error cargando la tabla: ", error)

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

            #Remover acentos
            eliminar_acentos(descripcion, contador)
            eliminar_acentos(referencia_fabrica, contador)
            
            #Datos extraños.Nombres que son numeros
            descripcion, result = tryParse(descripcion, float)
            if result:
                logs_proceso.append(f"CUIDADO: La descripción es un número, no una descripcion. Fila {contador+1}")
                descripciones_extranas += 1
            referencia_fabrica, result = tryParse(referencia_fabrica, float)
            if result:
                logs_proceso.append(f"CUIDADO: La referencia de fabrica es un numero. Fila {contador+1}")
                referencias_extranas += 1
                
            
            contador += 1
    
except (Exception) as error:
    print(f"Error leyendo el archivo csv ------------> {error}")
finally:
    if(connection):
        connection.close()
        print(f"Conexion con la base de datos {v_database} cerrada.")
        
with open(logRoute, "w") as File:
    File.write("")
    File.write(f"|-------------------ANALISIS RESULTANTE DE LA EXTRACCION DE DATOS--------------|\nDescripciones vacías: {descripciones_vacias}\nReferencias vacías: {referencias_vacias}\nPrecios vacíos: {precios_vacios}\nPrecios en 0: {precios_en_0}\nDescripciones extrañas: {descripciones_extranas}\nReferencias extrañas: {referencias_extranas}\nAcentos removidos: {acentos_removidos}")
