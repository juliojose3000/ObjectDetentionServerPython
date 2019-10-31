#Imports Modules
import socket
import csv
import boto3
import json
import base64
import pyperclip as clipboard

#Main
while True:

    print('Esperando imagenes para analizar...\n')

    #Defines Server Values
    listensocket = socket.socket()
    PORT = 7000
    HOST = "192.168.1.16" #local host

    maxConnections = 999
    IP = socket.gethostname()
    IP = socket.gethostname() #Gets Hostname Of Current Macheine

    listensocket.bind((HOST,PORT))

    #Opens Server
    listensocket.listen(maxConnections)

    #Accepts Incomming Connection
    (clientsocket, address) = listensocket.accept()

    decodeImage = ''

    parts = int(clientsocket.recv(50000).decode())

    print('cantidad de partes = ' + str(parts))

    for x in range(parts):

        data = clientsocket.recv(24900) #24.9 kilobyte

        dataStr = json.dumps(data.decode()).replace('"','')

        decodeImage += dataStr

    #-------------------------------------------------

    clipboard.copy(decodeImage)

    print("Imagen copiada al portapapeles")

    #------------------------------------------------------------------------------------------------------------------#

    with open('credentials.csv', 'r') as input:
        next(input)
        reader = csv.reader(input)
        for line in reader:
            access_key_id = line[2]
            secret_access_key = line[3]

    client = boto3.client('rekognition',
                          aws_access_key_id=access_key_id,
                          aws_secret_access_key=secret_access_key,
                          region_name='us-west-2')

    imgdata = base64.b64decode(decodeImage)

    source_bytes = imgdata # convertimos la imagen a bytes

    response = client.detect_labels(Image={'Bytes': source_bytes},
                                    MaxLabels=10,
                                    MinConfidence=50)

    print("\nDescripcion de la imagen recibida: ")
    for value in response['Labels']:
        print(str(value['Name']) + "      " + str(value['Confidence']))

    print("\n---------------------------------------")

    #------------------------------------------------------------------------------------------------------------------#

    clientsocket.close()