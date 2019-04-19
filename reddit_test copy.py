# /users/josh.flori/desktop/test/bin/python3 /users/josh.flori/documents/josh-flori/video-creator/reddit_test.py

#####################
# IMPORT SOME STUFF #
#####################
from PIL import Image, ImageDraw, ImageFont
# create image
img = Image.new('RGB', (1920,1080), color = (73, 109, 137))
# set font
fnt = ImageFont.truetype('/Library/Fonts/Verdana.ttf', 15)
# draw image
d = ImageDraw.Draw(img)
# first argument is xy coordinate of the top left of the text. DOPE!
d.text((800,1000), "I work at an Italian place right now ", font=fnt, fill=(255, 255, 0))
img.save('pil_text_font.png')