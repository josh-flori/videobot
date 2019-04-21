# /users/josh.flori/desktop/test/bin/python3 /users/josh.flori/desktop/test/lib/python3.6/site-packages/videobot/main.py

from videobot import get_audio
from videobot import get_comments
from videobot import get_chunks
from videobot import create_frames
from videobot import create_joined_audio
from videobot import create_video

# get comment data
cleaned_comment_list,users,age_list,age_type_list,updoots,thread_title = get_comments.get_comments("https://www.reddit.com/r/AskWomen/comments/bep6mc/what_are_your_favorite_smoothie_recipes/")

# get TITLE audio
get_audio.get_audio(thread_title,'/users/josh.flori/desktop/demo/','thread_title.mp3','thread_title.wav')


# get TITLE frames
image_paths = create_frames.create_frames(parameters,num_lines,exceeds_limit,users[0],age_list[0],age_type_list[0],updoots[0])

# create TITLE video
create_video.create_video(image_paths,parameters)




# get COMMENT audio
get_audio.get_audio(cleaned_comment_list[0],'/users/josh.flori/desktop/demo/','single_comment.mp3','single_comment.wav')

# join COMMENT audio with music
create_joined_audio.join_audio_and_convert()

# get COMMENT chunk information
parameters,num_lines,exceeds_limit = get_chunks.get_chunks(cleaned_comment_list[0])


# if the text is not too long...
if not exceeds_limit:
    
    # get COMMENT frames
    image_paths = create_frames.create_frames(parameters,num_lines,exceeds_limit,users[0],age_list[0],age_type_list[0],updoots[0])

    # create COMMENT video
    create_video.create_video(image_paths,parameters)


