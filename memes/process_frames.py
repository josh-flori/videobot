from google.cloud import automl
import numpy as np

""" The purpose of this module is for google's auto_ml to return bounding boxes around all relevant frames in the 
meme. Those bounding boxes are cleaned up and then combined with text boxes from process_text.py to create a total 
list of boxes needed to unveil the image, bit by bit. """

def get_frame_prediction_from_google(meme_path, img_num, project_id, model_id):
    """ I trained a custom model using google's auto_ml product to put bounding boxes around what I defined as
    relevant frames. So in a 4 panel meme, it would learn where those four panels are. This function returns bounding
    boxes from that model. These 'frames' will combine with the text bounding boxes from the process_text module to
    create all the boxes needed to unveil the image, bit by bit."""

    with open(meme_path + str(img_num) + '.jpg', 'rb') as ff:
        content = ff.read()

    prediction_client = automl.PredictionServiceClient()
    name = 'projects/{}/locations/us-central1/models/{}'.format(project_id, model_id)
    payload = {'image': {'image_bytes': content}}
    params = {}
    annotation = prediction_client.predict(name, payload, params)
    return annotation


def expand_to_edge(annotation):
    """" Push boundaries of boxes to 0/1 if close to edge of image. """
    for payload in annotation.payload:
        for i in range(2):
            if payload.image_object_detection.bounding_box.normalized_vertices[i].x < .05:
                payload.image_object_detection.bounding_box.normalized_vertices[i].x = 0
            if payload.image_object_detection.bounding_box.normalized_vertices[i].y < .05:
                payload.image_object_detection.bounding_box.normalized_vertices[i].y = 0
            if payload.image_object_detection.bounding_box.normalized_vertices[i].x > .95:
                payload.image_object_detection.bounding_box.normalized_vertices[i].x = 1
            if payload.image_object_detection.bounding_box.normalized_vertices[i].y > .95:
                payload.image_object_detection.bounding_box.normalized_vertices[i].y = 1


def perc_to_pix(image, perc, dim):
    """ Returns pixel value positions of bounding box since google returns percentages. """
    if dim == 'x':
        val = int(image.shape[1] * perc)
    else:
        val = int(image.shape[0] * perc)
    return val


def create_blocks_from_annotations(annotation, image):
    """ Parse the vertices of the bounding boxes from the google auto_ml annotation into list like:
    [topleft, bottomright, (255, 255, 255)]"""
    boxes = []
    for payload in annotation.payload:
        if payload.image_object_detection.score > .85:
            verts = payload.image_object_detection.bounding_box.normalized_vertices
            topleft = (perc_to_pix(image, verts[0].x, 'x'),
                       perc_to_pix(image, verts[0].y, 'y'))
            bottomright = (perc_to_pix(image, verts[1].x, 'x'),
                           perc_to_pix(image, verts[1].y, 'y'))
            boxes.append([topleft, bottomright, (255, 255, 255)])
    return boxes


def trim_white_space(image, boxes):
    """ Trim bad white space from annotated boxes in the case where a box has been annotated around a picture with
    extra, empty white pixels hanging above the top of it. """
    for box in boxes:
        # loop from top row to bottom row of that box
        for i in range(box[0][1] + 1, box[1][1]):
            # when this is true it denotes the transition from the row being all-white to non-all-white.
            if abs(np.mean(image[i]) - np.mean(image[i - 1])) > 100:
                box[0] = (box[0][0], i)
                break
