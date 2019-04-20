# /users/josh.flori/desktop/test/bin/python3 /users/josh.flori/desktop/test/lib/python3.6/site-packages/videobot/main.py

from videobot import get_audio
from videobot import get_comments
from videobot import get_chunks
from videobot import create_frames

# get comment data
cleaned_comment_list,users,age_list,age_type_list,updoots = get_comments.get_comments("https://www.reddit.com/r/videos/comments/begf1k/thoughts_on_the_new_butterfinger/")

# get audio data, returns nothing
get_audio.get_audio(cleaned_comment_list[0],'/users/josh.flori/desktop/demo/','single_comment.mp3','single_comment.wav')

# get chunk information
parameters,num_lines,exceeds_limit = get_chunks.get_chunks(cleaned_comment_list[0])

# get frames
... = create_frames.create_frames(parameters,num_lines,exceeds_limit,users[0],age_list[0],age_type_list[0])



print(cleaned_comment_list,"\n",users,"\n",age_list,"\n",age_type_list,"\n",updoots)