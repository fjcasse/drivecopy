import pydrive2
import json
import csv
import os.path 

from os import path
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

gauth = GoogleAuth()
gauth.LocalWebserverAuth() # Creates local webserver and auto handles authentication.

drive = GoogleDrive(gauth) # Create GoogleDrive instance with authenticated GoogleAuth instance

archivoDestino = open('origenDestino.csv', "w")
archivoDestino.close()

#CrearCarpeta Backup
#Guardar el id de Carpeta Backup de destino.
#if file_list = 'start'
# parentid = idbackupdestino


#Defino funcion para crear carpeta de Backup y me devuelva su id.
def crearCarpeta(titulo,origen):
  archivoDestino = open('origenDestino.csv', "a")
  foldertitle = '%s' % titulo
  filetype = "application/vnd.google-apps.folder"
  folder_metadata = { 'title' : foldertitle, 'mimeType' : filetype }
  folder = drive.CreateFile(folder_metadata)
  folder.Upload()
  folderid = folder['id']
  archivoDestino.write('%s,%s\n' % (origen,folderid))
  archivoDestino.close()
  return folderid

file_list = 'start'


#declaro funcion
def copiarsubarchivos():
  with open('origenDestino.csv', 'r') as file:
    csvreader = csv.reader(file)
    for row in csvreader:
      if row[0] != 'start':
        query = drive.ListFile({'q': f"'{row[0]}' in parents and trashed=false"}).GetList()
        for archivito in query:
          if archivito["mimeType"] != "application/vnd.google-apps.folder":
            archivito.Copy(target_folder={"id":row[1]})
          else:
            print("skip es una carpeta")

      
  #abrir csv en modo read
  #bucle de lectura del csv
    #leo linea, tomo parent old
    #hago una query que me devuelva los archivos de parent old
    #abro for archivito en query
      #archivito.copy con id destino parentnew(row1)



def listarCarpetasCompartidas(file_list):
  nombredearchivo = '%s.csv' % (file_list)
  #Creamos archivo CSV
  archivo = open('%s.csv' % (file_list), "w")
  #Controlamos si hacemos query a sharedwithMe u otra Carpeta.
  if file_list == 'start':
    idcarpetaraiz = crearCarpeta('BackupRestore', file_list)
    file_list = drive.ListFile({'q': f"sharedWithMe=true and trashed=false"}).GetList()
  else:
    file_list = drive.ListFile({'q': f"'{file_list}' in parents and trashed=false"}).GetList()
  #Iteramos la query para escribir el archivo
  for file1 in file_list:
    if file1["parents"] != []:
      parentid = file1["parents"][0]["id"]
      archivo.write('%s,%s,%s,%s\n' % (file1["title"], file1["id"], file1["mimeType"], parentid))
    elif file1["parents"] == [] and file1["mimeType"] != "application/vnd.google-apps.folder":
      file1.Copy(target_folder={"id":idcarpetaraiz})
    else:
      archivo.write('%s,%s,%s,%s\n' % (file1["title"], file1["id"], file1["mimeType"], file1["parents"]))
  archivo.close()
  archivo = open(nombredearchivo, "r")
  csvreader = csv.reader(archivo)
  for row in csvreader:
    while row != '':
      if row[2] == 'application/vnd.google-apps.folder':
        newfolder = crearCarpeta(row[0],row[1])
        a = open('origenDestino.csv', "r")
        acsv = csv.reader(a)
        for n in acsv:
          print(n)
          while n[0] == row[3]:
            query = drive.CreateFile({'id': f'{newfolder}', 'parents' : [{'id': n[1]}]})
            query.Upload()
            break
          while row[3] == '[]':
            query = drive.CreateFile({'id': f'{newfolder}', 'parents' : [{'id': idcarpetaraiz}]})
            query.Upload()
            break
        listarCarpetasCompartidas(row[1])
      break


listarCarpetasCompartidas(file_list)
copiarsubarchivos()