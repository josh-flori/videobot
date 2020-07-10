# /users/josh.flori/desktop/test/bin/python3 /users/josh.flori/desktop/test/lib/python3.6/site-packages/videobot/R_ask_reddit_main.py

from text import get_audio
from text import get_comments_from_sheet
from text import get_chunks_comments
from text import create_frames
from text import create_joined_audio
from text import create_video
from text import create_title_slide
from text import get_chunks_title
from text import initialize_folder
from text import concat_videos
import os
import shutil

        
        
directory='/users/josh.flori/desktop/demo'+str(i)


total_list = get_comments_from_reddit.get_comments('https://www.reddit.com/r/AskReddit/comments/grst2b/police_officers_of_reddit_what_are_you_thinking/')


initialize_folder.initialize_folder(directory,'first')



    ######################
    # CREATE TITLE VIDEO #
    ######################

    # get comment data
    cleaned_comment_list,users,age_list,age_type_list,updoots,thread_title,op = get_comments_from_sheet.get_comments(column,service,_id)

    # get TITLE audio
    get_audio.get_audio(thread_title,'/thread_title.mp3','thread_title.wav',directory)

    parameters,num_lines = get_chunks_title.get_chunks(thread_title,'/thread_title.mp3',.5,directory)

    # create TITLE slide (video)
    create_title_slide.create_title_slide(parameters,num_lines,'/thread_title.mp3',thread_title,op,age_list[0],age_type_list[0],directory)






    #########################
    # CREATE COMMENT VIDEOS #
    #########################

    for i in range(len(users))[0:3]:

        print(len(cleaned_comment_list[i]))

        # get COMMENT audio
        if not len(cleaned_comment_list[i]) >1500 and 'http' not in cleaned_comment_list[i]:


            get_audio.get_audio(cleaned_comment_list[i],'/single_comment'+str(i)+'.mp3','/single_comment'+str(i)+'.wav',directory)


            # get COMMENT chunk information
            parameters,num_lines,exceeds_limit = get_chunks_comments.get_chunks(cleaned_comment_list[i],'/single_comment'+str(i)+'.mp3',.5,directory)
            print(exceeds_limit)

            # if the text is not too long...
            if not exceeds_limit:

                # get COMMENT frames
                image_paths = create_frames.create_frames(parameters,num_lines,exceeds_limit,users[i],age_list[i],age_type_list[i],updoots[i],i,directory)

                # create COMMENT video
                create_video.create_video(image_paths,parameters,'/single_comment'+str(i)+'.mp3',i,directory)




    #################
    # CONCAT VIDEOS #
    #################

    concat_videos.concat_videos(directory)
    initialize_folder.initialize_folder(directory,'second')