from google.cloud import automl
import pickle

""" The purpose of this module is for google's auto_ml to return bounding boxes around all relevant frames in the 
meme. Those bounding boxes are cleaned up and then combined with text boxes from text.py to create a total 
list of boxes needed to unveil the meme, bit by bit. """


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


def remove_overlapping_frames(boxes):
    """ If two frames overlap, return the larger of the two. """
    non_overlapping_frames = []
    if len(boxes) == 1:
        return boxes
    else:
        for box in boxes:
            for boxx in boxes:
                # TODO - there is a better way to loop over this shit.... have to make sure you don't compare the same
                #  box to itself otherwise it will be viewed as 'overlapping' in technicallity and be returned
                #  automatically, even if it's the smaller of two overlapping boxes.
                if box != boxx:
                    # This checks if anything overlaps
                    if not box[1][1] < boxx[0][1] or boxx[1][1] < box[0][1] or box[1][0] < boxx[0][0] or boxx[1][0] < \
                            box[0][0]:
                        larger = box if (box[1][1] - box[0][1]) * (box[1][0] - box[0][0]) > (
                                boxx[1][1] - boxx[0][1]) * (boxx[1][
                                                                0] - boxx[0][0]) else boxx
                        gaaaa = [(box[1][1] - box[0][1]) * (box[1][0] - box[0][0]),
                                 (boxx[1][1] - boxx[0][1]) * (boxx[1][
                                                                  0] - boxx[0][0])]
                        print(gaaaa)
                        print(max(gaaaa))
                        if larger not in non_overlapping_frames:
                            non_overlapping_frames.append(larger)
        return non_overlapping_frames


def create_blocks_from_annotations(annotation, image):
    """ Parse the vertices of the bounding boxes from the google auto_ml annotation into list like:
    [topleft, bottomright, (255, 255, 255)]"""
    boxes = []
    for payload in annotation.payload:
        if payload.image_object_detection.score > .65:
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
        starts_with_white = [x[0] == 255 for x in image[box[0][1]]].count(True) / len(image[box[0][1]]) >= .99
        for i in range(box[0][1] + 1, box[1][1]):
            # when this is true it denotes the transition from the row being all-white to non-all-white.

            # old method
            # abs(np.mean(image[i]) - np.mean(image[i - 1])) > 100

            if [x[0] == 255 for x in image[i - 1]].count(True) / len(image[i - 1]) >= .99 and [x[0] == 255 for x in
                                                                                               image[i]].count(
                True) / len(image[i - 1]) < .9 and starts_with_white:
                box[0] = (box[0][0], i)
                break


def remove_slivers(all_boxes):
    """  auto_ml sometimes creates a sliver of a block - something small and irrelevant. This discards such boxes."""
    no_slivers = []
    for box in all_boxes:
        if box[1][1] - box[0][1] > 41:
            no_slivers.append(box)
    return no_slivers


def remove_unneeded_outer_frame(frame_boxes, image):
    """ It may be the case that automl identifies that entire image as a frame AS WELL AS identifying frames within
    it. In this case, write_images will fail because text boxes would be within two frames at once which just isn't
    what we want to be working with. The solution is to remove the outer frame. If a frame is around the entire """
    for i in frame_boxes:
        if i[0][0] == 0 and i[0][1] == 0 and i[1][0] == image.shape[1] and i[1][1] == image.shape[0]:
            frame_boxes.remove(i)


def deploy(model_client, model_full_id):
    response = model_client.deploy_model(model_full_id)
    print("Model deployment finished. {}".format(response.result()))


def undeploy(model_client, model_full_id):
    response = model_client.undeploy_model(model_full_id)
    print("Model un-deployment finished. {}".format(response.result()))

def write_pickle(all_annotations):
    output = open('annotations.pkl', 'wb')
    pickle.dump(all_annotations, output)
    output.close()


def read_pickle():
    pkl_file = open('annotations.pkl', 'rb')
    all_annotations = pickle.load(pkl_file)
    pkl_file.close()
    return all_annotations