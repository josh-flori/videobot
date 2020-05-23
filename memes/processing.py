import cv2
import numpy as np
from operator import itemgetter
from memes import config
import os

""" This module exists between frames.py/text.py and creation of the audio and video files. See notes.txt for an 
explanation on how all the text lists fit together. """


def align_tops(all_boxes):
    """ It may be the case that when we pass an image to auto_ml it identifies frames which in reality are on the
    same horizontal line but it offsets them a couple pixels from each other. This is a problem because when we sort
    our boxes to create a linear succession of video frames, frames would be out of order. We need to align the tops
    of frames so that sorting frames into proper succession works correctly. """
    for i in range(1, len(all_boxes)):
        area_cur = (all_boxes[i][1][0] - all_boxes[i][0][0]) * (all_boxes[i][1][1] - all_boxes[i][0][1])
        area_prev = (all_boxes[i - 1][1][0] - all_boxes[i - 1][0][0]) * (
                all_boxes[i - 1][1][1] - all_boxes[i - 1][0][1])
        if all_boxes[i][2][1] == 255 and all_boxes[i - 1][2][1] == 255:
            # abs((area_cur - area_prev) / area_cur) < .1 and
            if abs(all_boxes[i][0][1] - all_boxes[i - 1][0][1]) < 50:
                print('aligning..')
                all_boxes[i][0] = (all_boxes[i][0][0], all_boxes[i - 1][0][1])


def is_in_frame(all_boxes, i):
    """ Checks whether a given box is within an auto_ml identified frame. This should only be true for text boxes.
    The purpose of this is to avoid creating blocks over text boxes if that text is within a frame. This
    is an artistic decision. all_boxes will be at meme level and holds all text and frame boxes. which tells you,
    for any given box (should only apply to text boxes) which other box it resides in (should only apply to frames).
    Expand the edges of each target box just in case the text box extends beyond the frame a teeny little bit. """
    in_any_box = [all([all_boxes[i][0][0] > box[0][0] - 10, all_boxes[i][0][1] > box[0][1] - 10, all_boxes[i][1][0] <
                       box[1][0] + 10, all_boxes[i][1][1] < box[1][1] + 10]) for x, box in enumerate(all_boxes)
                  if x != i]
    in_frame = any(in_any_box)
    which = np.where(in_any_box)
    return in_frame, which


def is_in_frame_text(true_sorted_boxes, text_box):
    """ This is the exact same as is_in_frame() but differs in that this is used in the context of looping through
    text_boxes which will be less than or equal to the length of all_boxes with frames, therefore the mechanism by
    which we check if is in frame must differ since the length of the two differ. We want to exclude the reference
    box (text) from the search since we expand the target boxes (frames), the reference box would always be found in
    the target box"""
    ith = true_sorted_boxes.index(text_box)
    in_any_box = [all([text_box[0][0] > box[0][0] - 10, text_box[0][1] > box[0][1] - 10, text_box[1][0] <
                       box[1][0] + 10, text_box[1][1] < box[1][1] + 10]) for i, box in enumerate(true_sorted_boxes) if
                  i != ith]
    which = np.where(in_any_box)
    return which


def has_any_text(all_boxes, i):
    """ Checks whether a box has any boxes within it. This should only be the case when text is within an
    auto_ml box. The purpose of this is to decide whether the audio for this frame should be empty or not. """
    has_text = any([all([all_boxes[i][0][0] < box[0][0], all_boxes[i][0][1] < box[0][1], all_boxes[i][1][0] >
                         box[1][0], all_boxes[i][1][1] > box[1][1]]) for box in all_boxes])
    return has_text


def true_sort(all_boxes):
    """ The purpose of this function is to true sort all_boxes (comprised of text and auto_ml frames) where everything
    within each frame will be sorted together, in other words, imagine a four panel image with panels in top left,
    top right, bottom left, bottom right, each with text in them. We want the top left to reveal first, then the text
    within that frame. Then top right, then text within that frame. true_sort() accomplishes this.
    box[2][1] == 255 denotes frame,
    box[2][1] != 255 denotes text box"""

    true_sort_boxes = []
    i = 0
    for box in all_boxes:
        if box[2][1] == 255:
            true_sort_boxes.append(box)
        if box[2][1] != 255 and box not in true_sort_boxes:
            true_sort_boxes.append(box)
        # Check if any text boxes contained within that frame. If yes, append to true_sort.
        for boxx in all_boxes[i + 1:]:
            boxx_in_box = all(
                [boxx[0][0] > box[0][0], boxx[0][1] > box[0][1], boxx[1][0] < box[1][0], boxx[1][1] < box[1][1]])
            if boxx_in_box and boxx[2][1] != 255:
                true_sort_boxes.append(boxx)
        i += 1

    return true_sort_boxes


def update_true_sort(true_sorted_boxes):
    """ there's an issue with sorting happening here... if there is text in white region to left of an empty frame,
    sorting does not work. you could make an explicit rule... going through the sorted boxes... and if each box is
    text, if it is not in a frame and is to the left of a frame, move it to be before the subsequent frame... that
    would work..."""
    out = []
    last_frame = -1
    insert_at = 0
    for i in range(len(true_sorted_boxes)):
        if i == 0:
            out.append(true_sorted_boxes[0])
            if true_sorted_boxes[i][2][1] == 255:
                insert_at = 0
                last_frame = true_sorted_boxes[i]
                if true_sorted_boxes[i] not in out:
                    out.append(last_frame)
        else:
            if true_sorted_boxes[i][2][1] == 255:
                insert_at = 0
                last_frame = true_sorted_boxes[i]
                if true_sorted_boxes[i] not in out:
                    out.append(last_frame)
            if true_sorted_boxes[i][2][1] == 0 and last_frame != -1 and not is_in_frame(true_sorted_boxes, i)[0]:
                last_frame_i = out.index(last_frame)
                aside_frame = true_sorted_boxes[i][0][1] > last_frame[0][1] and true_sorted_boxes[i][1][1] < \
                              last_frame[1][1]
                if aside_frame:
                    print(true_sorted_boxes[i])
                    if insert_at == 0:
                        out.insert(last_frame_i, true_sorted_boxes[i])
                        insert_at = last_frame_i
                    else:
                        out.insert(insert_at, true_sorted_boxes[i])
                    insert_at += 1
                else:
                    out.append(true_sorted_boxes[i])
            elif true_sorted_boxes[i][2][1] != 255:
                out.append(true_sorted_boxes[i])
    return out


def write_images(image, true_sorted_boxes, output_path, img_num):
    """ Creates images in succession with each boxed element being unveiled slide after slide. Also returns
    slide_text which is the entire text string for that given unveiled video slide. This differs from and will be
    equal to or less than the text used to create the chunks of audio. For instance given a leading paragraph like:
    'me waiting for the lifegaurd\nto give me the green light\n to go down the slide:'.... each of the three sections
    split at newlines would represent a distinct slide (distinct image in the video) but it all represents (in this
    theoretical example) a single paragraph object from the google vision api. paragraphs are are what are passed to
    the audio api. so the entire thing is send at once for a single mp3 but there are three distinct slides. the
    length of the audio has to be distributed across all relevant subtexts to determine the length of each slide.
    that is the purpose of slide_text. sub_slide_text will append together all of the lines of text that are within a
    frame. that must be treated as a single slide since it is - all the text across multiple lines will display at
    once if it is within a frame - this is contrary to text that is outside of a frame.
    slide text will be of form: [[empty],[text,text],[text]...], here is a specific example:
    ['first_frame', 'what kim jong un saw before', 'the sedatives kicked in', 'empty']

    which tells you, for any given box (should only apply to text boxes) which other box it resides in (should only
    apply to frames). this is use to determine which subtexts in frames exist together. if previous_which==which then
    that means the current text in the loop exists in the same frame as text from the previous loop and BOTH of
    those, up until all text in that frame, are the text for that SLIDE and act as a single entity within slide_text. """
    # Create the final slide with no rectangles covering anything up.
    cv2.imwrite(output_path + str(img_num) + "." + str(len(true_sorted_boxes) + 100) + '.jpg', image)
    slide_text = []
    sub_slide_text = []
    previous_which = ''
    for i in reversed(range(len(true_sorted_boxes))):
        in_frame, which = is_in_frame(true_sorted_boxes, i)
        has_text = has_any_text(true_sorted_boxes, i)
        # if in frame and next frame is box, don't do
        if i > 0:
            next_box_is_frame = true_sorted_boxes[i - 1][2][1] == 255
        else:
            next_box_is_frame = False
        if true_sorted_boxes[i][2][1] == 0 and next_box_is_frame and in_frame:
            slide_text.append([true_sorted_boxes[i][3]])
            print(true_sorted_boxes[i])
            print(in_frame)
            print(which)
        else:
            # true when first text was in frame and next is not
            if sub_slide_text != []:
                slide_text.append(sub_slide_text)
                sub_slide_text = []
                previous_which = ''
            # true if box is text, box may not be text
            if true_sorted_boxes[i][2][1] == 0:
                slide_text.append([true_sorted_boxes[i][3]])
            elif not has_text:
                slide_text.append([['empty']])
            image = cv2.rectangle(image, true_sorted_boxes[i][0], true_sorted_boxes[i][1], true_sorted_boxes[i][2], -1)
            cv2.imwrite(output_path + str(img_num) + "." + str(i + 100) + '.jpg', image)  # add 100 so when we run

        # video.createvideo the sorted() function doens't stick 1.10.jpg in front of 1.2.jpg >:[
    #     # make sure it's not a stupid sliver that doesn't need to exist
    #     elif all_boxes[i][2][1] == 0:
    #         # DEBUGGING
    #         # print(all_boxes[i][3])
    #         # print(previous_which)
    #         # print(which)
    #         # print(sub_slide_text)
    #         if previous_which == '':
    #             sub_slide_text.append(all_boxes[i][3])
    #             previous_which = which
    #             # DEBUGGING
    #             # print('yup')
    #         elif which == previous_which:
    #             sub_slide_text.append(all_boxes[i][3])
    #             previous_which = which
    #             # DEBUGGING
    #             # print('p')
    #         # true on the first text that is not part of the previous frame
    #         else:
    #             slide_text.append(sub_slide_text)
    #             previous_which = ''
    #             sub_slide_text = []
    #             sub_slide_text.append(all_boxes[i][3])
    #             # DEBUGGING
    #             # print('ysdfsdp')
    #             # print(sub_slide_text)
    # # i don't think you need to check both these conditions but it's easier than me trying to figure out if they
    # # would ever both be true. we have to append sub_slide_text for the final iteration because otherwise the loop doesn't
    # # catch it
    # if sub_slide_text != [] and sub_slide_text not in slide_text:
    #     slide_text.append(sub_slide_text)
    slide_text.append([['first_frame']])
    return slide_text


def clean_slide_text(slide_text):
    """ I guess this just reverses slide_text though im not sure why that's important. The reason we have two list
    comps is because slide_text has both first and second order lists, like: [[empty],[text,text]...]... so the
    nested list comp reverses the nested text in slide_text... """
    cleaned = list(reversed([' '.join([ii[0] for ii in reversed(i)]) if len(i) > 1 else i[0][0] for i in slide_text]))
    return cleaned


def encode_box_text_type(all_boxes):
    """ To make a real video, we need empty audio files for slides where there is no text. Accomplishing this is a two
    part process.
    First, this function will return either 'text' if a given box has text or 'empty' otherwise. For a slide_text of:
    ['first_frame', 'what kim jong un saw before', 'the sedatives kicked in', 'empty']
    the output from this function looks like this, where first_frame HAS NO PLACEHOLDER:
    ['text', 'text', 'empty']
    Second, since box text may exist at a sub-slide level (text from multiple boxes may exist within a slide),
    we use the subsequent get_audio_text() function to determine if the overall slide itself is empty """
    box_text_type = []
    i = 0
    for box in all_boxes:
        # [2] corresponds to box rgb tuple, [1] is the g value. will be 0 for text, 255 for frames
        if box[2][1] == 0:
            box_text_type.append('text')
        elif box[2][1] == 255:
            # CHECK IF ANY TEXT IS WITHIN THAT BOX. IF NOT FOUND, DENOTE EMPTY FOR AUDIO SPACING
            if not has_any_text(all_boxes, i):
                box_text_type.append('empty')
            # SKIP - UNIMPORTANT
            else:
                pass
        i += 1
    return box_text_type


def get_audio_text(box_text_type, raw_text):
    """ The purpose of this function is to come after encode_box_text_type... it will take all text from p_text
        (raw_text) and line up the boxes from all_boxes with the text, inserting 'empty' where
        there should be an empty frame... then this gets passed to the audio function"""
    audio_text = []
    break_count = sum([i.count('\n') for i in raw_text])
    text_box_count = box_text_type.count('text')
    assert (break_count == text_box_count)
    i = 0
    x = 0
    for text in box_text_type:
        if text == 'text':
            i += 1
            if i == raw_text[x].count('\n'):
                audio_text.append(raw_text[x])
                x += 1
                i = 0
        elif text == 'empty':
            audio_text.append('empty')

    return audio_text


def rerank(raw_text, true_sorted_boxes):
    """ The purpose of this function is to update the order of raw_text according to how the boxes have changed
    position, if at all. Remember that raw_text and text_boxes are generated at the same time and then raw_text is
    passed off to create audio, but then the text_boxes are combined with frame_boxes and the order of the text may
    be change through sorting, but this is indepedent from the raw_text. Thus, your audio and slides may become out
    of order. So, when we produce our text_boxes, we pass in what the RANK of that text was out of the original
    ordered raw_text, where there is 1 rank for each text box, less than or equal to the number of paragraph texts.
    This function will first split the raw_text on '\n' and also append the number indicating which paragraph it came
    from. Then, we re-order the texts according to the updated rank (new_rank) obtained from true_sorted boxes. Then,
    for all texts within each original p_text, we combine them back into paragraphs so the audio function can read it
    correctly. """
    # Get updated rank
    ranks = [i[4] for i in true_sorted_boxes if i[2][1] == 0]

    # Split out raw_text on newline so it matches the number of ranked elements above, but keep information regarding
    # which paragraph it belonged to so they can be joined later.
    split_out = []
    for i in range(len(raw_text)):
        for ii in raw_text[i].split('\n'):
            if ii != '':
                split_out.append([ii, i])

    reordered_raw_text = [split_out[i] for i in ranks]

    indexes = []
    for i in reordered_raw_text:
        if i[1] not in indexes:
            indexes.append(i[1])

    joined_text = []
    for num in indexes:
        joined_text.append('\n'.join([i[0] for i in reordered_raw_text if i[1] == num]))
    joined_text = [i + '\n' for i in joined_text]
    return joined_text


def set_amazon_envs():
    os.environ['ACCESS_KEY'] = config.aws_ACCESS_KEY
    os.environ['SECRET'] = config.aws_SECRET
    os.environ['region'] = config.aws_region


def clear_dirs(meme_output_path, audio_output_path, video_out_path):
    for f in os.listdir(meme_output_path):
        os.remove(meme_output_path + f)
    for f in os.listdir(audio_output_path):
        os.remove(audio_output_path + f)
    for f in os.listdir(video_out_path):
        if f[0:3] == 'out':
            os.remove(video_out_path + f)



