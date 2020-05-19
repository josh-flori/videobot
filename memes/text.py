import io, re
import numpy as np
from google.cloud import vision

""" The purpose of this module is to return meme text using google vision api, combine with some exclusion rules to 
ignore irrelevant text and return bounding a list of bounding boxes around all relevant text boxes. Text boxes are 
combined with frame boxes from frames.py to create a total list of boxes needed to unveil the meme, bit by bit. """


def get_image_text_from_google(image_path):
    """ Uses google vision api to return full text from meme image. A credentialled connection must have already been
    created but does not need to be passed. full_response contains a large nested structure of text information at
    character level which must be built into words in further functions."""
    with io.open(image_path, 'rb') as image_file:
        content = image_file.read()
    client = vision.ImageAnnotatorClient()
    image = vision.types.Image(content=content)
    raw_text_response = client.document_text_detection(image=image).full_text_annotation
    return raw_text_response


def slide_text(paragraph):
    """ get_image_text_from_google() returns text at character level. This function concatenates those symbols into a
    single, human-readable chunk of text.

    paragraph: One of many nested objects returned from get_image_text_from_google(), containing textual symbols to
    be parsed. """
    p_text = ''
    conf = []
    lookup = {'': '', 'type: LINE_BREAK\n': '\n', 'type: SPACE\n': ' ', 'type: EOL_SURE_SPACE\n': '\n',
              'type: HYPHEN\n': '\n'}
    for word in paragraph.words:
        for symbol in word.symbols:
            p_text += symbol.text
            # TODO - import actual break types and use that instead of string values
            p_text += lookup[str(symbol.property.detected_break)]
            conf.append(symbol.confidence)
    return p_text, conf


def add_period(p_text):
    """ The purpose of this function is to add periods for proper audio spacing, so for instance given this
    paragraph: '"A degree in art is useless"\nMe as an art major:\n', we would want to add a period after the word
    useless so the audio module creates natural sounding speech. The idea is to create pauses where needed."""
    quote_count = 0
    p_text_output = ''
    for i in range(len(p_text)):
        if p_text[i] != '"':
            p_text_output += p_text[i]
        elif p_text[i] == '"' and quote_count == 0:
            p_text_output += p_text[i]
            quote_count += 1
        elif p_text[i] == '"' and quote_count == 1:
            p_text_output += '.'
            p_text_output += p_text[i]
            quote_count = 0
    return p_text_output


def should_exclude(p_text):
    """ Returns True if paragraph text is evaluated as garbage. """
    exclude = any([p_text == 'Details',
                   re.search('u/.*?', p_text) is not None,
                   re.search('@.*', p_text) is not None,
                   re.search('imgflip.com', p_text) is not None,
                   re.search('[0-9] hours ago', p_text) is not None,
                   re.search('mematic', p_text) is not None,
                   re.search('www', p_text) is not None,
                   re.search('made with love', p_text) is not None,
                   p_text.isdigit(),
                   p_text.strip().replace('-', '').isdigit(),
                   p_text.strip().lower() == 'srgrafo',
                   'adultswim' in p_text,
                   p_text.strip() == 'ORSAIR',
                   '[deleted]' in p_text,
                   'Ad ' in p_text,
                   re.search('[0-9]{1,2}:[0-9]{2}', p_text) is not None and len(p_text) <= 5,
                   re.search('[0-9]{1,2}, [0-9]{4} AT [0-9]{1,2}:[0-9]{1,2}', p_text) is not None,
                   p_text == "I'm Luis! ^_^\n",
                   p_text == "June 20, 2017 Science\n",
                   p_text == "GAME THRONES\n"])
    return exclude


def create_blocks_from_paragraph(raw_text_response):
    """ Returns a list of (x,y,rgb,text) bounding boxes for all relevant text in image. Returning raw_text
    and putting the text in the image block is slightly redundant, but each have their purposes."""
    text_boxes = []
    raw_text = []
    # Iterate through text object returned by get_image_text_from_google()
    for page in raw_text_response.pages:
        for block in page.blocks:
            for paragraph in block.paragraphs:
                verts = paragraph.bounding_box.vertices
                p_text, conf = slide_text(paragraph)
                p_text = add_period(p_text)
                # DEBUGGING
                # print(p_text)
                # print(should_exclude(p_text))

                if not should_exclude(p_text) and np.mean(conf) > .8:
                    raw_text.append(p_text)
                    # Break up multi-line paragraphs
                    if p_text.count('\n') > 0:
                        # Split multi-line text into equal sized vertical sections to create greater visual appeal
                        subd = (verts[2].y - verts[0].y) / p_text.count('\n')
                        for i in range(p_text.count('\n')):
                            text_boxes.append(
                                [(verts[0].x, int(verts[0].y + (subd * i))),
                                 (verts[2].x, int(verts[0].y + (subd * (i + 1)))),
                                 (255, 0, 0),
                                 [p_text.split('\n')[i]]])
                    # DEBUGGING
                    # else:
                    # print('skipping')
        return text_boxes, raw_text


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
    damn google). We also check left alignment.
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
                                                                                                                i][0][
                                                                                                                0] > midpoint_ii
        return is_vertically_aligned

    def horizontally_aligned_with_next(i, text_boxes, height_of_current_box):
        """ Compare two adjacent text boxes to see if the next comes vertically within .5 height of previous. """
        return text_boxes[i + 1][0][1] < text_boxes[i][1][1] + (height_of_current_box * .5)

    def horizontally_aligned_with_previous(i, text_boxes, height_of_previous_box):
        """ Compare two adjacent text boxes to see if the next comes vertically within .5 height of previous. """
        return text_boxes[i][0][1] < text_boxes[i - 1][1][1] + (height_of_previous_box * .5)

    def left_aligned(i, ii, text_boxes):
        width_refrence_box = text_boxes[i][1][0] - text_boxes[i][0][0]
        return abs(text_boxes[i][0][0] - text_boxes[ii][0][0]) < width_refrence_box / 4

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
            if not vertically_aligned(i, i + 1, text_boxes) or not \
                    horizontally_aligned_with_next(i, text_boxes, height_of_current_box):
                raw_text_output.append(raw_text[0])
        # FINAL BOX
        elif i == len(text_boxes) - 1:
            height_of_previous_box = text_boxes[i - 1][1][1] - text_boxes[i - 1][0][1]
            if left_aligned(i, i - 1, text_boxes) and horizontally_aligned_with_previous(i, text_boxes,
                                                                                         height_of_previous_box) \
                    and vertically_aligned(i, i - 1, text_boxes):
                raw_text_output.append(''.join(raw_text[previous_text_index:]))
            else:
                raw_text_output.append(''.join(raw_text[-1]))
        # ALL OTHER BOXES
        else:
            height_of_previous_box = text_boxes[i - 1][1][1] - text_boxes[i - 1][0][1]
            # IF ALIGNED WITH PREVIOUS
            if left_aligned(i, i - 1, text_boxes) and horizontally_aligned_with_previous(i, text_boxes,
                                                                                         height_of_previous_box) \
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


def add_newline(raw_text):
    """ It happens that the assertion in get_audio_text() basically requires each paragraph end in \n since thats how
    most of them are. This function just appends \n to anything that doesn't have it. """
    out = []
    for p_text in raw_text:
        if p_text[-1:] != '\n':
            out.append(p_text + '\n')
        else:
            out.append(p_text)
    return out


def sort_text(text_boxes):
    """" It just so happens that magically, most of the time, the raw_text returned from google is in the exactly
    proper sequence and I have not had to align or sorrt it in any way until now. But it happens 4 panel memes
    (and more im sure) that one text paragraphs on left may be slightly lower than text panel on right causing the
    raw text to go in that backward order. Thus, we need to sort any paragraphs that are very close to each other on
    a line. This works similar to processing.align_tops."""
    for i in range(1, len(text_boxes)):
        height_cur = text_boxes[i][1][1] - text_boxes[i][0][1]
        height_prev = text_boxes[i - 1][1][1] - text_boxes[i - 1][0][1]
        if abs(height_cur - height_prev) < 10 and abs(text_boxes[i][0][1] - text_boxes[i - 1][0][1]) < 30:
            text_boxes[i][0] = (text_boxes[i][0][0], text_boxes[i - 1][0][1])
    sorted_boxes = sorted(text_boxes, key=lambda x: (x[0][1], x[0][0]))
    return [i[3][0]+'\n' for i in sorted_boxes]
