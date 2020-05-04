import io, re
import numpy as np
from google.cloud import vision


def get_image_text(image_path):
    """ Uses google vision api to return full text from meme image. A credentialled connection must have already been
    created but does not need to be passed. full_response contains a large nested structure of information at
    character level which must be built into words in further functions."""
    with io.open(image_path, 'rb') as image_file:
        content = image_file.read()
    client = vision.ImageAnnotatorClient()
    image = vision.types.Image(content=content)
    full_response = client.document_text_detection(image=image).full_text_annotation
    return full_response


def get_text(paragraph):
    """ Returns: concatenated symbol text into single text string for evaluation by should_exclude(),
                 all confidence scores for each symbol. if mean score < threshold, paragraph is skipped by
                 create_blocks_from_paragraph() """
    p_text = ''
    conf = []
    lookup = {'': '', 'type: LINE_BREAK\n': '\n', 'type: SPACE\n': ' ', 'type: EOL_SURE_SPACE\n': '\n'}
    for word in paragraph.words:
        for symbol in word.symbols:
            p_text += symbol.text
            # TODO - import actual break types and use that somehow
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


def create_blocks_from_paragraph(image_text):
    """ Returns list of (x,y,rgb) bounding boxes for all relevant text in image. """
    boxes = []
    human_readable_text = []
    # Iterate through text object
    for page in image_text.pages:
        for block in page.blocks:
            for paragraph in block.paragraphs:
                verts = paragraph.bounding_box.vertices

                p_text, conf = get_text(paragraph)
                # print(p_text)
                # print(should_exclude(p_text))

                # Pass if text is irrelevant or confidence below threshold
                if not should_exclude(p_text) and np.mean(conf) > .8:
                    # Append to list so we can create audio from it
                    human_readable_text.append(p_text)
                    # Break up multi-line paragraphs
                    if p_text.count('\n') > 0:
                        subd = (verts[2].y - verts[0].y) / p_text.count('\n')
                        for i in range(p_text.count('\n')):
                            boxes.append(
                                [(verts[0].x, int(verts[0].y + (subd * i))),
                                 (verts[2].x, int(verts[0].y + (subd * (i + 1)))),
                                 (255, 0, 0),
                                 [p_text.split('\n')[i]]])
                    # else:
                    # print('skipping')
        return boxes, human_readable_text
