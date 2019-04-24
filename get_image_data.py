import praw
import requests
import cv2
import pytesseract

def get_image_data(subreddit,limit):

    ############################
    # DEFINE REDDIT CONNECTION #
    ############################
    reddit = praw.Reddit(client_id='eZ0qCk4LGFmlvg',
                         client_secret= 'ObVykPZwUf6AtmvQyh-HFIlhn8I',
                         user_agent= 'myApp',
                         username= '',
                         password= '')

    ##################
    #  DO THE STUFF  #
    ##################
    submissions = reddit.subreddit("memes").top("day",limit=limit)

    i=0
    text_list=[]
    # for tesseract
    config = ('-l eng --oem 2 --psm 12')
    # loop through posts
    for submission in submissions:
        url = submission.url
        r = requests.get(url, allow_redirects=True)
        path='/users/josh.flori/desktop/demo1/'+str(i)+'.jpg'
        print(url)
        if ".gif" not in url:
            open(path, 'wb').write(r.content)    
            # Read image from disk
            im = cv2.imread(path, cv2.IMREAD_COLOR)
            # Run tesseract OCR on image
            text = pytesseract.image_to_string(im, config=config)
            text_list.append(text)        
        print(i)
        i+=1
        
    return text_list
