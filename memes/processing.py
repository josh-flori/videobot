import cv2
import numpy as np

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
        if abs((area_cur - area_prev) / area_cur) < .05 and abs(all_boxes[i][0][1] - all_boxes[i - 1][0][1]) < 20:
            print('aligning..')
            all_boxes[i][0] = (all_boxes[i][0][0], all_boxes[i - 1][0][1])


def is_a_sliver(all_boxes, i):
    """  auto_ml sometimes creates a sliver of a block - something small and irrelevant. This discards such boxes."""
    if all_boxes[i][1][1] - all_boxes[i][0][1] < 20:
        sliver = True
    else:
        sliver = False
    return sliver


def is_in_frame(all_boxes, i):
    """ Checks whether a given box is within an auto_ml identified frame. This should only be true for text boxes.
    The purpose of this is to avoid creating blocks over text boxes if that text is within a frame. This
    is an artistic decision. all_boxes will be at meme level and holds all text and frame boxes. which tells you,
    for any given box (should only apply to text boxes) which other box it resides in (should only apply to frames) """
    in_any_box = [all([all_boxes[i][0][0] > box[0][0], all_boxes[i][0][1] > box[0][1], all_boxes[i][1][0] <
                       box[1][0], all_boxes[i][1][1] < box[1][1]]) for box in all_boxes]
    in_frame = any(in_any_box)
    which = np.where(in_any_box)
    return in_frame, which


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


def write_images(image, all_boxes, output_path, img_num):
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
    cv2.imwrite(output_path + str(img_num) + "." + str(len(all_boxes) + 100) + '.jpg', image)
    slide_text = []
    sub_slide_text = []
    previous_which = ''
    for i in reversed(range(len(all_boxes))):
        in_frame, which = is_in_frame(all_boxes, i)
        is_sliver = is_a_sliver(all_boxes, i)
        has_text = has_any_text(all_boxes, i)
        print(i)
        print(all_boxes[i])
        if not in_frame and not is_sliver:
            # true when first text was in frame and next is not
            if sub_slide_text != []:
                slide_text.append(sub_slide_text)
                sub_slide_text = []
                previous_which = ''
            # true if box is text, box may not be text
            if all_boxes[i][2][1] == 0:
                slide_text.append([all_boxes[i][3]])
            elif not has_text:
                slide_text.append([['empty']])

            image = cv2.rectangle(image, all_boxes[i][0], all_boxes[i][1], all_boxes[i][2], -1)
            cv2.imwrite(output_path + str(img_num) + "." + str(i + 100) + '.jpg', image) # add 100 so when we run
            # video.createvideo the sorted() function doens't stick 1.10.jpg in front of 1.2.jpg >:[
        # make sure it's not a stupid sliver that doesn't need to exist
        elif all_boxes[i][2][1] == 0:
            # DEBUGGING
            # print(all_boxes[i][3])
            # print(previous_which)
            # print(which)
            # print(sub_slide_text)
            if previous_which == '':
                sub_slide_text.append(all_boxes[i][3])
                previous_which = which
                # DEBUGGING
                # print('yup')
            elif which == previous_which:
                sub_slide_text.append(all_boxes[i][3])
                previous_which = which
                # DEBUGGING
                # print('p')
            # true on the first text that is not part of the previous frame
            else:
                slide_text.append(sub_slide_text)
                previous_which = ''
                sub_slide_text = []
                sub_slide_text.append(all_boxes[i][3])
                # DEBUGGING
                # print('ysdfsdp')
                # print(sub_slide_text)
    # i don't think you need to check both these conditions but it's easier than me trying to figure out if they
    # would ever both be true. we have to append sub_slide_text for the final iteration because otherwise the loop doesn't
    # catch it
    if sub_slide_text != [] and sub_slide_text not in slide_text:
        slide_text.append(sub_slide_text)
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