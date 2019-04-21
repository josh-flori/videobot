from moviepy.editor import VideoFileClip, concatenate_videoclips
from pydub import AudioSegment

def concat_videos():
    clip1 = VideoFileClip("/users/josh.flori/desktop/demo/slide_title.mp4")
    clip2 = VideoFileClip("/users/josh.flori/desktop/demo/first_video.mp4")
    final_clip = concatenate_videoclips([clip1,clip2])
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