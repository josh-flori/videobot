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
chunked = list(split_seq(TweetTokenizer().tokenize(comment),5))
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
img = Image.new('RGB', (1920,1080), color = (26, 26, 26))
d = ImageDraw.Draw(img)
# add user
d.text((100,200), user, font=fnt, fill=(42, 175, 247))
# add points
d.text((100+len(user)*27,210), "21k points", font=fnt1, fill=(170, 170, 170))
# add time
d.text((100+len(user)*27+174,210), '\u00B7 2 days ago', font=fnt1, fill=(170, 170, 170))
t="1111111111111111111111111111111111111111111111111111111111111111111"
d.text((100,260), t, font=fnt2, fill=(240, 240, 240))
img.save('/users/josh.flori/desktop/test.png')

for i in range(len(chunked)):
    # add comments, using different text (bigger)
    d.text((200,(i*60)+260), " ".join(chunked[i]), font=fnt2, fill=(240, 240, 240))
    img.save('/users/josh.flori/desktop/pil_text_font'+str(i)+'.png')
        





# TODO... loop through comment chunks and save as image files. store log of how many characters each image contains which will be used to sync up to the audio data


# for creating movie... https://github.com/Zulko/moviepy
# first argument is xy coordinate of the top left of the text. DOPE!







