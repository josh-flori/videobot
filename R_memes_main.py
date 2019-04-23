# /users/josh.flori/desktop/test/bin/python3 /users/josh.flori/desktop/test/lib/python3.6/site-packages/videobot/R_memes_main.py

from videobot import get_audio
from videobot import get_image_data
from videobot import initialize_folder

#######################
# CLEAR OLD FILES OUT #
#######################

initialize_folder.initialize_folder('demo1')




text_list=get_image_data.get_image_data('memes')
print(text_list)
# get TITLE audio
#get_audio.get_audio(thread_title,'/users/josh.flori/desktop/demo/','thread_title.mp3','thread_title.wav')

