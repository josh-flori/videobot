import os, praw, requests, io, re, cv2
import numpy as np
from google.cloud import vision
import sys
from google.cloud import automl_v1beta1
from google.cloud.automl_v1beta1.proto import service_pb2

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
    """ Returns top n images from specified sub to specified path. """
    submissions = reddit_conn.subreddit(subreddit).top(time_limit, limit=limit)
    i = 0
    for s in submissions:
        r = requests.get(s.url, allow_redirects=True)
        if ".gif" not in s.url:
            open(output_path + str(i) + '.jpg', 'wb').write(r.content)
            i += 1


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

                    #
                    # # TODO - ask the internet if there is a better way to do this
                    # # Get colon position else set to left-most paragraph vertex
                    # try:
                    #     v0x, v0y = find_colon(paragraph)
                    # except TypeError:
                    #     v0x, v0y = verts[0].x, verts[0].y
                    #
                    # # Abstract conditions so if statements are easier to read
                    # colon_found = v0x != verts[0].x
                    # colon_not_last_char = verts[2].x - v0x > 20
                    # multi_line = verts[2].y - v0y > 0
                    #
                    # # Assumes colon will be on first line
                    # if colon_found and colon_not_last_char and multi_line:
                    #     boxes.append([(verts[0].x, verts[0].y), (v0x, v0y), (255, 0, 0)])  # box for colon
                    #     boxes.append([(v0x, verts[0].y), (verts[2].x, v0y), (192, 192, 192)])  # box after colon
                    #     boxes.append([(verts[0].x, v0y), (verts[2].x, verts[2].y), (192, 192, 192)])  # entire next line
                    # elif colon_found and colon_not_last_char:
                    #     boxes.append([(verts[0].x, verts[0].y), (v0x, v0y), (255, 0, 0)])  # box for colon
                    #     boxes.append([(v0x, verts[0].y), (verts[2].x, v0y), (192, 192, 192)])  # box after colon
                    # elif colon_found:
                    #     boxes.append([(verts[0].x, verts[0].y), (verts[2].x, v0y), (255, 0, 0)])  # box for colon
                    # else:
                    #     boxes.append([(verts[0].x, verts[0].y), (verts[2].x, verts[2].y), (192, 192, 192)]) # regular box
                else:
                    print('skipping')
    return boxes


def create_boxes(boxes, image, img_num, image_path):
    """ Returns successive images to path with less text blocked out after each images. """
    cv2.imwrite(image_path + str(img_num) + "." + str(len(boxes) + 1) + '.jpg', image)
    for i in reversed(range(len(boxes))):
        image = cv2.rectangle(image, boxes[i][0], boxes[i][1], boxes[i][2], -1)
        cv2.imwrite(image_path + str(img_num) + "." + str(i) + '.jpg', image)


for i in range(0, 1):
    image = cv2.imread('/users/josh.flori/desktop/memes/' + str(i) + '.jpg')
    image_text = get_image_text('/users/josh.flori/desktop/memes/' + str(i) + '.jpg')
    boxes = create_blocks_from_paragraph(image_text, image, i)
    create_boxes(boxes, image, i, '/users/josh.flori/desktop/')

reddit_conn = connect_to_reddit()
get_image_data('/users/josh.flori/desktop/memes/', 'memes', 'week', 1000, reddit_conn)
for i in range(24, 30):
    image_text = get_image_text('/users/josh.flori/desktop/memes/' + str(i) + '.jpg')
    print(image_text[0].description)


# --------------------------------------------


# 'content' is base-64-encoded image data.
def get_prediction(content, project_id, model_id):
    prediction_client = automl_v1beta1.PredictionServiceClient()

    name = 'projects/{}/locations/us-central1/models/{}'.format(project_id, model_id)
    payload = {'image': {'image_bytes': content}}
    params = {}
    request = prediction_client.predict(name, payload, params)
    return request  # waits till request is returned

import os
os.environ[
    'GOOGLE_APPLICATION_CREDENTIALS'] = '/users/josh.flori/pycharmprojects/reddit-vision-239200-50adace0d3bf.json'


all_annotations=[]
for i in tqdm.tqdm(range(100)):
    with open('/users/josh.flori/desktop/memes/'+str(i)+'.jpg', 'rb') as ff:
        content = ff.read()

    all_annotations.append(get_prediction(content, '140553804812', 'IOD2492808364447236096'))

all_annotations[0]
for payload in all_annotations[1].payload:
    print(payload.image_object_detection.bounding_box.normalized_vertices[0])
    print(payload.image_object_detection.bounding_box.normalized_vertices[1])
    print("---")
