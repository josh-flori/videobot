import cv2
import numpy as np

""" This module does a variety of different processing steps between process_frames and process_text the image boxes 
and the actual creation of the audio and video files."""


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
    is an artistic decision. """
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
    """ Creates images in succession with each boxed element being unveiled frame after frame. Also returns
    frame_text which is the entire text string for that given unveiled video frame. This differs and will be equal to or
    less than the text used to create the chunks of audio. Frame text and audio text will be used jointly to
    determine how long the duration of each frame should be.

    So I think the whole deal with dump is like, frame_text will be of form [[empty],[text,text]...] and this tells
    you about the text for a given slide. TODO - RENAME THIS FROM FRAME TO SLIDE, or something, stop using frame for
    both video frames and auto_ml frames. confusing. ... and this will be passed to create the audio... blabla im
    tired...
    which will not necessarily always have a non-empty value. if that given text box is not in a frame, it will be
    empty"""
    # Create the final frame with no rectangles covering anything up.
    cv2.imwrite(output_path + str(img_num) + "." + str(len(all_boxes) + 1) + '.jpg', image)
    frame_text = []
    # dump is used to concat together multiple text boxes that are within a frame
    dump = []
    previous_which = ''
    for i in reversed(range(len(all_boxes))):
        in_frame, which = is_in_frame(all_boxes, i)
        is_sliver = is_a_sliver(all_boxes, i)
        has_text = has_any_text(all_boxes, i)
        if not in_frame and not is_sliver:
            # true when first text was in frame and next is not
            if dump != []:
                frame_text.append(dump)
                dump = []
                previous_which = ''
            # true if box is text, box may not be text
            if all_boxes[i][2][1] == 0:
                frame_text.append([all_boxes[i][3]])
            elif not has_text:
                frame_text.append([['empty']])

            image = cv2.rectangle(image, all_boxes[i][0], all_boxes[i][1], all_boxes[i][2], -1)
            cv2.imwrite(output_path + str(img_num) + "." + str(i + 1) + '.jpg', image)
        # make sure it's not a stupid sliver that doesn't need to exist
        elif all_boxes[i][2][1] == 0:
            # DEBUGGING
            # print(all_boxes[i][3])
            # print(previous_which)
            # print(which)
            # print(dump)
            if previous_which == '':
                dump.append(all_boxes[i][3])
                previous_which = which
                # DEBUGGING
                # print('yup')
            elif which == previous_which:
                dump.append(all_boxes[i][3])
                previous_which = which
                # DEBUGGING
                # print('p')
            else:
                frame_text.append(dump)
                previous_which = ''
                dump = []
                dump.append(all_boxes[i][3])
                # DEBUGGING
                # print('ysdfsdp')
                # print(dump)
    # i don't think you need to check both these conditions but it's easier than me trying to figure out if they
    # would ever both be true. we have to append dump for the final iteration because otherwise the loop doesn't
    # catch it
    if dump != [] and dump not in frame_text:
        frame_text.append(dump)
    frame_text.append([['first_frame']])
    return frame_text


def clean_frame_text(frame_text):
    """ I guess this just reverses frame_text though im not sure why that's important. The reason we have two list
    comps is because frame_text has both first and second order lists, like: [[empty],[text,text]...]... so the
    nested list comp reverses the nested text in frame_text... """
    cleaned = list(reversed([' '.join([ii[0] for ii in reversed(i)]) if len(i) > 1 else i[0][0] for i in frame_text]))
    return cleaned


def space_text(all_boxes):
    """ This function helps solve the problem of how to get audio mixed in with spaces. We have to loop through the
         boxes and ask whether it is blank or not. If not blank, remove it because it does not need anything special to
         happen to it, if blank, denote empty_frame... then on the other side of this we loop through p_text, matching
         \n up with boxes of text in output... then when we reach an empty frame, we pass that information to the audio
         module so we can stick some extra audio in there... we will need to send all audio to module up UNTIL an
         empty frame. we then need a seperate audio function that will combine all distinct frame-text-mp3s with
         the appropriate empty space at the appropriate places"""
    space_text_output = []
    i = 0
    for box in all_boxes:
        # [2] corresponds to box rgb tuple, [1] is the g value. will be 0 for text, 255 for frames
        if box[2][1] == 0:
            space_text_output.append('text')
        elif box[2][1] == 255:
            # CHECK IF ANY TEXT IS WITHIN THAT BOX. IF NOT FOUND, DENOTE EMPTY FOR AUDIO SPACING
            if not has_any_text(all_boxes, i):
                space_text_output.append('empty_frame')
            # SKIP - UNIMPORTANT
            else:
                pass
        i += 1
    return space_text_output


def matchupwhatever(space_text_output, human_readable_text):
    """ The purpose of this function is to come after space_text... it will take all text from p_text
        (human_readable_text) and line up the boxes from all_boxes with the text, inserting 'empty' where
        there should be an empty frame... then this gets passed to the audio function"""
    audio_text = []
    break_count = sum([i.count('\n') for i in human_readable_text])
    text_box_count = space_text_output.count('text')
    assert (break_count == text_box_count)
    i = 0
    x = 0
    for text in space_text_output:
        if text == 'text':
            i += 1
            if i == human_readable_text[x].count('\n'):
                audio_text.append(human_readable_text[x])
                x += 1
                i = 0
        elif text == 'empty_frame':
            audio_text.append('empty')

    return audio_text
