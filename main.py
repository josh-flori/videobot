# /users/josh.flori/desktop/test/bin/python3 /users/josh.flori/desktop/test/lib/python3.6/site-packages/videobot/main.py

from videobot import get_audio
from videobot import get_comments
from videobot import get_chunks_comments
from videobot import create_frames
from videobot import create_joined_audio
from videobot import create_video
from videobot import create_title_slide
from videobot import get_chunks_title
from videobot import initialize_folder
from videobot import concat_videos


#######################
# CLEAR OLD FILES OUT #
#######################

initialize_folder.initialize_folder()






######################
# CREATE TITLE VIDEO #
######################

# get comment data
cleaned_comment_list,users,age_list,age_type_list,updoots,thread_title,op = get_comments.get_comments("https://www.reddit.com/r/AskReddit/comments/b9q1zj/what_sounds_like_fiction_but_is_actually_a_real/")

# get TITLE audio
get_audio.get_audio(thread_title,'/users/josh.flori/desktop/demo/','thread_title.mp3','thread_title.wav')

parameters,num_lines = get_chunks_title.get_chunks(thread_title,'/users/josh.flori/desktop/demo/thread_title.mp3',.5)

# create TITLE slide (video)
create_title_slide.create_title_slide(parameters,num_lines,'/users/josh.flori/desktop/demo/thread_title.mp3',thread_title,op,age_list[0],age_type_list[0])






#########################
# CREATE COMMENT VIDEOS #
#########################

for i in range(len(users))[0:2]:
    
    # get COMMENT audio
    get_audio.get_audio(cleaned_comment_list[0],'/users/josh.flori/desktop/demo/','single_comment'+str(i)+'.mp3','single_comment'+str(i)+'.wav')


    # get COMMENT chunk information
    parameters,num_lines,exceeds_limit = get_chunks_comments.get_chunks(cleaned_comment_list[0],'/users/josh.flori/desktop/demo/single_comment'+str(i)+'.mp3',.5)


    # if the text is not too long...
    if not exceeds_limit:

        # get COMMENT frames
        image_paths = create_frames.create_frames(parameters,num_lines,exceeds_limit,users[i],age_list[i],age_type_list[i],updoots[i],i)

        # create COMMENT video
        create_video.create_video(image_paths,parameters,'/users/josh.flori/desktop/demo/single_comment'+str(i)+'.mp3')




#################
# CONCAT VIDEOS #
#################

concat_videos.concat_videos()