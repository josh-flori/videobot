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



def create_title_slide(parameters,num_lines,title_speech,title_text):

    img=Image.open('/users/josh.flori/desktop/demo/template.jpg')
    #  
    fnt1 = ImageFont.truetype('/Library/Fonts/Verdana.ttf', 70)
    fnt2 = ImageFont.truetype('/Library/Fonts/Verdana.ttf', 50)
    #   
    d = ImageDraw.Draw(img)
    # add points
    d.text((46,515), str(randint(1,30))+"."+str(randint(0,9))+"k", font=fnt2, fill=(170, 170, 170))
    #
    #
    img.save('/users/josh.flori/desktop/demo/slide_title.png')
            
            
    #################
    # CREATE FRAMES #
    #################
    line=0
    image_paths=[]
    line=0
    for i in range(len(parameters)):
        d.text((224,524-(num_lines*32)+(line*74)), parameters[i][0], font=fnt1, fill=(230, 230, 230))
        img.save('/users/josh.flori/desktop/demo/title'+str(i)+'.png')
        image_paths.append('/users/josh.flori/desktop/demo/title'+str(i)+'.png')
        line+=1
        
    
        # subtract -.2 to make the next clip show up before this one is over cuz better user experience    
    clips = [ImageClip(image_paths[i]).set_duration(parameters[i][2]-.32) if i < len(image_paths)-1 else ImageClip(image_paths[i]).set_duration(parameters[i][2]+.5) for i in range(len(image_paths))] # <-- give the last frame a little time to breath before jumping into the next 

    
    concat_clip = concatenate_videoclips(clips, method="compose")
    concat_clip.write_videofile("/users/josh.flori/desktop/demo/slide_title.mp4", fps=3,audio=title_speech)
    








    
    
