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



def create_title_slide(parameters,num_lines,title_speech,title_text,op,age,age_type):
    
    font = ImageFont.truetype('/users/josh.flori/downloads/verdana.ttf' , 35)

    img=Image.open('/users/josh.flori/desktop/demo/template.jpg')

    fnt1 = ImageFont.truetype('/Library/Fonts/Verdana.ttf', 70)
    fnt2 = ImageFont.truetype('/Library/Fonts/Verdana.ttf', 50)
    fnt3 = ImageFont.truetype('/Library/Fonts/Verdana.ttf', 35)
    fnt4 = ImageFont.truetype('/Library/Fonts/Verdana.ttf', 30)

    d = ImageDraw.Draw(img)
    # add points
    d.text((46,515), str(randint(1,30))+"."+str(randint(0,9))+"k", font=fnt2, fill=(170, 170, 170))
    # add user
    d.text((220,475-(num_lines*32)), str(op), font=fnt3, fill=(42, 175, 247))
    # add time
    d.text((220+font.getsize(str(op))[0],480-(num_lines*32)), ' \u00B7 '+str(age)+' '+age_type+' ago', font=fnt4, fill=(170, 170, 170))

    img.save('/users/josh.flori/desktop/demo/slide_title.png')
            
            
    #################
    # CREATE FRAMES #
    #################
    line=0
    image_paths=[]
    line=0
    for i in range(len(parameters)):
        d.text((224,526-(num_lines*35)+(line*83)), parameters[i][0], font=fnt1, fill=(230, 230, 230))
        img.save('/users/josh.flori/desktop/demo/title'+str(i)+'.png')
        image_paths.append('/users/josh.flori/desktop/demo/title'+str(i)+'.png')
        line+=1
        
    
        # subtract -.2 to make the next clip show up before this one is over cuz better user experience    
    clips = [ImageClip(image_paths[i]).set_duration(parameters[i][2]-.4) if i < len(image_paths)-1 else ImageClip(image_paths[i]).set_duration(parameters[i][2]+.5) for i in range(len(image_paths))] # <-- give the last frame a little time to breath before jumping into the next 

    
    concat_clip = concatenate_videoclips(clips, method="compose")
    concat_clip.write_videofile("/users/josh.flori/desktop/demo/slide_title.mp4", fps=10,audio=title_speech)
    








    
    
