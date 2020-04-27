from google.cloud import automl_v1beta1
from google.cloud.automl_v1beta1.proto import service_pb2
import os, cv2, tqdm
import numpy as np


def print_anno(annotation):
    for payload in annotation.payload:
        print(payload.image_object_detection.bounding_box.normalized_vertices[0].x)
        print(payload.image_object_detection.bounding_box.normalized_vertices[0].y)
        print(payload.image_object_detection.bounding_box.normalized_vertices[1].x)
        print(payload.image_object_detection.bounding_box.normalized_vertices[1].y)


def get_prediction(content, project_id, model_id):
    """ Return object detections """
    prediction_client = automl_v1beta1.PredictionServiceClient()
    name = 'projects/{}/locations/us-central1/models/{}'.format(project_id, model_id)
    payload = {'image': {'image_bytes': content}}
    params = {}
    request = prediction_client.predict(name, payload, params)
    return request


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


def create_blocks_from_annotations(annotation):
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
    """ Trim bad white space from annotated boxes.
        Assumes there will be extra white space on top....
        Boxes of form [ [(top_left_xy),(bottom_right_xy),(rgb)] ,...]"""
    i = 0
    for box in boxes:
        print(box)
        for ii in range(box[0][1] + 1, box[1][1]):
            if abs(np.mean(image[ii]) - np.mean(image[ii - 1])) > 100:
                box[0] = (box[0][0], ii)
                break


#
#
# # all_annotations = []
# for i in tqdm.tqdm(range(100)):
#     with open('/users/josh.flori/desktop/memes/' + str(i) + '.jpg', 'rb') as ff:
#         content = ff.read()
#
#     all_annotations.append(get_prediction(content, '140553804812', 'IOD2492808364447236096'))
#
# print_anno(all_annotations[0])
#
# for payload in all_annotations[4].payload:
#     print(payload.image_object_detection.score)
