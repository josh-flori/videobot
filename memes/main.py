from memes import get_image_data_from_reddit
from memes import process_text
from memes import process_frames
import os
import cv2

os.environ[
    'GOOGLE_APPLICATION_CREDENTIALS'] = '/users/josh.flori/pycharmprojects/reddit-vision-239200-50adace0d3bf.json'
meme_path = '/users/josh.flori/desktop/memes/'
desk = '/users/josh.flori/desktop/'
subreddit = 'memes'
time_limit = 'week'
limit = 1000

# get_image_data_from_reddit.get_images(meme_path, subreddit, time_limit, limit)
# process_text.overlay_text_boxes(meme_path, desk, 10)


image = cv2.imread('/users/josh.flori/desktop/memes/' + str(i) + '.jpg')
image_text = get_image_text(pathtoimages + str(i) + '.jpg')
text_boxes=process_text.create_blocks_from_paragraph()
