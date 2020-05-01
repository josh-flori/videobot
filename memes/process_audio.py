# on mac, ffmpeg must be installed liked: brew install ffmpeg
# and AudioSegment.converter must point to the download location (installs to /usr/local/Cellar/ by default)
# I had to restart pycharm
from botocore.exceptions import BotoCoreError, ClientError
from contextlib import closing
from memes import config
import boto3
import sys
from pydub import AudioSegment

AudioSegment.ffmpeg = '/users/josh.flori/pycharmprojects/bla/'

def get_audio(text, fname_mp3, directory):
    polly_client = boto3.Session(
        aws_access_key_id=config.aws_ACCESS_KEY,
        aws_secret_access_key=config.aws_SECRET,
        region_name='us-west-2').client('polly')

    try:
        # Request speech synthesis
        response = polly_client.synthesize_speech(Text=text, OutputFormat="mp3",
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
            output = directory + fname_mp3
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
    combined += AudioSegment.from_mp3(directory + fname_mp3)
    combined += AudioSegment.from_mp3(directory + 'padding.mp3')
    combined.export(directory + fname_mp3, format="mp3")

