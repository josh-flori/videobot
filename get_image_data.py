import praw
import requests
import cv2
import pytesseract

def get_image_data(subreddit):

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
submissions = reddit.subreddit(subreddit).top("day",limit=15)

i=0
text_list=[]
# for tesseract
config = ('-l eng --oem 1 --psm 3')
# loop through posts
for submission in submissions:
    url = submission.url
    r = requests.get(url, allow_redirects=True)
    path='/users/josh.flori/desktop/demo1/'+str(i)+'.jpg'
    if ".gif" not in url:
        open(path, 'wb').write(r.content)    
        # Read image from disk
        im = cv2.imread(path, cv2.IMREAD_COLOR)
        # Run tesseract OCR on image
        text = pytesseract.image_to_string(im, config=config)
        text_list.append(text)        
    i+=1
        
    return text_list

    
