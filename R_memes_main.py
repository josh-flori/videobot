# /users/josh.flori/desktop/test/bin/python3 /users/josh.flori/desktop/test/lib/python3.6/site-packages/videobot/R_memes_main.py

from videobot import get_audio
from videobot import get_image_data
from videobot import initialize_folder
from videobot import process_image_text

#######################
# CLEAR OLD FILES OUT #
#######################

#initialize_folder.initialize_folder('demo1')



from videobot import get_image_data
text_list=get_image_data.get_image_data('memes',5)

text=text_list[0]

t=process_image_text.process_image_text(text)


t=process_image_text(text)


# get TITLE audio
#get_audio.get_audio(thread_title,'/users/josh.flori/desktop/demo/','thread_title.mp3','thread_title.wav')

