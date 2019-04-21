import wave
from os import path
from pydub import AudioSegment
from pydub import AudioSegment
from pydub.playback import play
from moviepy.editor import *


def create_video(image_paths,parameters):
    clips = [ImageClip(image_paths[i]).set_duration(parameters[i][3]/20) for i in range(len(image_paths))]

    concat_clip = concatenate_videoclips(clips, method="compose")
    concat_clip.write_videofile("/users/josh.flori/desktop/demo/first_video.mp4", fps=1,audio="/users/josh.flori/desktop/demo/joined_audio.mp3")











