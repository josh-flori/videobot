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
limit = 3

# GET IMAGE DATA FROM REDDIT

get_image_data_from_reddit.get_images(meme_path, 'memes', 'week', limit)

print('Dont forget to turn off the custom model!!!!!!!!')
for i in range(limit):
    ############
    # PART 1: GET IMAGE API DATA (TEXT/CUSTOM MODEL BOUNDING BOX DATA
    ############

    # LOAD IMAGE
    image = cv2.imread('/users/josh.flori/desktop/memes/' + str(i) + '.jpg')
    # GET IMAGE TEXT FROM GOOGLE API
    image_text_raw = process_text.get_image_text('/users/josh.flori/desktop/memes/' + str(i) + '.jpg')
    # CREATE TEXT BOUNDING BOXES WITH A BUNCH OF RULES AND EXCLUSIONS BUILT IN
    text_boxes, human_readable_text = process_text.create_blocks_from_paragraph(image_text_raw)
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

    ############
    # PART 4: CREATE AUDIO CLIPS
    ############
    print(all_boxes)
    process_audio.create_mp3_per_frame('', str(i) + '.mp3', '/users/josh.flori/desktop/')

    # everything until this line is all tested and works....

def space_text(all_boxes):
    """ This function helps solve the problem of how to get audio mixed in with spaces. We have to loop through the
         boxes and ask whether it is blank or not. If not blank, remove it because it does not need anything special to
         happen to it, if blank, denote empty_frame... then on the other side of this we loop through p_text, matching
         \n up with boxes of text in output... then when we reach an empty frame, we pass that information to the audio
         module so we can stick some extra audio in there... we will need to send all audio to module up UNTIL an
         empty frame. we then need a seperate audio function that will combine all distinct frame-text-mp3s with
         the appropriate empty space at the appropriate places"""
    output = []
    for box in all_boxes:
        # [2] corresponds to box rgb tuple, [1] is the g value. will be 0 for text, 255 for frames
        if box[2][1] == 0:
            output.append('text')
        elif box[2][1] == 255:
            # CHECK IF ANY TEXT IS WITHIN THAT BOX. IF NOT FOUND, DENOTE EMPTY FOR AUDIO SPACING
            if not utils.is_in_frame(all_boxes, box):
                output.append('empty_frame')
            # SKIP - UNIMPORTANT
            else:
                pass
    return output

# I wish i had time to continue this tonight... but i don't... oh well :) i can't be unhappy with myself. i have to
# live within the limits of reality.

print('Dont forget to turn off the custom model!!!!!!!!')
