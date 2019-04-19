# /users/josh.flori/desktop/test/bin/python3 /users/josh.flori/documents/josh-flori/video-creator/reddit_test.py

#####################
# IMPORT SOME STUFF #
#####################
from PIL import Image, ImageDraw, ImageFont
# create image
img = Image.new('RGB', (1920,1080), color = (26, 26, 26))
# set font
fnt1 = ImageFont.truetype('/Library/Fonts/Verdana.ttf', 30)
fnt2 = ImageFont.truetype('/Library/Fonts/Verdana.ttf', 40)
# draw image
d = ImageDraw.Draw(img)
user="bla"
arbitrary_time = "3 months ago"

# first argument is xy coordinate of the top left of the text. DOPE!
# add user
d.text((200,200), user, font=fnt, fill=(42, 175, 247))
# add points
d.text((200+len(user)*27,210), "21k points", font=fnt1, fill=(170, 170, 170))
# add time
d.text((200+len(user)*27+174,210), "* "+arbitrary_time, font=fnt1, fill=(170, 170, 170))

# add comments, using different text (bigger)
d.text((200,290), "I work at an Italian place right now ", font=fnt2, fill=(240, 240, 240))
img.save('pil_text_font.png')

# TODO... loop through comment chunks and save as image files. store log of how many characters each image contains which will be used to sync up to the audio data


# for creating movie... https://github.com/Zulko/moviepy