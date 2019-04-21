import wave
from os import path
from pydub import AudioSegment
from pydub import AudioSegment
from pydub.playback import play
from moviepy.editor import *


def create_video(image_paths,parameters):
    # subtract -.2 to make the next clip show up before this one is over cuz better user experience
    clips = [ImageClip(image_paths[i]).set_duration(parameters[i][4]-.2) if i < len(image_paths)-1 else ImageClip(image_paths[i]).set_duration(parameters[i][4]+.5) for i in range(len(image_paths))] # <-- give the last frame a little time to breath before jumping into the next 

    concat_clip = concatenate_videoclips(clips, method="compose")
    concat_clip.write_videofile("/users/josh.flori/desktop/demo/first_video.mp4", fps=3,audio="/users/josh.flori/desktop/demo/single_comment.mp3")
    










