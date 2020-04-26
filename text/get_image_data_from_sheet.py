#https://googlecloudplatform.github.io/google-cloud-python/latest/vision/gapic/v1/api.html

import requests
import cv2
import io
import os
import sys

def get_image_data(urls):
    i=0
    for url in urls:    
        r = requests.get(url[0], allow_redirects=True)
        path='/users/josh.flori/desktop/memes/'+str(i)+'.jpg'
        if ".gif" not in url:
            open(path, 'wb').write(r.content)     
        else:
            print('gif found, oh no.')
            sys.exit()
        i+=1
        