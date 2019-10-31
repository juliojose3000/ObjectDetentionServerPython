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

    response = client.detect_faces(Image={'Bytes': source_bytes}, Attributes=['ALL'])

    for key, value in response.items():
        if key == 'FaceDetails':
            for people_att in value:
                print('\nDescripción de la persona: ')
                print('Rango de edad: '+str(people_att['AgeRange']))
                print('Está sonriendo? '+str(people_att['Smile']['Value']))
                print('Genero: '+str(people_att['Gender']['Value']))
                print('Tiene barba? '+str(people_att['Beard']['Value']))
                print('Tiene Bigote? ' + str(people_att['Mustache']['Value']))
                print('Emociones: ')
                for emotion in people_att['Emotions']:
                    print('\t'+str(emotion['Type']) +' -------------- '+str(emotion['Confidence']))


                print("====================================================")

    print("\n---------------------------------------")

    #------------------------------------------------------------------------------------------------------------------#

    clientsocket.close()