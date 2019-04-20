# /users/josh.flori/desktop/test/bin/python3 /users/josh.flori/desktop/test/lib/python3.6/site-packages/videobot/main.py

from videobot import get_audio
from videobot import get_comments
from videobot import create_frames

# get comment data
cleaned_comment_list,users,age_list,age_type_list,updoots=get_comments.get_comments("https://www.reddit.com/r/videos/comments/begf1k/thoughts_on_the_new_butterfinger/")

# get audio data
get_audio.get_audio(cleaned_comment_list[0],'/users/josh.flori/desktop/demo/','single_comment.mp3','single_comment.wav')

# get frames
... = create_frames.create_frames(users[0],cleaned_comment_list[0],age_list[0],updoots[0])



print(cleaned_comment_list,"\n",users,"\n",age_list,"\n",age_type_list,"\n",updoots)