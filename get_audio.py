# https://console.aws.amazon.com/iam/home?#/users
# pip install awscli
# pip install boto3
# aws config (from command line)... then input data... 
# ACCESS_KEY = AKIAZHJIK7VSX3NOGMFV 
# SECRET = 90NEX623FmzyOctli84+9E3Q+bE1p5oPcX8w18kino 
# region = us-east-1

from boto3 import Session
from botocore.exceptions import BotoCoreError, ClientError
from contextlib import closing
import os
import sys
import subprocess
from tempfile import gettempdir
from os import path
from pydub import AudioSegment


def get_audio(comment,path,fname_mp3,fname_wav):
        
    # initialize api
    session = Session(profile_name="default")
    polly = session.client("polly")
    
    try:
        # Request speech synthesis
        response = polly.synthesize_speech(Text=comment, OutputFormat="mp3",
                                        VoiceId="Matthew")
    except (BotoCoreError, ClientError) as error:
        # The service returned an error, exit gracefully
        print(error)
        sys.exit(-1)


    # Access the audio stream from the response
    if "AudioStream" in response:
        # Note: Closing the stream is important as the service throttles on the
        # number of parallel connections. Here we are using contextlib.closing to
        # ensure the close method of the stream object will be called automatically
        # at the end of the with statement's scope.
        with closing(response["AudioStream"]) as stream:
            output = path+fname_mp3
            try:
                # Open a file for writing the output as a binary stream
                with open(output, "wb") as file:
                    file.write(stream.read())
            except IOError as error:
                # Could not write to file, exit gracefully
                print(error)
                sys.exit(-1)
    else:
        # The response didn't contain audio data, exit gracefully
        print("Could not stream audio")
        sys.exit(-1)
    
    
    
    # pad with 1 second of silence to create breathing room in the video
    combined = AudioSegment.empty()
    combined += AudioSegment.from_mp3(path+fname_mp3)
    combined += AudioSegment.from_mp3('/users/josh.flori/desktop/demo/padding.mp3')

    combined.export(path+fname_mp3, format="mp3")
    
    
        
        
    # convert to wav
    def convert_to_wav(src,dst):
        sound = AudioSegment.from_mp3(src)
        sound.export(dst, format="wav")
        
    convert_to_wav(path+fname_mp3,path+fname_wav)    
        
        



