import wave
from os import path
from pydub import AudioSegment
from pydub import AudioSegment
from pydub.playback import play
from moviepy.editor import *
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import itertools
import wave
from random import randint



def create_title_slide(title_speech,title_text):
title_text="BLA BLA BLA"
img=Image.open('/users/josh.flori/desktop/demo/template.jpg')
#  
fnt1 = ImageFont.truetype('/Library/Fonts/Verdana.ttf', 70)
fnt2 = ImageFont.truetype('/Library/Fonts/Verdana.ttf', 50)
#   
d = ImageDraw.Draw(img)
# add user
d.text((303,500), title_text, font=fnt1, fill=(230,230,230))
# add points
d.text((127,517), str(randint(1,30))+"."+str(randint(0,9))+"k", font=fnt2, fill=(170, 170, 170))
#
#
img.save('/users/josh.flori/desktop/demo/slide_title.png')
            








    
    






def create_video(image_paths,parameters):
    clips = [ImageClip(image_paths[i]).set_duration(parameters[i][3]/20) for i in range(len(image_paths))]

    concat_clip = concatenate_videoclips(clips, method="compose")
    concat_clip.write_videofile("/users/josh.flori/desktop/demo/first_video.mp4", fps=1,audio="/users/josh.flori/desktop/demo/joined_audio.mp3")











