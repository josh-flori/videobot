import io, re
import numpy as np
from google.cloud import vision

""" The purpose of this module is to return meme text using google vision api, combine with some exclusion rules to 
ignore irrelevant text and return bounding a list of bounding boxes around all relevant text boxes. Text boxes are 
combined with frame boxes from frames.py to create a total list of boxes needed to unveil the image, 
bit by bit. """

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


def parse_text(paragraph):
    """ get_image_text_from_google() returns text at character level. This function concatenates those symbols into a
    single, human-readable chunk of text.

    paragraph: One of many nested objects returned from get_image_text_from_google(), containing textual symbols to
    be parsed. """
    p_text = ''
    conf = []
    lookup = {'': '', 'type: LINE_BREAK\n': '\n', 'type: SPACE\n': ' ', 'type: EOL_SURE_SPACE\n': '\n'}
    for word in paragraph.words:
        for symbol in word.symbols:
            p_text += symbol.text
            # TODO - import actual break types and use that instead of string values
            p_text += lookup[str(symbol.property.detected_break)]
            conf.append(symbol.confidence)
    return p_text, conf


def should_exclude(p_text):
    """ Returns True if paragraph text is evaluated as garbage. """
    exclude = any([p_text == 'Details',
                   re.search('u/.*?', p_text) is not None,
                   re.search('@.*', p_text) is not None,
                   re.search('imgflip.com', p_text) is not None,
                   re.search('[0-9] hours ago', p_text) is not None,
                   re.search('made with mematic', p_text) is not None,
                   re.search('www', p_text) is not None,
                   re.search('made with love', p_text) is not None,
                   p_text.isdigit(),
                   p_text.strip().replace('-', '').isdigit(),
                   p_text.strip().lower() == 'srgrafo',
                   'adultswim' in p_text,
                   p_text.strip() == 'ORSAIR',
                   '[deleted]' in p_text])
    return exclude


def create_blocks_from_paragraph(raw_text_response):
    """ Returns a list of (x,y,rgb,text) bounding boxes for all relevant text in image. Returning human_readable_text
    and putting the text in the image block is slightly redundant, but each have their purposes."""
    boxes = []
    human_readable_text = []
    # Iterate through text object returned by get_image_text_from_google()
    for page in raw_text_response.pages:
        for block in page.blocks:
            for paragraph in block.paragraphs:
                verts = paragraph.bounding_box.vertices
                p_text, conf = parse_text(paragraph)
                # DEBUGGING
                # print(p_text)
                # print(should_exclude(p_text))

                if not should_exclude(p_text) and np.mean(conf) > .8:
                    human_readable_text.append(p_text)
                    # Break up multi-line paragraphs
                    if p_text.count('\n') > 0:
                        # Split multi-line text into equal sized vertical sections to create greater visual appeal
                        subd = (verts[2].y - verts[0].y) / p_text.count('\n')
                        for i in range(p_text.count('\n')):
                            boxes.append(
                                [(verts[0].x, int(verts[0].y + (subd * i))),
                                 (verts[2].x, int(verts[0].y + (subd * (i + 1)))),
                                 (255, 0, 0),
                                 [p_text.split('\n')[i]]])
                    # DEBUGGING
                    # else:
                    # print('skipping')
        return boxes, human_readable_text