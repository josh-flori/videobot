from pydub import AudioSegment
from pydub.playback import play



# must be converted back to mp3 for the video to be able to use it

def join_audio_and_convert():
    speech = AudioSegment.from_wav("/users/josh.flori/desktop/demo/single_comment.wav")
    music = AudioSegment.from_wav("/users/josh.flori/desktop/demo/music.wav")

    # export speech + music
    speech.overlay(music, position=0).export("/users/josh.flori/desktop/demo/joined_audio.wav", format="wav") 
    
    # convert back to mp3 for the video
    joined = AudioSegment.from_wav("/users/josh.flori/desktop/demo/joined_audio.wav")
    joined.export("/users/josh.flori/desktop/demo/joined_audio.mp3", format="mp3")
    
