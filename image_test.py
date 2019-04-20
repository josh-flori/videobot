# /users/josh.flori/desktop/test/bin/python3 /users/josh.flori/documents/josh-flori/video-creator/reddit_test.py

# estimated average characters per minute: 652.5
# max characters per line = 67
# first argument is xy coordinate of the top left of the text. DOPE!

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
        is_eos.append(False)
        chunk_len.append(0)
    # test to see if the sentence has ended before the end of the line
    elif all([any([comment[i] == "." or comment[i] == "!" or comment[i] == "?"]),comment[i+1]==" "]):
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
    # another test, based on a sentence ending in a quote...
    elif all([any([comment[i-1]==".",comment[i-1]=="?",comment[i-1]=="!"]),comment[i]=='"' and comment[i+1]==" "]):
        dump="".join(temp)
        chunked.append(dump)
        temp=[]
        is_eos.append(True)
        chunk_len.append(len(dump))        
        
assert(len(chunked)==len(is_eos)==len(chunk_len))
# get them together for easier processing
parameters=list(zip(chunked,is_eos,chunk_len))
        
# we now need to determine how many lines there are. We can't fit more than x lines on an image. Two things must occur. we must check if lines exceed limit, if so, remove comment and don't include it in the video. also return number of lines, which will be used to adjust the y_adjust in the image
num_lines=int(len(is_eos)-is_eos.count(True))
exceeds_limit=num_lines>13        
        







####################
# INITIALIZE IMAGE #
####################
img = Image.new('RGB', (1920,1080), color = (26, 26, 26))
# set font
fnt1 = ImageFont.truetype('/Library/Fonts/Verdana.ttf', 30)
fnt2 = ImageFont.truetype('/Library/Fonts/Verdana.ttf', 40)

d = ImageDraw.Draw(img)
# add user
d.text((100,500-(num_lines*30)), user, font=fnt, fill=(42, 175, 247))
# add points
d.text((100+len(user)*27,510-(num_lines*30)), "21k points", font=fnt1, fill=(170, 170, 170))
# add time
d.text((100+len(user)*27+174,510-(num_lines*30)), '\u00B7 2 days ago', font=fnt1, fill=(170, 170, 170))




#################
# CREATE IMAGES #
#################
line=0
x_adjust=0
# parameters[i][0]==chunk, parameters[i][1]==is_eos, parameters[i][0]==chunk_len 
for i in range(len(parameters)):
    # so the point of x_adjust is when a sentence ends mid-line, we want to indent the next chunk on the same line. this is true when the previous chunk was a sentence that ended mid-line
    if i!=0:
        if parameters[i-1][1]==True:
            x_adjust=parameters[i-1][2]
        else:
            x_adjust=0
    d.text(((20.4*x_adjust)+100,560-(num_lines*30)+(line*60)), parameters[i][0], font=fnt2, fill=(240, 240, 240))
    img.save('/users/josh.flori/desktop/pil_text_font'+str(i)+'.png')
    if parameters[i][1]!=True:
        line+=1    






# for creating movie... https://github.com/Zulko/moviepy








