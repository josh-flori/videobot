from moviepy.editor import VideoFileClip, concatenate_videoclips
from pydub import AudioSegment
import os
import glob

def concat_videos():
    clips =[VideoFileClip("/users/josh.flori/desktop/demo/slide_title.mp4")]
        
    files=sorted(glob.glob('/users/josh.flori/desktop/demo/*.mp4'), key=os.path.getmtime)
    for f in files:            
        if 'slide_title' not in f:
            clips.append(VideoFileClip(f))
    

    
    final_clip = concatenate_videoclips(clips)
    final_clip.write_videofile("/users/josh.flori/desktop/demo/concat.mp4")
    
    video = VideoFileClip("/users/josh.flori/desktop/demo/concat.mp4")
    audio = video.audio
    audio.write_audiofile('/users/josh.flori/desktop/demo/concat_audio.mp3')

    # convert to wav
    def convert_to_wav(src,dst):
        sound = AudioSegment.from_mp3(src)
        sound.export(dst, format="wav")

    convert_to_wav('/users/josh.flori/desktop/demo/concat_audio.mp3','/users/josh.flori/desktop/demo/concat_audio.wav')
    music = AudioSegment.from_wav("/users/josh.flori/desktop/demo/music.wav")

    concat_audio = AudioSegment.from_wav("/users/josh.flori/desktop/demo/concat_audio.wav")
    concat_audio.overlay(music, position=0).export("/users/josh.flori/desktop/demo/joined_audio.wav", format="wav")

    # convert back to mp3 for the video
    joined = AudioSegment.from_wav("/users/josh.flori/desktop/demo/joined_audio.wav")
    joined.export("/users/josh.flori/desktop/demo/joined_audio.mp3", format="mp3")

    
    final_clip=VideoFileClip("/users/josh.flori/desktop/demo/concat.mp4")
    final_clip.write_videofile("/users/josh.flori/desktop/demo/finished.mp4",audio="/users/josh.flori/desktop/demo/joined_audio.mp3")