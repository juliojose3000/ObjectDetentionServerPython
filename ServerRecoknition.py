# Imports Modules
import socket
import csv
import boto3
import json
import base64
import pyperclip as clipboard

OBJECT_AND_SCENE_DETENTION = 'object_and_scene_detention'
FACIAL_ANALYSIS = 'face_analysis'
SHOPPING = 'shopping'
IMAGE_MODERATION = 'image_moderation'

INVENTARIO = {'Carrot': 500, 'Watermelon': 600, 'Potato': 200, 'Avocado': 1000, 'Orange': 300, 'Banana': 200,
              'Apple': 100, 'Pineapple': 1500, 'Pear': 350,'Grapes':50}

NA_PRODUCTS = ['Fruit','Plant','Food','Citrus Fruit']

# Main
while True:

    print(
        '\n-------------------------------------------------\nEsperando imagenes para analizar...\n------------------------------------------------\n')

    # Defines Server Values
    listensocket = socket.socket()
    PORT = 7000
    HOST = "192.168.1.14"

    maxConnections = 10

    listensocket.bind((HOST, PORT))

    # Opens Server
    listensocket.listen(maxConnections)

    # Accepts Incomming Connection
    (clientsocket, address) = listensocket.accept()

    decodeImage = ''

    messageFromMobile = clientsocket.recv(50000).decode().split('.')

    imageBase64BitsParts = int(messageFromMobile[1])

    option = messageFromMobile[0]

    #print('cantidad de partes = ' + str(imageBase64BitsParts))

    for stringBase64Part in range(imageBase64BitsParts):
        data = clientsocket.recv(24900)  # 24.9 kilobyte

        dataStr = json.dumps(data.decode()).replace('"', '')

        decodeImage += dataStr

    clipboard.copy(decodeImage)

    #print("Imagen copiada al portapapeles")

    print('Imagen recibida\n')

    # ------------------------------------------------------------------------------------------------------------------#

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

    source_bytes = imgdata  # convertimos la imagen a bytes

    # ------------------------------------------------------------------------------------------------------------------#

    if option == SHOPPING:

        amount_payment = 0

        response = client.detect_labels(Image={'Bytes': source_bytes},
                                        MaxLabels=10,
                                        MinConfidence=50)

        print("\nCOMPRA REALIZADA POR EL CLIENTE: ")
        for value in response['Labels']:

            product = str(value['Name'])
            confidence = str(value['Confidence'])[:5]

            if product in INVENTARIO:
                amount_payment += INVENTARIO[product]
                # print(product + " ----- " + confidence+ ' ----- '+str(INVENTARIO[product])+' colones')
                print(product + " ----- " + str(INVENTARIO[product]) + ' colones')
            elif product not in NA_PRODUCTS:
                # print(product + " ----- " + confidence)
                print(product + " ----- NOT REGISTERED")

        print('Total de la compra: ' + str(amount_payment) + ' colones')

    # ------------------------------------------------------------------------------------------------------------------#

    elif option == FACIAL_ANALYSIS:

        response = client.detect_faces(Image={'Bytes': source_bytes}, Attributes=['ALL'])

        total_hapiness = 0

                    #  0      1         2         3        4           5         6     7
        emotions = ['CALM','ANGRY','DISGUSTED','HAPPY','CONFUSED','SURPRISED','FEAR','SAD']

        emotion_to_test = emotions[3]

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

                        if(str(emotion['Type'])==str(emotion_to_test)):
                            total_hapiness+=emotion['Confidence']

                        print('\t' + str(emotion['Type']) + ' -------------- ' + str(emotion['Confidence']))

        print('\nTOTAL '+str(emotion_to_test)+': '+str(total_hapiness))
    # ------------------------------------------------------------------------------------------------------------------#

    elif option == OBJECT_AND_SCENE_DETENTION:

        response = client.detect_labels(Image={'Bytes': source_bytes},
                                        MaxLabels=10,
                                        MinConfidence=50)

        print("\nObjetos y descripcion de la escena: ")
        for value in response['Labels']:
            product = str(value['Name'])
            confidence = str(value['Confidence'])[:5] + '%'
            print(product + " ----- " + confidence)

    # ------------------------------------------------------------------------------------------------------------------#

    elif option == IMAGE_MODERATION:

        response = client.detect_moderation_labels(Image={'Bytes': source_bytes})

        print('\nDescripción de la imágen:')

        for item in response['ModerationLabels']:
            print('\t'+item['Name']+' ----- '+str(item['Confidence'])[:5]+'%')

    # -------------------------------------------------------------------------------------------------------------------#

    clientsocket.close()
