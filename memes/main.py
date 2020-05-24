from memes import reddit, text, frames, processing, config, audio, video
import cv2, time, os, tqdm
processing.set_amazon_envs()
processing.clear_dirs(config.meme_output_path, config.audio_output_path, config.video_out_path)

limit = 200
# TODO - you should add a rule where if not majority letters are cap and not majority every word cap, use cap to
#  indicate end of line


# reddit.get_images(config.meme_path, 'memes', 'day', limit)

# all_annotations = []
# frames.deploy(config.model_client, config.model_full_id)
# for i in tqdm.tqdm(range(limit)):
#     annotation = frames.get_frame_prediction_from_google(config.meme_path, i, config.custom_model_project_id,
#                                                          config.custom_model_model_id)
#     time.sleep(.3)
#     all_annotations.append(annotation)
# frames.undeploy(config.model_client, config.model_full_id)
# processing.write_pickle(all_annotations,'annotations.pkl')
# all_annotations = processing.read_pickle('annotations.pkl')


# all_raw_text_responses = []
# for i in tqdm.tqdm(range(limit)):
#     image = cv2.imread(config.meme_path + str(i) + '.jpg')
#     raw_text_response = text.get_image_text_from_google(config.meme_path + str(i) + '.jpg')
#     all_raw_text_responses.append(raw_text_response)
# processing.write_pickle(all_raw_text_responses,'raw_text_responses.pkl')
# all_raw_text_responses=processing.read_pickle('raw_text_responses.pkl')

for i in range(20,200):
    try:
        image = cv2.imread(config.meme_path + str(i) + '.jpg')
        # PART 1: GET MEME DATA FROM APIs (VISION & AUTO_ML)
        raw_text_response=all_raw_text_responses[i]
        text_boxes, raw_text = text.create_blocks_from_paragraph(raw_text_response)
        text_boxes = text.expand_to_edge_text(text_boxes, image)
        # raw_text = text.sort_text(text_boxes,raw_boxes)

        # PART 2: CLEAN UP THE DATA
        annotation = all_annotations[i]
        frames.expand_to_edge(annotation)
        frame_boxes = frames.create_blocks_from_annotations(annotation, image)
        frames.trim_white_space(image, frame_boxes)
        frame_boxes = frames.remove_slivers(frame_boxes)
        frames.remove_unneeded_outer_frame(frame_boxes, image)
        # frame_boxes = frames.remove_overlapping_frames(frame_boxes)

        # PART 3: CREATE MASTER LIST OF BOX OBJECTS
        all_boxes = text_boxes + frame_boxes
        all_boxes = sorted(all_boxes, key=lambda x: (x[0][1], x[0][0]))  # SORT BY Y, THEN X
        processing.align_tops(all_boxes)
        all_boxes = sorted(all_boxes, key=lambda x: (x[0][1], x[0][0]))  # RESORT NOW THAT THINGS ARE ALIGNED...
        true_sorted_boxes = processing.true_sort(all_boxes)
        true_sorted_boxes = processing.update_true_sort(true_sorted_boxes)

        raw_text = text.create_paragraphs(text_boxes, raw_text, true_sorted_boxes, debug=False)
        raw_text = text.add_newline(raw_text)
        raw_text = text.add_period_alt(raw_text,config.language_client)
        raw_text = text.lower_text(raw_text)

        slide_text = processing.write_images(image, true_sorted_boxes, config.meme_output_path, i)
        slide_text = processing.clean_slide_text(slide_text)
        slide_text = text.lower_text(slide_text)

        # print(all_boxes)
        # print(true_sorted_boxes)
        # PART 4: CREATE AUDIO CLIPS
        box_text_type = processing.encode_box_text_type(true_sorted_boxes)
        reordered_raw_text = processing.rerank(raw_text, true_sorted_boxes)
        audio_text = processing.get_audio_text(box_text_type, reordered_raw_text)
        audio.create_mp3s(audio_text, i, config.audio_output_path, config.padding_dir)
        # audio.extend_short_audio(config.audio_output_path, audio_text, i)
        wait_time=audio.extend_all_audio(config.audio_output_path, audio_text, i)

        # PART 5: CREATE VIDEO
        slide_durations = video.compute_slide_durations(config.audio_output_path, audio_text, slide_text, i,
                                                        '/users/josh.flori/desktop/padding.mp3')
        slide_durations = video.readjust_slide_durations(slide_durations,wait_time)
        video.combine_audio(config.audio_output_path, 'out.mp3', i)
        video.create_video(slide_durations, config.meme_output_path, config.audio_output_path, 'out.mp3', i)
    except:
        pass



video.convert_videos(config.video_out_path)