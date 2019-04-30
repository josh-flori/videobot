#https://googlecloudplatform.github.io/google-cloud-python/latest/vision/gapic/v1/api.html
#export GOOGLE_APPLICATION_CREDENTIALS='/users/josh.flori/downloads/Reddit Vision-a52010045078.json'
#pip install --upgrade google-cloud


import requests
import cv2
from google.cloud import vision
from google.cloud.vision import types
import io
import os
import sys

def get_image_data(urls):
    i=0
    text_list=[]
    # loop through posts
    for url in urls:
        
        r = requests.get(url[0], allow_redirects=True)
        path='/users/josh.flori/desktop/memes/'+str(i)+'.jpg'
        if ".gif" not in url:
            open(path, 'wb').write(r.content)     
        else:
            print('gif found, oh no.')
            sys.exit()
        i+=1

        # Performs label detection on the image file. Returns stuff like "face, head, water, girl, car" and confidence labels
        def get_image_text(image_path):
            """Detects text in the file."""
            from google.cloud import vision
            client = vision.ImageAnnotatorClient()
            with io.open(image_path, 'rb') as image_file:
                content = image_file.read()
            image = vision.types.Image(content=content)
            response = client.text_detection(image=image)
            texts = response.text_annotations
            return texts
        
        text_list.append(get_image_text(path)[0].description)
        
    return(text_list)
        