# /users/josh.flori/desktop/test/bin/python3 /users/josh.flori/desktop/test/lib/python3.6/site-packages/videobot/main.py

from videobot import get_audio
from videobot import get_comments




get_audio.get_audio("this is a test",'/users/josh.flori/desktop/','test.mp3')
comments=get_comments.get_comments("https://www.reddit.com/r/videos/comments/begf1k/thoughts_on_the_new_butterfinger/")
print(comments)