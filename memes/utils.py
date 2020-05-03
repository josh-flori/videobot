import cv2
import numpy as np


def align_tops(all_boxes):
    """ Align boxes which should be on the same line. Helps sorting work correctly. """
    for i in range(1, len(all_boxes)):
        area_cur = (all_boxes[i][1][0] - all_boxes[i][0][0]) * (all_boxes[i][1][1] - all_boxes[i][0][1])
        area_prev = (all_boxes[i - 1][1][0] - all_boxes[i - 1][0][0]) * (
                all_boxes[i - 1][1][1] - all_boxes[i - 1][0][1])
        if abs((area_cur - area_prev) / area_cur) < .05 and abs(all_boxes[i][0][1] - all_boxes[i - 1][0][1]) < 20:
            print('aligning..')
            all_boxes[i][0] = (all_boxes[i][0][0], all_boxes[i - 1][0][1])


def is_a_sliver(all_boxes, i):
    """  """
    if all_boxes[i][1][1] - all_boxes[i][0][1] < 20:
        sliver = True
    else:
        sliver = False
    return sliver


def is_in_frame(all_boxes, i):
    """ Checks if box is within a frame. we have to return the frame it is in for use in write_images()....
     that helps us determine which text is in which image which is useful for determining the time
     needed to wait for each frame"""
    in_any_box = [all([all_boxes[i][0][0] > box[0][0], all_boxes[i][0][1] > box[0][1], all_boxes[i][1][0] <
                       box[1][0], all_boxes[i][1][1] < box[1][1]]) for box in all_boxes]
    in_frame = any(in_any_box)
    which = np.where(in_any_box)
    return in_frame, which


def has_any_text(all_boxes, i):
    """ basically the exact same as is_in_frame but flipped around because im stupid coder and do things backward """
    has_text = any([all([all_boxes[i][0][0] < box[0][0], all_boxes[i][0][1] < box[0][1], all_boxes[i][1][0] >
                         box[1][0], all_boxes[i][1][1] > box[1][1]]) for box in all_boxes])
    return has_text


def true_sort(all_boxes):
    """ The purpose of this function is to true sort all_boxes where everything within each frame will be sorted
        together, otherwise the previous behavior was to give precedent to frames which were on the same line
        and only after sorting frames, text came next. that wasn't a problem with write images because text wasn't being
        displayed if in a frame, but we abandon that paradigm because otherwise space_text wouldn't work."""
    true_sort_boxes = []
    i = 0
    for box in all_boxes:
        # 255 denotes frame
        if box[2][1] == 255:
            true_sort_boxes.append(box)
        if box[2][1] != 255 and box not in true_sort_boxes:
            true_sort_boxes.append(box)
        for boxx in all_boxes[i + 1:]:
            boxx_in_box = all(
                [boxx[0][0] > box[0][0], boxx[0][1] > box[0][1], boxx[1][0] < box[1][0], boxx[1][1] < box[1][1]])
            if boxx_in_box and boxx[2][1] != 255:
                true_sort_boxes.append(boxx)
        i += 1

    return true_sort_boxes


def write_images(image, all_boxes, output_path, img_num):
    """ Creates boxes over image.
        Boxes of form [ [(top_left_xy),(bottom_right_xy),(rgb)] ,...]"""
    cv2.imwrite(output_path + str(img_num) + "." + str(len(all_boxes) + 1) + '.jpg', image)
    output_text = []
    # dump is used to concat together multiple text boxes that are within a frame
    dump = []
    previous_which = ''
    for i in reversed(range(len(all_boxes))):
        in_frame, which = is_in_frame(all_boxes, i)
        is_sliver = is_a_sliver(all_boxes, i)
        has_text=has_any_text(all_boxes, i)
        if not in_frame and not is_sliver:
            # true when first text was in frame and next is not
            if dump != []:
                output_text.append(dump)
                dump = []
                previous_which = ''
            # true if box is text, box may not be text
            if all_boxes[i][2][1] == 0:
                output_text.append([all_boxes[i][3]])
            elif not has_text:
                output_text.append([['empty']])

            image = cv2.rectangle(image, all_boxes[i][0], all_boxes[i][1], all_boxes[i][2], -1)
            cv2.imwrite(output_path + str(img_num) + "." + str(i + 1) + '.jpg', image)
        # make sure it's not a stupid sliver that doesn't need to exist
        elif all_boxes[i][2][1] == 0:
            # print(all_boxes[i][3])
            # print(previous_which)
            # print(which)
            # print(dump)
            if previous_which == '':
                dump.append(all_boxes[i][3])
                previous_which = which
                # print('yup')
            elif which == previous_which:
                dump.append(all_boxes[i][3])
                previous_which = which
                # print('p')
            else:
                output_text.append(dump)
                previous_which = ''
                dump = []
                dump.append(all_boxes[i][3])
                # print('ysdfsdp')
                # print(dump)
    # i don't think you need to check both these conditions but it's easier than me trying to figure out if they
    # would ever both be true. we have to append dump for the final iteration because otherwise the loop doesn't
    # catch it
    if dump !=[] and dump not in output_text:
        output_text.append(dump)
    return output_text

def clean_output_text(output_text):
    cleaned=list(reversed([' '.join([ii[0] for ii in reversed(i)]) if len(i) > 1 else i[0][0] for i in output_text]))
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
    text_with_pauses = []
    break_count = sum([i.count('\n') for i in human_readable_text])
    text_box_count = space_text_output.count('text')
    assert (break_count == text_box_count)
    i = 0
    x = 0
    for text in space_text_output:
        if text == 'text':
            i += 1
            if i == human_readable_text[x].count('\n'):
                text_with_pauses.append(human_readable_text[x])
                x += 1
                i = 0
        elif text == 'empty_frame':
            text_with_pauses.append('empty')

    text_with_pauses.append('empty')  # stick empty at end for breathing room

    return text_with_pauses
