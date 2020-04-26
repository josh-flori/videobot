import io, re, cv2
import numpy as np
from google.cloud import vision


def get_image_text(image_path):
    """ Returns full text from image. """
    with io.open(image_path, 'rb') as image_file:
        content = image_file.read()
    client = vision.ImageAnnotatorClient()
    image = vision.types.Image(content=content)
    full_response = client.document_text_detection(image=image).full_text_annotation
    return full_response


def find_colon(paragraph):
    """ Returns top right bounding boxes of first colon found in paragraph text.
        Used to create custom block over text like: 'Me: blablabla...
                                                     My Mom: blablabla... """
    for word in paragraph.words:
        for symbol in word.symbols:
            if symbol.text == ':':
                return symbol.bounding_box.vertices[2].x, symbol.bounding_box.vertices[2].y


def get_text(paragraph):
    """ Returns: concatenated symbol text into single text string for evaluation by should_exclude(),
                 all confidence scores for each symbol. if mean score < threshold, paragraph is skipped by
                 create_blocks_from_paragraph() """
    # TODO - is redundantly looping over same shit as find_colon()... not great
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


def create_blocks_from_paragraph(image_text, image, img_num):
    """ Returns list of bounding boxes for all relevant text in image. """
    boxes = []
    # Iterate through text object
    for page in image_text.pages:
        for block in page.blocks:
            for paragraph in block.paragraphs:
                verts = paragraph.bounding_box.vertices

                p_text, conf = get_text(paragraph)
                print(p_text)
                print(should_exclude(p_text))

                # Pass if text is irrelevant or confidence below threshold
                if not should_exclude(p_text) and np.mean(conf) > .8:
                    # Break up multi-line paragraphs
                    if p_text.count('\n') > 0:
                        subd = (verts[2].y - verts[0].y) / p_text.count('\n')
                        for i in range(p_text.count('\n')):
                            boxes.append(
                                [(verts[0].x, int(verts[0].y + (subd * i))),
                                 (verts[2].x, int(verts[0].y + (subd * (i + 1)))),
                                 (255, 0, 0)])
                else:
                    print('skipping')
    return boxes


# def create_boxes(boxes, image, img_num, image_path):
#     """ Returns successive images to path with less text blocked out after each images. """
#     cv2.imwrite(image_path + str(img_num) + "." + str(len(boxes) + 1) + '.jpg', image)
#     for i in reversed(range(len(boxes))):
#         image = cv2.rectangle(image, boxes[i][0], boxes[i][1], boxes[i][2], -1)
#         cv2.imwrite(image_path + str(img_num) + "." + str(i) + '.jpg', image)


#
# def overlay_text_boxes(pathtoimages,outputpath, limit):
#     for i in range(limit):
#         image = cv2.imread('/users/josh.flori/desktop/memes/' + str(i) + '.jpg')
#         image_text = get_image_text(pathtoimages + str(i) + '.jpg')
#         boxes = create_blocks_from_paragraph(image_text, image, i)
#         create_boxes(boxes, image, i, outputpath)
