from memes import get_image_data_from_reddit, process_text, process_frames, utils, config, process_audio
import os
import cv2

os.environ[
    'GOOGLE_APPLICATION_CREDENTIALS'] = '/users/josh.flori/pycharmprojects/reddit-vision-239200-50adace0d3bf.json'
os.environ['ACCESS_KEY'] = config.aws_ACCESS_KEY
os.environ['SECRET'] = config.aws_SECRET
os.environ['region'] = config.aws_region

meme_path = '/users/josh.flori/desktop/memes/'
desk = '/users/josh.flori/desktop/'
subreddit = 'memes'
time_limit = 'week'
limit = 1000

# get_image_data_from_reddit.get_images(meme_path, subreddit, time_limit, limit)
# process_text.overlay_text_boxes(meme_path, desk, 10)

i = 0
for i in range(20):
    image = cv2.imread('/users/josh.flori/desktop/memes/' + str(i) + '.jpg')
    image_text = process_text.get_image_text('/users/josh.flori/desktop/memes/' + str(i) + '.jpg')
    # text_boxes = process_text.create_blocks_from_paragraph(image_text)
    # frame_boxes = process_frames.create_blocks_from_annotations(all_annotations[0])
    text_boxes = create_blocks_from_paragraph(image_text)
    expand_to_edge(all_annotations[i])
    frame_boxes = create_blocks_from_annotations(all_annotations[i])
    trim_white_space(image, frame_boxes)

    all_boxes = text_boxes + frame_boxes
    all_boxes = sorted(all_boxes, key=lambda x: (x[0][1], x[0][0]))
    align_tops(all_boxes)
    all_boxes = sorted(all_boxes, key=lambda x: (x[0][1], x[0][0]))
    print(all_boxes)
    which_comes_next(image, all_boxes, desk, i)


process_audio.get_audio("bla bla bla", 'empty.mp3', '', '/users/josh.flori/desktop/')