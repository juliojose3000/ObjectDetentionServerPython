#Imports Modules
import socket
import csv
import boto3
import json
import base64
import pyperclip as clipboard

OBJECT_AND_SCENE_DETENTION = '1'
FACIAL_ANALYSIS = '0'

#Main
while True:

    print('-------------------------------------------------\nEsperando imagenes para analizar...\n----------------------------------------------')

    #Defines Server Values
    listensocket = socket.socket()
    PORT = 7000
    HOST = "192.168.1.16"

    maxConnections = 10

    listensocket.bind((HOST,PORT))

    #Opens Server
    listensocket.listen(maxConnections)

    #Accepts Incomming Connection
    (clientsocket, address) = listensocket.accept()

    decodeImage = ''

    messageFromMobile = clientsocket.recv(50000).decode().split('.')

    imageBase64BitsParts = int(messageFromMobile[1])

    option = messageFromMobile[0]

    print('cantidad de partes = ' + str(imageBase64BitsParts))

    for stringBase64Part in range(imageBase64BitsParts):

        data = clientsocket.recv(24900) #24.9 kilobyte

        dataStr = json.dumps(data.decode()).replace('"','')

        decodeImage += dataStr

    #-------------------------------------------------#

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

    #------------------------------------------------------------------------------------------------------------------#

    if option == OBJECT_AND_SCENE_DETENTION:

        response = client.detect_labels(Image={'Bytes': source_bytes},
                                        MaxLabels=10,
                                        MinConfidence=50)

        print("\nObjetos y descripcion de la escena: ")
        for value in response['Labels']:
            print(str(value['Name']) + "      " + str(value['Confidence']))

        print("\n---------------------------------------")

    elif option == FACIAL_ANALYSIS:

        response = client.detect_faces(Image={'Bytes': source_bytes}, Attributes=['ALL'])

        for key, value in response.items():
            if key == 'FaceDetails':
                for people_att in value:
                    print('\nDescripción facial de la persona: ')
                    print('Rango de edad: ' + str(people_att['AgeRange']))
                    print('¿Está sonriendo? ' + str(people_att['Smile']['Value']))
                    print('Genero: ' + str(people_att['Gender']['Value']))
                    print('¿barba? ' + str(people_att['Beard']['Value']))
                    print('¿Bigote? ' + str(people_att['Mustache']['Value']))
                    print('Emociones: ')
                    for emotion in people_att['Emotions']:
                        print('\t' + str(emotion['Type']) + ' -------------- ' + str(emotion['Confidence']))

    #------------------------------------------------------------------------------------------------------------------#

    clientsocket.close()