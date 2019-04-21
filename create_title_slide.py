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


# parameters[i][0]==chunk_text (list), parameters[i][1]==is_eos (list), parameters[i][2]==indent (list), parameters[i][3]==chunk_len (list)

def create_frames(parameters,num_lines,exceeds_limit,user,age,age_type,updoots):

    ####################
    # INITIALIZE IMAGE #
    ####################
    img = Image.new('RGB', (1920,1080), color = (26, 26, 26))
    # set font
    fnt1 = ImageFont.truetype('/Library/Fonts/Verdana.ttf', 30)
    fnt2 = ImageFont.truetype('/Library/Fonts/Verdana.ttf', 40)

    d = ImageDraw.Draw(img)
    # add user
    d.text((100,500-(num_lines*30)), user, font=fnt1, fill=(42, 175, 247))
    # add points
    d.text((100+len(user)*27,510-(num_lines*30)), str(updoots)+" points", font=fnt1, fill=(170, 170, 170))
    # add time
    d.text((100+len(user)*27+174,510-(num_lines*30)), '\u00B7 '+str(age)+' '+age_type+' ago', font=fnt1, fill=(170, 170, 170))


    #################
    # CREATE FRAMES #
    #################
    line=0
    x_adjust=0
    image_paths=[]
    for i in range(len(parameters)):
        # so the point of x_adjust is when a sentence ends mid-line, we want to indent the next chunk on the same line. this is true when the previous chunk was a sentence that ended mid-line
        if i!=0:
            if parameters[i-1][1]==True:
                x_adjust=parameters[i-1][2]
            else:
                x_adjust=0
        d.text(((2.5*x_adjust)+100,560-(num_lines*30)+(line*60)), parameters[i][0], font=fnt2, fill=(240, 240, 240))
        img.save('/users/josh.flori/desktop/demo/'+str(i)+'.png')
        image_paths.append('/users/josh.flori/desktop/demo/'+str(i)+'.png')
        if parameters[i][1]!=True:
            line+=1   
            
    return image_paths 
            
            








    
    






def create_video(image_paths,parameters):
    clips = [ImageClip(image_paths[i]).set_duration(parameters[i][3]/20) for i in range(len(image_paths))]

    concat_clip = concatenate_videoclips(clips, method="compose")
    concat_clip.write_videofile("/users/josh.flori/desktop/demo/first_video.mp4", fps=1,audio="/users/josh.flori/desktop/demo/joined_audio.mp3")











