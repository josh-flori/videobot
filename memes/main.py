from memes import get_image_data_from_reddit
from memes import process_text
from memes import process_frames
from memes import utils
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

i = 0
image_text = process_text.get_image_text('/users/josh.flori/desktop/memes/' + str(i) + '.jpg')
text_boxes = process_text.create_blocks_from_paragraph(image_text)
frame_boxes = process_frames.create_blocks_from_annotations(all_annotations[0])



text_boxes = create_blocks_from_paragraph(image_text)
frame_boxes = create_blocks_from_annotations(all_annotations[0])
all_boxes=text_boxes+frame_boxes
all_boxes=sorted(all_boxes, key = lambda x: x[0][1])

image=cv2.imread('/users/josh.flori/desktop/memes/0.jpg')
which_comes_next(image,all_boxes,desk,0)