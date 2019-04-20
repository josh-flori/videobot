from pydub import AudioSegment
from pydub.playback import play

sound1 = AudioSegment.from_wav("/users/josh.flori/downloads/speech.wav")
sound2 = AudioSegment.from_wav("/users/josh.flori/desktop/untitled_Master.wav")


# mix sound2 with sound1, starting at 70% into sound1)
tmpsound = sound1.overlay(sound2, position=0)

#play(tmpsound)
tmpsound.export("/users/josh.flori/desktop/final_output.wav", format="wav") 

