import io, re
import numpy as np
from google.cloud import vision
from memes import processing
from google.cloud.language_v1 import enums

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
                   p_text == "GAME THRONES\n",
                   len(p_text) == 2 and p_text[0].isalpha() and p_text[1:] == '\n',
                   p_text == 'MINEL\n',
                   p_text.lower() == 'geely\n',
                   re.search('[0-9]{1,2}.[0-9]{1,2}k', p_text.lower()) is not None,
                   p_text == 'CT\n',
                   p_text.lower() == 'shencomix.com\n'])
    return exclude


def spell_correct(p_text):
    """ The purpose of this function is to correct spelling mistakes. """
    p_text = p_text.lower().replace('attacked.me?', 'attacked me!').replace('shit','shhh').replace('damn',
                                                                                                   'darn').replace(
        'oh my god','oh my gosh').replace('fucking','fing').replace('fuck','ef')
    return p_text


# TODO - update this so if this text in frame and next not in frame, or visaversa, don't stick together
def create_blocks_from_paragraph(raw_text_response):
    """ Returns a list of (x,y,rgb,text) bounding boxes for all relevant text in image. Returning raw_text
    and putting the text in the image block is slightly redundant, but each have their purposes.
    To each text box we also append the rank corresponding to where that chunk of text came from out of the original
    raw_text. This is so when we alter the sorting of the boxes later independent of raw_text, we can pass the
    updated rank back into raw_text for use in the audio module, and so slide/audio are aligned. """
    text_boxes = []
    raw_text = []
    rank = 0
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
                    p_text=spell_correct(p_text)
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
                                 [p_text.split('\n')[i]],
                                 rank])
                            rank += 1
                    # DEBUGGING
                    # else:
                    # print('skipping')
        return text_boxes, raw_text


def create_paragraphs(text_boxes, raw_text, true_sorted_boxes, debug=False):
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
        if i > 0:
            previous_which = processing.is_in_frame_text(true_sorted_boxes, text_boxes[i - 1])
        which = processing.is_in_frame_text(true_sorted_boxes, text_boxes[i])
        if i < len(text_boxes) - 1:
            next_which = processing.is_in_frame_text(true_sorted_boxes, text_boxes[i + 1])
        height_of_current_box = text_boxes[i][1][1] - text_boxes[i][0][1]
        # FIRST BOX
        # print(i)
        # print(which)
        # print(next_which)
        # try:
        #     print(previous_which)
        # except UnboundLocalError:
        #     pass
        if i == 0:
            # if it is not aligned with next, append since it is isolated, else let subsequent code paragraph it.
            if not vertically_aligned(i, i + 1, text_boxes) or not \
                    horizontally_aligned_with_next(i, text_boxes, height_of_current_box) or not np.array_equal(which,
                                                                                                               next_which):
                raw_text_output.append(raw_text[0])
        # FINAL BOX
        elif i == len(text_boxes) - 1:
            height_of_previous_box = text_boxes[i - 1][1][1] - text_boxes[i - 1][0][1]
            # left_aligned(i, i - 1, text_boxes) and
            if horizontally_aligned_with_previous(i, text_boxes,
                                                  height_of_previous_box) \
                    and vertically_aligned(i, i - 1, text_boxes) and np.array_equal(which, previous_which):
                raw_text_output.append(''.join(raw_text[previous_text_index:]))
                print(print(str(i) + '0'))
            else:
                raw_text_output.append(''.join(raw_text[-1]))
                print(str(i) + '1')
        # ALL OTHER BOXES
        else:
            height_of_previous_box = text_boxes[i - 1][1][1] - text_boxes[i - 1][0][1]
            # IF ALIGNED WITH PREVIOUS
            # left_aligned(i, i - 1, text_boxes) and
            if horizontally_aligned_with_previous(i, text_boxes, height_of_previous_box) \
                    and vertically_aligned(i, i - 1, text_boxes) and np.array_equal(which, previous_which):
                if part_of_previous == False:
                    previous_text_index = \
                        [ii for ii in range(len(raw_text)) if text_boxes[i - 1][3][0] in raw_text[ii]][0]
                    part_of_previous = True
                # IF NOT ALIGNED WITH NEXT
                if not vertically_aligned(i, i + 1, text_boxes) \
                        or not horizontally_aligned_with_next(i, text_boxes, height_of_current_box) or \
                        not np.array_equal(which, next_which):
                    # DUMP
                    next_text_index = \
                        [ii for ii in range(previous_text_index, len(raw_text)) if text_boxes[i][
                            3][0] in raw_text[ii]][0]
                    raw_text_output.append(''.join(raw_text[previous_text_index:next_text_index + 1]))
                    part_of_previous = False
                    previous_text_index = next_text_index
            # IF NOT ALIGNED WITH PREVIOUS OR NEXT
            elif (not vertically_aligned(i, i + 1, text_boxes) or not np.array_equal(which, previous_which)) \
                    and (not horizontally_aligned_with_next(i, text_boxes, height_of_current_box) or not
            np.array_equal(which, next_which)):
                raw_text_output.append(text_boxes[i][3][0])
                print(str(i) + 'ya')
            # IF NOT ALIGNED WITH PREVIOUS, MAY BE ALIGNED WITH NEXT
            elif not vertically_aligned(i, i - 1, text_boxes) \
                    or not horizontally_aligned_with_previous(i, text_boxes,
                                                              height_of_current_box) or not np.array_equal(which,
                                                                                                           previous_which):
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


def sort_text(raw_boxes):
    """" It just so happens that magically, most of the time, the raw_text returned from google is in the exactly
    proper sequence and I have not had to align or sort it in any way until now. But it happens in 4 panel memes
    (and more im sure) that one text paragraph on left may be slightly lower than text panel on right causing the
    raw text to go in that backward order. Thus, we need to sort any paragraphs that are very close to each other on
    a line. This works similar to processing.align_tops."""
    for i in range(1, len(raw_boxes)):
        # height_cur = raw_boxes[i][1][1] - raw_boxes[i][0][1]
        # height_prev = raw_boxes[i - 1][1][1] - raw_boxes[i - 1][0][1]
        if abs(raw_boxes[i][0][1] - raw_boxes[i - 1][0][1]) < 30:
            raw_boxes[i][0] = (raw_boxes[i][0][0], raw_boxes[i - 1][0][1])
    sorted_boxes = sorted(raw_boxes, key=lambda x: (x[0][1], x[0][0]))
    raw_text = [i[3][0] for i in sorted_boxes], [i[3][0] for i in sorted_boxes]
    text_boxes = []

    for i in sorted_boxes:
        p_text = i[3][0]
        subd = (i[1][1] - i[0][1]) / p_text.count('\n')
        for ii in range(p_text.count('\n')):
            text_boxes.append(
                [(i[0][0], int(i[0][1] + (subd * ii))),
                 (i[1][0], int(i[0][1] + (subd * (ii + 1)))),
                 (255, 0, 0),
                 [p_text.split('\n')[ii]]])
    return text_boxes, raw_text


def expand_to_edge_text(text_boxes, image):
    """ The purpose of this function is to fix bounding box prediction from google vision. The bounding boxes will
    often be literally OUTSIDE the bounds of the image. In that case, this forces it back to the edge. """
    # have to create temp because i made the stupid decision to use tuples which don't support assignment...
    for i in range(len(text_boxes)):
        temp = []
        if text_boxes[i][0][0] < 0:
            temp.append(1)
        else:
            temp.append(text_boxes[i][0][0])
        if text_boxes[i][0][1] < 0:
            temp.append(1)
        else:
            temp.append(text_boxes[i][0][1])
        text_boxes[i][0] = (temp[0], temp[1])
        temp = []

        if text_boxes[i][1][0] > image.shape[1]:
            temp.append(image.shape[1] - 1)
        else:
            temp.append(text_boxes[i][1][0])
        if text_boxes[i][1][1] > image.shape[0]:
            temp.append(image.shape[0] - 1)
        else:
            temp.append(text_boxes[i][1][1])
        text_boxes[i][1] = (temp[0], temp[1])
    return text_boxes


def add_period_alt(raw_text, client):
    """ The purpose of this function is to help insert pauses into the audio at appropriate places. For instance,
    given this raw_text chunk: 'Me: tries to read Latin\nSatan:\n', you would want a pause after 'Latin' since it is
    the end of the line. The rule here is, if <majority words start with upper case, then at uppercase and after \n,
    insert period, so long as the final character before the next space is a colon ':'. """
    out = []
    # type_ = enums.Document.Type.PLAIN_TEXT
    # encoding_type = enums.EncodingType.UTF8
    # language = "en"

    for chunk in raw_text:
        is_upper = [x[0].isupper() for x in chunk.split(' ')]
        mostly_not_upper = is_upper.count(False) / len(is_upper) > .4
        if mostly_not_upper:
            # document = {"content": chunk, "type": type_, "language": language}
            # response = client.analyze_syntax(document, encoding_type=encoding_type)
            # for i in response.tokens:
            #     if i.part_of_speech.proper==1:
            #         chunk=chunk.replace(i.text.content,i.text.content.lower())
            temp = ''
            for i in range(len(chunk)):
                try:
                    for n in chunk[i + 1:]:
                        if n == ':':
                            colon_before_space = True
                            break
                        elif n == ' ' or n == '\n':
                            colon_before_space = False
                            break
                        else:
                            colon_before_space = False
                    if chunk[i] == '\n' and chunk[i + 1].isupper() and colon_before_space:
                        temp += '.'
                        temp += chunk[i]
                    else:
                        temp += chunk[i]
                except IndexError:
                    temp += chunk[i]
            out.append(temp)
        else:
            out.append(chunk)
    return out


def lower_text(text_list):
    """ The purpose of this is because if you sent something like 'US' to polly it will read it as 'YOU-ESS',
    short for united states. """
    return [i.lower() for i in text_list]
