from google.cloud import automl
import os
from google.cloud import language_v1

os.environ[
        'GOOGLE_APPLICATION_CREDENTIALS'] = '/users/josh.flori/pycharmprojects/reddit-vision-239200-50adace0d3bf.json'
model_client = automl.AutoMlClient()
language_client = language_v1.LanguageServiceClient()
aws_ACCESS_KEY = 'AKIAZHJIK7VSX3NOGMFV'
aws_SECRET = '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'
aws_region = 'us-east-1'
reddit_client_id = 'eZ0qCk4LGFmlvg'
reddit_client_secret = 'ObVykPZwUf6AtmvQyh-HFIlhn8I'
custom_model_project_id = '140553804812'
custom_model_model_id = 'IOD8594130328371593216'
model_full_id = model_client.model_path(custom_model_project_id, "us-central1", custom_model_model_id)
meme_path = '/users/josh.flori/desktop/memes/'
meme_output_path = '/users/josh.flori/desktop/memes_output/'
audio_output_path = '/users/josh.flori/desktop/mp3_output/'
padding_dir = '/users/josh.flori/desktop/'
output_audio_fname = 'out.mp3'
video_out_path = '/users/josh.flori/desktop/'
