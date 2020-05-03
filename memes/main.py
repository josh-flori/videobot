from memes import get_image_data_from_reddit, process_text, process_frames, utils, config, process_audio, make_video
import os
import cv2
import shelve
from google.cloud import automl

os.environ[
    'GOOGLE_APPLICATION_CREDENTIALS'] = '/users/josh.flori/pycharmprojects/reddit-vision-239200-50adace0d3bf.json'
# model_client = automl.AutoMlClient()
# model_full_id = model_client.model_path(config.custom_model_project_id, "us-central1", config.custom_model_model_id)
# response = model_client.deploy_model(model_full_id)

# print("Model deployment finished. {}".format(response.result()))


os.environ['ACCESS_KEY'] = config.aws_ACCESS_KEY
os.environ['SECRET'] = config.aws_SECRET
os.environ['region'] = config.aws_region

meme_path = '/users/josh.flori/desktop/memes/'
meme_output_path = '/users/josh.flori/desktop/memes_output/'
audio_output_path = '/users/josh.flori/desktop/mp3_output/'
padding_dir = '/users/josh.flori/desktop/'
limit = 8

# GET IMAGE DATA FROM REDDIT

# get_image_data_from_reddit.get_images(meme_path, 'memes', 'week', limit)

print('Dont forget to turn off the custom model!!!!!!!!')
# to be passed to make_video module to determine frame length
all_text_with_pauses = []
all_output_text = []
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
    true_sorted_boxes = utils.true_sort(all_boxes)
    print(true_sorted_boxes)
    output_text = utils.write_images(image, true_sorted_boxes, meme_output_path, i)
    print(output_text)
    cleaned_output=utils.clean_output_text(output_text)
    all_output_text.append(cleaned_output)
    ############
    # PART 4: CREATE AUDIO CLIPS
    ############
    # CONVERT ALL_BOXES INTO TEXTUAL REPRESENTATION OF WHAT IS HAPPENING
    space_text_output = utils.space_text(true_sorted_boxes)
    # CONVERT THAT INTO TEXT THAT CAN BE FED TO AUDIO FUNCTION
    text_with_pauses = utils.matchupwhatever(space_text_output, human_readable_text)
    all_text_with_pauses += text_with_pauses
    process_audio.create_mp3s(text_with_pauses, i, audio_output_path, padding_dir)

os.remove(meme_output_path + '.DS_Store')
os.remove(audio_output_path + '.DS_Store')
durations = make_video.get_frame_duration(audio_output_path)
make_video.create_video(durations, meme_output_path)

# response = model_client.undeploy_model(model_full_id)
# print("Model un-deployment finished. {}".format(response.result()))


#
# filename='/users/josh.flori/desktop/shelve.out'
# my_shelf = shelve.open(filename,'n') # 'n' for new
#
# for key in dir():
#     try:
#         my_shelf[key] = globals()[key]
#     except TypeError:
#         #
#         # __builtins__, my_shelf, and imported modules can not be shelved.
#         #
#         print('ERROR shelving: {0}'.format(key))
# my_shelf.close()
#
#
# my_shelf = shelve.open(filename)
# for key in my_shelf:
#     globals()[key]=my_shelf[key]
# my_shelf.close()
