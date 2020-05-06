from memes import reddit, text, frames, processing, config, audio, make_video
import os
import cv2
from google.cloud import automl

os.environ[
    'GOOGLE_APPLICATION_CREDENTIALS'] = '/users/josh.flori/pycharmprojects/reddit-vision-239200-50adace0d3bf.json'
model_client = automl.AutoMlClient()
model_full_id = model_client.model_path(config.custom_model_project_id, "us-central1", config.custom_model_model_id)
response = model_client.deploy_model(model_full_id)

print("Model deployment finished. {}".format(response.result()))

os.environ['ACCESS_KEY'] = config.aws_ACCESS_KEY
os.environ['SECRET'] = config.aws_SECRET
os.environ['region'] = config.aws_region

meme_path = '/users/josh.flori/desktop/memes/'
meme_output_path = '/users/josh.flori/desktop/memes_output/'
audio_output_path = '/users/josh.flori/desktop/mp3_output/'
padding_dir = '/users/josh.flori/desktop/'
output_audio_fname = 'out.mp3'
limit = 1

# GET IMAGE DATA FROM REDDIT

# get_image_data_from_reddit.get_images(meme_path, 'memes', 'week', limit)

all_audio_text = []  # chunked text at paragraph level to create audio files

for i in range(limit):
    # PART 1: GET MEME DATA FROM APIs (VISION & AUTO_ML)
    image = cv2.imread('/users/josh.flori/desktop/memes/' + str(i) + '.jpg')
    raw_text_response = text.get_image_text_from_google('/users/josh.flori/desktop/memes/' + str(i) + '.jpg')
    text_boxes, raw_text = text.create_blocks_from_paragraph(raw_text_response)
    annotation = frames.get_frame_prediction_from_google(meme_path, i, config.custom_model_project_id,
                                                         config.custom_model_model_id)

    # PART 2: CLEAN UP THE DATA
    frames.expand_to_edge(annotation)
    frame_boxes = frames.create_blocks_from_annotations(annotation, image)
    frames.trim_white_space(image, frame_boxes)

    # PART 3: CREATE MASTER LIST OF BOX OBJECTS
    all_boxes = text_boxes + frame_boxes
    all_boxes = sorted(all_boxes, key=lambda x: (x[0][1], x[0][0]))  # SORT BY Y, THEN X
    processing.align_tops(all_boxes)
    all_boxes = sorted(all_boxes, key=lambda x: (x[0][1], x[0][0]))  # RESORT NOW THAT THINGS ARE ALIGNED...
    true_sorted_boxes = processing.true_sort(all_boxes)
    slide_text = processing.write_images(image, true_sorted_boxes, meme_output_path, i)
    slide_text = processing.clean_slide_text(slide_text)

    # PART 4: CREATE AUDIO CLIPS
    box_text_type = processing.encode_box_text_type(true_sorted_boxes)
    audio_text = processing.get_audio_text(box_text_type, raw_text)
    all_audio_text.append(audio_text)
    audio.create_mp3s(audio_text, i, audio_output_path, padding_dir)

    # PART 5: CREATE VIDEO
    slide_durations = make_video.compute_slide_duration(audio_output_path, audio_text, slide_text, i,
                                                        '/users/josh.flori/desktop/padding.mp3')
    make_video.create_video(slide_durations, meme_output_path, audio_output_path, 'out.mp3', i)


response = model_client.undeploy_model(model_full_id)
print("Model un-deployment finished. {}".format(response.result()))
