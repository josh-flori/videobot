from PIL import Image, ImageDraw, ImageFont
from nltk.tokenize import TweetTokenizer
import numpy as np
import itertools
import wave
from random import randint

# parameters[i][0]==chunk_text (list), parameters[i][1]==is_eos (list), parameters[i][2]==indent (list), parameters[i][3]==chunk_len (list)

def create_frames(parameters,num_lines,exceeds_limit,user,age,age_type,updoots):
    
    font = ImageFont.truetype('/users/josh.flori/downloads/verdana.ttf' , 12)
    
    ####################
    # INITIALIZE IMAGE #
    ####################
    img = Image.new('RGB', (1920,1080), color = (26, 26, 26))
    # set font
    fnt1 = ImageFont.truetype('/Library/Fonts/Verdana.ttf', 30)
    fnt2 = ImageFont.truetype('/Library/Fonts/Verdana.ttf', 40)

    d = ImageDraw.Draw(img)
    # add user
    d.text((100,500-(num_lines*29)), user, font=fnt1, fill=(42, 175, 247))
    # add points
    d.text((100+font.getsize(user)[0]*2,510-(num_lines*30)), str(randint(1,9))+"."+str(randint(0,9))+"k points", font=fnt1, fill=(170, 170, 170))
    # add time
    d.text((100+font.getsize(user)[0]*2+174,510-(num_lines*30)), '\u00B7 '+str(age)+' '+age_type+' ago', font=fnt1, fill=(170, 170, 170))


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
        d.text(((3.41*x_adjust)+100,560-(num_lines*30)+(line*60)), parameters[i][0], font=fnt2, fill=(240, 240, 240))
        img.save('/users/josh.flori/desktop/demo/'+str(i)+'.png')
        image_paths.append('/users/josh.flori/desktop/demo/'+str(i)+'.png')
        if parameters[i][1]!=True:
            line+=1   
            
    return image_paths 
            
            








    
    

