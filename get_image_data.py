#https://googlecloudplatform.github.io/google-cloud-python/latest/vision/gapic/v1/api.html

#export GOOGLE_APPLICATION_CREDENTIALS='/users/josh.flori/downloads/Reddit Vision-a52010045078.json'

#pip install --upgrade google-cloud

import praw
import requests
import cv2
from google.cloud import vision
from google.cloud.vision import types
import io
import os

def get_image_data(subreddit,limit):
#
    ############################
    # DEFINE REDDIT CONNECTION #
    ############################
    reddit = praw.Reddit(client_id='eZ0qCk4LGFmlvg',
                         client_secret= 'ObVykPZwUf6AtmvQyh-HFIlhn8I',
                         user_agent= 'myApp',
                         username= '',
                         password= '')
#
    ##################
    #  DO THE STUFF  #
    ##################
    submissions = reddit.subreddit("memes").top("day",limit=limit)
#
    i=0
    text_list=[]
    # loop through posts
    for submission in submissions:
        url = submission.url
        r = requests.get(url, allow_redirects=True)
        path='/users/josh.flori/desktop/demo1/'+str(i)+'.jpg'
        print(url)
        if ".gif" not in url:
            open(path, 'wb').write(r.content)     
        i+=1
#
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
            print(texts[0].description)
        #
        get_image_text(path)
        
        
        
        
        
        
get_image_data('memes',2)