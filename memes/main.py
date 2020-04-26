from memes import get_image_data_from_reddit
import os

os.environ[
    'GOOGLE_APPLICATION_CREDENTIALS'] = '/users/josh.flori/pycharmprojects/reddit-vision-239200-50adace0d3bf.json'
output_path='/users/josh.flori/desktop/memes/'
subreddit='memes'
time_limit='week'
limit=1000


# get_image_data_from_reddit.get_images(output_path, subreddit, time_limit, limit)
