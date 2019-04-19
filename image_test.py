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


def split_seq(iterable, size):
    it = iter(iterable)
    item = list(itertools.islice(it, size))
    while item:
        yield item
        item = list(itertools.islice(it, size))



######################
# SET SOME THINGS UP #
######################
chunked = list(split_seq(TweetTokenizer().tokenize(comment),7))
# create image
img = Image.new('RGB', (1920,1080), color = (26, 26, 26))
# set font
fnt1 = ImageFont.truetype('/Library/Fonts/Verdana.ttf', 30)
fnt2 = ImageFont.truetype('/Library/Fonts/Verdana.ttf', 40)
# user
user="bla"
# age
age = "3 months ago"
# updoots
updoots = updoots


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


# measures how many characters have accumulated on that line
fill=0
# determines if write to same line
same_line=True
# control movement parameters
x_adjust=0
vertical=0

for i in range(len(chunked)):
    # this starts at 0, will increment with each new line, controls the vertical dimension of where the line is typed, adjusts as "same_line" variable adjusts
    chunk_length=len("".join(chunked[i]))
    fill+=chunk_length
    print(fill)
    if fill >= 67:
        same_line=False
        # reset to chunk length
        fill=chunk_length
        # bump to next line
        vertical+=1
        x_adjust=0
    else:
        same_line=True
    # add comments, using different text (bigger)
    d.text(((25*x_adjust)+200,(vertical*60)+260), " ".join(chunked[i]), font=fnt2, fill=(240, 240, 240))
    img.save('/users/josh.flori/desktop/pil_text_font'+str(i)+'.png')
    x_adjust+=chunk_length    





# TODO... loop through comment chunks and save as image files. store log of how many characters each image contains which will be used to sync up to the audio data


# for creating movie... https://github.com/Zulko/moviepy
# first argument is xy coordinate of the top left of the text. DOPE!







