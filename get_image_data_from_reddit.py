import os, praw, requests, io, re, cv2
from google.cloud import vision
import construct_frames

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


def get_text_size(image_path, image_text):
    image = cv2.imread(image_path)
    for word in image_text[1:]:
        verts = word.bounding_poly.vertices
        size = (verts[3].y - verts[0].y)
        print(size / image.shape[1])


def clean_text(text):
    # replace reddit users like u/dopypants where a \n is expected as the first trailing character
    text = re.sub('u/.*?\\n', '', text)
    text = re.sub('imgflip.com', '', text)
    text = re.sub('made with mematic', '', text)
    text = re.sub('www', '', text)
    # maybe replace ' U ' with I'll.. see if you get more examples
    return text


reddit_conn = connect_to_reddit()
get_image_data('/users/josh.flori/desktop/memes/', 'memes', 'week', 1000, reddit_conn)
for i in range(15, 30):
    image_text = get_image_text('/users/josh.flori/desktop/memes/' + str(i) + '.jpg')
    print(image_text[0].description)


def create_blocks_from_paragraph(image_text, image, img_num):
    """ image_text to be full document"""
    boxes = []
    for page in image_text.pages:
        for block in page.blocks:
            for paragraph in block.paragraphs:
                verts = paragraph.bounding_box.vertices

                def find_colon(paragraph):
                    for word in paragraph.words:
                        for symbol in word.symbols:
                            if symbol.text == ':':
                                return symbol.bounding_box.vertices[2].x, symbol.bounding_box.vertices[2].y

                try:
                    v0x, v0y = find_colon(paragraph)
                except TypeError:  # true when ':' not found in paragraph
                    v0x, v0y = verts[0].x, verts[0].y

                colon_found = v0x != verts[0].x
                colon_not_last_char = verts[2].x - v0x > 20
                multi_line = verts[2].y - v0y > 0

                # assumes colon will be on first line
                if colon_found and colon_not_last_char and multi_line:
                    # print("ya")
                    boxes.append([(verts[0].x, verts[0].y), (v0x, v0y), (255, 0, 0)])
                    # image = cv2.rectangle(image, (verts[0].x, verts[0].y), (v0x, v0y), (255, 0, 0), -1)
                    # cv2.imwrite('/users/josh.flori/desktop/' + str(img_num) + '.' + str(i) + '.jpg', image)
                    # i += 1
                    # image = cv2.rectangle(image, (v0x, verts[0].y), (verts[2].x, v0y), (255, 255, 255), -1)
                    boxes.append([(v0x, verts[0].y), (verts[2].x, v0y), (192, 192, 192)])
                    # cv2.imwrite('/users/josh.flori/desktop/' + str(img_num) + '.' + str(i) + '.jpg', image)
                    # i += 1
                    # image = cv2.rectangle(image, (verts[0].x, v0y), (verts[2].x, verts[2].y), (255, 255, 255), -1)
                    boxes.append([(verts[0].x, v0y), (verts[2].x, verts[2].y), (192, 192, 192)])
                    # cv2.imwrite('/users/josh.flori/desktop/' + str(img_num) + '.' + str(i) + '.jpg', image)
                    # i += 1

                elif colon_found and colon_not_last_char:
                    # print("y")
                    # image = cv2.rectangle(image, (verts[0].x, verts[0].y), (v0x, v0y), (255, 0, 0), -1)
                    boxes.append([(verts[0].x, verts[0].y), (v0x, v0y), (255, 0, 0)])
                    # cv2.imwrite('/users/josh.flori/desktop/' + str(img_num) + '.' + str(i) + '.jpg', image)
                    # i += 1
                    # image = cv2.rectangle(image, (v0x, verts[0].y), (verts[2].x, v0y), (255, 255, 255), -1)
                    boxes.append([(v0x, verts[0].y), (verts[2].x, v0y), (192, 192, 192)])
                    # cv2.imwrite('/users/josh.flori/desktop/' + str(img_num) + '.' + str(i) + '.jpg', image)
                    # i += 1
                # true when paragraph is single line and ends with colon
                elif colon_found:
                    # print("yaa")
                    # image = cv2.rectangle(image, (verts[0].x, verts[0].y), (verts[2].x, v0y), (255, 0, 0), -1)
                    boxes.append([(verts[0].x, verts[0].y), (verts[2].x, v0y), (255, 0, 0)])
                    # cv2.imwrite('/users/josh.flori/desktop/' + str(img_num) + '.' + str(i) + '.jpg', image)
                    # i += 1
                else:
                    # print("b")
                    # image = cv2.rectangle(image, (verts[0].x, verts[0].y), (verts[2].x, verts[2].y), (255, 255, 255), -1)
                    boxes.append([(verts[0].x, verts[0].y), (verts[2].x, verts[2].y), (192, 192, 192)])
                    # cv2.imwrite('/users/josh.flori/desktop/' + str(img_num) + '.' + str(i) + '.jpg', image)
                    # i += 1
    return boxes


def create_boxes(boxes, image, img_num,  image_path):
    cv2.imwrite(image_path + str(img_num) + "."+ str(len(boxes)+1) + '.jpg', image)
    for i in reversed(range(len(boxes))):
        image = cv2.rectangle(image, boxes[i][0], boxes[i][1], boxes[i][2], -1)
        cv2.imwrite(image_path + str(img_num)+ "."+str(i) + '.jpg', image)


for i in range(40, 60):
    image = cv2.imread('/users/josh.flori/desktop/memes/' + str(i) + '.jpg')
    image_text = get_image_text('/users/josh.flori/desktop/memes/' + str(i) + '.jpg')
    boxes = create_blocks_from_paragraph(image_text, image, i)
    create_boxes(boxes, image, i, '/users/josh.flori/desktop/')

for page in image_text.pages:
    for block in page.blocks:
        for paragraph in block.paragraphs:
            for word in paragraph.words:
                print(word.symbols[0].text)
                print("------------")
print('\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n')
