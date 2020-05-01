from memes import get_image_data_from_reddit, process_text, process_frames, utils, config, process_audio, process_audio
import os
import cv2

os.environ[
    'GOOGLE_APPLICATION_CREDENTIALS'] = '/users/josh.flori/pycharmprojects/reddit-vision-239200-50adace0d3bf.json'
os.environ['ACCESS_KEY'] = config.aws_ACCESS_KEY
os.environ['SECRET'] = config.aws_SECRET
os.environ['region'] = config.aws_region

meme_path = '/users/josh.flori/desktop/memes/'
output_path = '/users/josh.flori/desktop/'
subreddit = 'memes'
time_limit = 'week'
limit = 1000

# GET IMAGE DATA FROM REDDIT

# get_image_data_from_reddit.get_images(meme_path, subreddit, time_limit, limit)

print('Dont forget to turn off the custom model!!!!!!!!')
for i in range(limit):

    ############
    # PART 1: GET IMAGE API DATA (TEXT/CUSTOM MODEL BOUNDING BOX DATA
    ############

    # LOAD IMAGE
    image = cv2.imread('/users/josh.flori/desktop/memes/' + str(i) + '.jpg')
    # GET IMAGE TEXT FROM GOOGLE API
    image_text = process_text.get_image_text('/users/josh.flori/desktop/memes/' + str(i) + '.jpg')
    # CREATE TEXT BOUNDING BOXES WITH A BUNCH OF RULES AND EXCLUSIONS BUILT IN
    text_boxes = process_text.create_blocks_from_paragraph(image_text)
    # GET MODEL BOUNDING BOXES
    annotation = process_frames.get_prediction(meme_path, i, config.custom_model_project_id,
                                               config.custom_model_model_id)

    ############
    # PART 2: CLEAN UP THE DATA
    ############

    # CLEAN UP ANNOTATION
    process_frames.expand_to_edge(annotation)
    # CREATE BLOCKS FROM ANNOTATION
    frame_boxes = process_frames.create_blocks_from_annotations(annotation, image)
    # CLEAN UP ANNOTATION AGAIN
    process_frames.trim_white_space(image, frame_boxes)

    ############
    # PART 3: CREATE MASTER LIST OF BOX OBJECTS
    ############
    # COMBINE TEXT/CUSTOM MODEL BOXES
    all_boxes = text_boxes + frame_boxes
    # SORT BY Y, THEN X
    all_boxes = sorted(all_boxes, key=lambda x: (x[0][1], x[0][0]))
    # MORE CLEANING UP - FOR ANY BOXES THAT SHOULD BE ALIGNED HORIZONTALLY, ALIGN THEM
    utils.align_tops(all_boxes)
    # RESORT NOW THAT THINGS ARE ALIGNED...
    all_boxes = sorted(all_boxes, key=lambda x: (x[0][1], x[0][0]))
    utils.write_images(image, all_boxes, output_path, i)

# process_audio.get_audio("bla bla bla", 'blaaa.mp3', '/users/josh.flori/desktop/')
print('Dont forget to turn off the custom model!!!!!!!!')