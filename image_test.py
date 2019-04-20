# /users/josh.flori/desktop/test/bin/python3 /users/josh.flori/documents/josh-flori/video-creator/reddit_test.py

# estimated average characters per minute: 652.5
# max characters per line = 67

#####################
# IMPORT SOME STUFF #
#####################
from PIL import Image, ImageDraw, ImageFont
from nltk.tokenize import TweetTokenizer
import numpy as np
import itertools

comment= """That she can't have a relationship with her grandfather because he's a pedophile and I would never trust him. The rest of my family maintains a relationship with him and leans on me hard to open up communication because "family comes first." They are absolutely right, my family does come first, which is why my daughter won't ever have to have a relationship with him."""
# user
user="bla"
# age
age = "3 months ago"
# updoots
updoots = updoots

######################
# SET SOME THINGS UP #
######################
count = 0
# holds total chunked list 
chunked=[]
# holds each letter as the for loop progress, dumped into chunked once character limit or sentence end is reached
temp=[]
# contains information about whether that chunk is the end of a sentence, to be passed in when creating the images so that the image thing knows to put the next chunk on the same line rather than the next line
is_eos=[]
# when the above is triggered, the image thing needs to know how far to indent the next chunk on the same line, so this will govern that
chunk_len=[]
# loop through each letter
for i in range(len(comment)):
    # append that letter to temporary holding list
    temp.append(comment[i])
    # increase count of letters
    count+=1
    # test to see if the sentence has ended before the end of the line
    if comment[i] == "." or comment[i] == "!" or comment[i] == "?" and comment[i+1]==" ":
        # join letters together into single string
        dump="".join(temp)
        # append to chunked
        chunked.append(dump)
        # reset temporary holding list
        temp=[]
        # this will be used to govern the x_adjust parameter in the image thing
        is_eos.append(True)
        # this will be used to govern the x_adjust parameter in the image thing
        chunk_len.append(len(dump))
    # test if end of line has been reached
    if count >67:
        if comment[i]==" ":
            dump="".join(temp)
            chunked.append(dump)
            temp=[]
            count=0
            is_eos.append(False)
            chunk_len.append(0) 
    # true when reached the end of the comment and no other condition was met
    elif i == len(comment)-1:
        dump="".join(temp)
        chunked.append(dump)
        
# get them together for easier processing
parameters=list(zip(chunked,is_eos,chunk_len))











# create image
img = Image.new('RGB', (1920,1080), color = (26, 26, 26))
# set font
fnt1 = ImageFont.truetype('/Library/Fonts/Verdana.ttf', 30)
fnt2 = ImageFont.truetype('/Library/Fonts/Verdana.ttf', 40)


####################
# INITIALIZE IMAGE #
####################
d = ImageDraw.Draw(img)
# add user
d.text((100,200), user, font=fnt, fill=(42, 175, 247))
# add points
d.text((100+len(user)*27,210), "21k points", font=fnt1, fill=(170, 170, 170))
# add time
d.text((100+len(user)*27+174,210), '\u00B7 2 days ago', font=fnt1, fill=(170, 170, 170))




# control movement parameters
vertical=0

for i in range(len(chunked)):
    # add comments, using different text (bigger)
    d.text(((25*x_adjust)+200,(vertical*60)+260), chunked[i], font=fnt2, fill=(240, 240, 240))
    img.save('/users/josh.flori/desktop/pil_text_font'+str(i)+'.png')
    vertical+=1    





# TODO... loop through comment chunks and save as image files. store log of how many characters each image contains which will be used to sync up to the audio data


# for creating movie... https://github.com/Zulko/moviepy
# first argument is xy coordinate of the top left of the text. DOPE!







