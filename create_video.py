# /users/josh.flori/desktop/test/bin/python3 /users/josh.flori/documents/josh-flori/video-creator/reddit_test.py

# estimated average characters per second: 10.875
# max characters per line = 67
# first argument is xy coordinate of the top left of the text. DOPE!

#####################
# IMPORT SOME STUFF #
#####################
import wav


from moviepy.editor import *

clips = [ImageClip(image_paths[i]).set_duration(parameters[i][3]/24) for i in range(len(image_paths))]

concat_clip = concatenate_videoclips(clips, method="compose")
concat_clip.write_videofile("/users/josh.flori/desktop/testt.mp4", fps=1,audio="/users/josh.flori/desktop/speech.mp3")






from os import path
from pydub import AudioSegment

# files                                                                         
src = "/users/josh.flori/desktop/speech.mp3"
dst = "/users/josh.flori/desktop/test.wav"

# convert wav to mp3                                                            
sound = AudioSegment.from_mp3(src)
sound.export(dst, format="wav")
# FileNotFoundError: [Errno 2] No such file or directory: 'ffprobe': 'ffprobe'





from pydub import AudioSegment
from pydub.playback import play

sound1 = AudioSegment.from_wav("/users/josh.flori/downloads/speech.wav")
sound2 = AudioSegment.from_wav("/users/josh.flori/desktop/untitled_Master.wav")


# mix sound2 with sound1, starting at 70% into sound1)
tmpsound = sound1.overlay(sound2, position=0)

#play(tmpsound)
tmpsound.export("/users/josh.flori/desktop/final_output.wav", format="wav") 












