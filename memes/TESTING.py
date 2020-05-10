def create_paragraphs(text_boxes, raw_text, debug=False):
    """" It may be the case that google vision takes some true paragraph like 'my ability to fall asleep at night'
    and turns it into seperate paragraphs. this is a problem because it both slows down the audio and makes it sound
    very unnatural. The goal of this function is to identify any text boxes which should all be a single paragraph
    and combine them into a single text box. The logic works like this: assume sequentiality, which is to say that
    boxes that are in the same paragraph will only ever be next to each other in sequence, the midpoint of a
    given textbox should be within the left/right bounds of the previous box (aligned vertically) AND the vertical
    space between this box and the previous should be no more than .5x the height of the previous box (in fact it
    will usually be very close to 0x higher than he end of the previous box). If all those conditions are true,
    we assume the current box belongs with the previous box even if google doesn't think so (
    damn google).
    We leave text_boxes the way they are a d use text_boxes to alter raw_text. Ok.
    So I guess what you could do is have a variable that stays true UNTIL a text box is not part of the previous one. At
     that point you could find where that text is in raw_text and join everything together between that point and the
     previous point, whether that be the beginning or the previous stop point"""

    def vertically_aligned(i, ii, text_boxes):
        """ Compare two adjacent text boxes to see if they both fall along a vertical line drawn through the midpoint of
        the reference box: i """
        midpoint = text_boxes[i][1][0] - ((text_boxes[i][1][0] - text_boxes[i][0][0]) / 2)
        midpoint_ii = text_boxes[ii][1][0] - ((text_boxes[ii][1][0] - text_boxes[ii][0][0]) / 2)
        is_vertically_aligned = midpoint > text_boxes[ii][0][0] and midpoint < text_boxes[ii][1][0] and not text_boxes[
            i][0][0] > midpoint_ii
        return is_vertically_aligned

    def horizontally_aligned_with_next(i, text_boxes, height_of_current_box):
        """ Compare two adjacent text boxes to see if the next comes vertically within .5 height of previous. """
        return text_boxes[i + 1][0][1] < text_boxes[i][1][1] + (height_of_current_box * .5)

    def horizontally_aligned_with_previous(i, text_boxes, height_of_previous_box):
        """ Compare two adjacent text boxes to see if the next comes vertically within .5 height of previous. """
        return text_boxes[i][0][1] < text_boxes[i - 1][1][1] + (height_of_previous_box * .5)

    # If the whole thing is 1 paragraph, just skip it
    if len(raw_text) == 1:
        return raw_text
    raw_text_output = []
    part_of_previous = False
    for i in range(len(text_boxes)):
        height_of_current_box = text_boxes[i][1][1] - text_boxes[i][0][1]
        # FIRST BOX
        if i == 0:
            # if it is not aligned with
            if not vertically_aligned(i, i + 1, text_boxes):
                raw_text_output.append(raw_text[0])
        # FINAL BOX
        elif i == len(text_boxes) - 1:
            height_of_previous_box = text_boxes[i - 1][1][1] - text_boxes[i - 1][0][1]
            if horizontally_aligned_with_previous(i, text_boxes, height_of_previous_box) \
                    and vertically_aligned(i, i - 1, text_boxes):
                raw_text_output.append(''.join(raw_text[previous_text_index:]))
            else:
                raw_text_output.append(''.join(raw_text[-1]))
        # ALL OTHER BOXES
        else:
            height_of_previous_box = text_boxes[i - 1][1][1] - text_boxes[i - 1][0][1]
            # IF ALIGNED WITH PREVIOUS
            if horizontally_aligned_with_previous(i, text_boxes, height_of_previous_box) \
                    and vertically_aligned(i, i - 1, text_boxes):
                if part_of_previous == False:
                    previous_text_index = \
                        [ii for ii in range(len(raw_text)) if text_boxes[i - 1][3][0] in raw_text[ii]][0]
                    part_of_previous = True
                # IF NOT ALIGNED WITH NEXT
                if not vertically_aligned(i, i + 1, text_boxes) \
                        or not horizontally_aligned_with_next(i, text_boxes, height_of_current_box):
                    # DUMP
                    next_text_index = \
                        [ii for ii in range(previous_text_index, len(raw_text)) if text_boxes[i][
                            3][0] in raw_text[ii]][0]
                    raw_text_output.append(''.join(raw_text[previous_text_index:next_text_index + 1]))
                    part_of_previous = False
                    previous_text_index = next_text_index
            # IF NOT ALIGNED WITH PREVIOUS OR NEXT
            elif not vertically_aligned(i, i + 1, text_boxes) \
                    or not horizontally_aligned_with_next(i, text_boxes, height_of_current_box):
                raw_text_output.append(text_boxes[i][3][0])
            # IF NOT ALIGNED WITH PREVIOUS, MAY BE ALIGNED WITH NEXT
            elif not vertically_aligned(i, i - 1, text_boxes) \
                    or not horizontally_aligned_with_previous(i, text_boxes, height_of_current_box):
                part_of_previous = False
                previous_text_index = [ii for ii in range(len(raw_text)) if text_boxes[i][3][0] in raw_text[ii]][0]
    return raw_text_output

for i in range(0,9):
    image = cv2.imread('/users/josh.flori/desktop/memes/' + str(i) + '.jpg')
    raw_text_response = text.get_image_text_from_google('/users/josh.flori/desktop/memes/' + str(i) + '.jpg')
    text_boxes, raw_text = text.create_blocks_from_paragraph(raw_text_response)
    print(create_paragraphs(text_boxes, raw_text, debug=False))