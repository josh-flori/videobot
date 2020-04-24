import os, praw, requests, io, re, cv2
import numpy as np
from google.cloud import vision

# TODO - if 'mods' in text, ignore that image entirely.

os.environ[
    'GOOGLE_APPLICATION_CREDENTIALS'] = '/users/josh.flori/pycharmprojects/reddit-vision-239200-50adace0d3bf.json'


def connect_to_reddit():
    """ Returns credentialled connection to reddit api. """
    reddit_conn = praw.Reddit(client_id='eZ0qCk4LGFmlvg',
                              client_secret='ObVykPZwUf6AtmvQyh-HFIlhn8I',
                              user_agent='myApp',
                              username='',
                              password='')
    return reddit_conn


def get_image_data(output_path, subreddit, time_limit, limit, reddit_conn):
    """ Writes top image posts from given subreddit to specified output path. """
    submissions = reddit_conn.subreddit(subreddit).top(time_limit, limit=limit)
    i = 0
    for s in submissions:
        r = requests.get(s.url, allow_redirects=True)
        if ".gif" not in s.url:
            open(output_path + str(i) + '.jpg', 'wb').write(r.content)
            i += 1


def get_image_text(image_path):
    """ Returns text from image file. """
    with io.open(image_path, 'rb') as image_file:
        content = image_file.read()
    client = vision.ImageAnnotatorClient()
    image = vision.types.Image(content=content)
    full_response = client.document_text_detection(image=image).full_text_annotation
    return full_response


def find_colon(paragraph):
    for word in paragraph.words:
        for symbol in word.symbols:
            if symbol.text == ':':
                return symbol.bounding_box.vertices[2].x, symbol.bounding_box.vertices[2].y


def get_text(paragraph):
    # TODO - shouldn't really loop through same shit twice...
    p_text = ''
    conf = []
    lookup = {'': '', 'type: LINE_BREAK\n': '', 'type: SPACE\n': ' ', 'type: EOL_SURE_SPACE\n': ''}
    for word in paragraph.words:
        for symbol in word.symbols:
            p_text += symbol.text
            # TODO - import actual break types and use that somehow
            p_text += lookup[str(symbol.property.detected_break)]
            conf.append(symbol.confidence)
    return p_text, conf


def create_boxes(boxes, image, img_num, image_path):
    cv2.imwrite(image_path + str(img_num) + "." + str(len(boxes) + 1) + '.jpg', image)
    for i in reversed(range(len(boxes))):
        image = cv2.rectangle(image, boxes[i][0], boxes[i][1], boxes[i][2], -1)
        cv2.imwrite(image_path + str(img_num) + "." + str(i) + '.jpg', image)


def should_exclude(p_text):
    """ ... """
    exclude = any([p_text == 'Details',
                   re.search('u/.*?', p_text) is not None,
                   re.search('@.*', p_text) is not None,
                   re.search('imgflip.com', p_text) is not None,
                   re.search('[0-9] hours ago', p_text) is not None,
                   re.search('made with mematic', p_text) is not None,
                   re.search('www', p_text) is not None,
                   re.search('made with love', p_text) is not None,
                   p_text.isdigit(),
                   p_text.replace('-','').isdigit(),
                   p_text.lower() == 'srgrafo',
                  'adultswim' in p_text,
                   p_text=='ORSAIR',
                   '[deleted]' in p_text])
    return exclude


def create_blocks_from_paragraph(image_text, image, img_num):
    """ image_text to be full document"""
    boxes = []
    for page in image_text.pages:
        for block in page.blocks:
            for paragraph in block.paragraphs:
                verts = paragraph.bounding_box.vertices

                p_text, conf = get_text(paragraph)
                print(p_text)
                if not should_exclude(p_text) and np.mean(conf) > .8:

                    # TODO - ask the internet if there is a better way to do this
                    try:
                        v0x, v0y = find_colon(paragraph)
                    except TypeError:  # true when ':' not found in paragraph
                        v0x, v0y = verts[0].x, verts[0].y

                    colon_found = v0x != verts[0].x
                    colon_not_last_char = verts[2].x - v0x > 20
                    multi_line = verts[2].y - v0y > 0

                    # assumes colon will be on first line
                    if colon_found and colon_not_last_char and multi_line:
                        boxes.append([(verts[0].x, verts[0].y), (v0x, v0y), (255, 0, 0)])
                        boxes.append([(v0x, verts[0].y), (verts[2].x, v0y), (192, 192, 192)])
                        boxes.append([(verts[0].x, v0y), (verts[2].x, verts[2].y), (192, 192, 192)])
                    elif colon_found and colon_not_last_char:
                        boxes.append([(verts[0].x, verts[0].y), (v0x, v0y), (255, 0, 0)])
                        boxes.append([(v0x, verts[0].y), (verts[2].x, v0y), (192, 192, 192)])
                    elif colon_found:
                        boxes.append([(verts[0].x, verts[0].y), (verts[2].x, v0y), (255, 0, 0)])
                    else:
                        boxes.append([(verts[0].x, verts[0].y), (verts[2].x, verts[2].y), (192, 192, 192)])
                else:
                    print('skipping')
    return boxes


for i in range(30, 35):
    image = cv2.imread('/users/josh.flori/desktop/memes/' + str(i) + '.jpg')
    image_text = get_image_text('/users/josh.flori/desktop/memes/' + str(i) + '.jpg')
    boxes = create_blocks_from_paragraph(image_text, image, i)
    create_boxes(boxes, image, i, '/users/josh.flori/desktop/')



reddit_conn = connect_to_reddit()
get_image_data('/users/josh.flori/desktop/memes/', 'memes', 'week', 1000, reddit_conn)
for i in range(24, 30):
    image_text = get_image_text('/users/josh.flori/desktop/memes/' + str(i) + '.jpg')
    print(image_text[0].description)

print(re.search('u/.*?\\n', 'asdfasdfu/blablfasdf'))

print(str(image_text.text))
