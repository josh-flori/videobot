from botocore.exceptions import BotoCoreError, ClientError
from contextlib import closing
from memes import config
import boto3
import sys
from pydub import AudioSegment

# To properly install ffmpeg on mac, it must be brew installed and AudioSegment.converter must point to the download
# location (installs to /usr/local/Cellar/ by default). After doing this, I had to restart pycharm.

AudioSegment.ffmpeg = '/users/josh.flori/pycharmprojects/bla/'


def create_mp3s(audio_text, image_num, directory, padding_dir):
    """ Returns distinct mp3 files for each section of text or silence. To be combined in later function. """
    polly_client = boto3.Session(
        aws_access_key_id=config.aws_ACCESS_KEY,
        aws_secret_access_key=config.aws_SECRET,
        region_name='us-west-2').client('polly')
    f = 0
    for text in audio_text:
        if text != 'empty':
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
                    output = directory + str(image_num) + '.' + str(f) + '.mp3'
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
        else:
            empty = AudioSegment.from_mp3(padding_dir + 'padding.mp3')
            empty.export(directory + str(image_num) + '.' + str(f) + '.mp3', format="mp3")
        f += 1
