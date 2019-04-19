# /users/josh.flori/desktop/test/bin/python3 /users/josh.flori/documents/josh-flori/video-creator/amazon_api_test.py

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

reddit_text="I‘m the child but my dad waited till I‘m grown up to tell me that my mom gave me a lot of sleeping pills when I was a little child, so she could leave me alone at home to maintain her relationship with her lover while my dad was working in another country.. that cleared up many things"
session = Session(profile_name="default")
polly = session.client("polly")

try:
    # Request speech synthesis
    response = polly.synthesize_speech(Text=reddit_text, OutputFormat="mp3",
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
        output = '/users/josh.flori/desktop/speech.mp3'
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



