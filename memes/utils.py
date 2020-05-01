import cv2


def align_tops(all_boxes):
    """ Align boxes which should be on the same line. Helps sorting work correctly. """
    for i in range(1, len(all_boxes)):
        area_cur = (all_boxes[i][1][0] - all_boxes[i][0][0]) * (all_boxes[i][1][1] - all_boxes[i][0][1])
        area_prev = (all_boxes[i - 1][1][0] - all_boxes[i - 1][0][0]) * (
                    all_boxes[i - 1][1][1] - all_boxes[i - 1][0][1])
        if abs((area_cur - area_prev) / area_cur) < .05 and abs(all_boxes[i][0][1] - all_boxes[i - 1][0][1]) < 20:
            print('aligning..')
            all_boxes[i][0] = (all_boxes[i][0][0], all_boxes[i - 1][0][1])


def is_a_sliver(all_boxes, i):
    """  """
    if all_boxes[i][1][1]-all_boxes[i][0][1]<20:
        sliver=True
    else:
        sliver=False
    return sliver

def is_in_frame(all_boxes, i):
    """  """
    in_frame = any([all([all_boxes[i][0][0] > box[0][0], all_boxes[i][0][1] > box[0][1], all_boxes[i][1][0] <
                            box[1][0], all_boxes[i][1][1] < box[1][1]]) for box in all_boxes])
    return in_frame


def write_images(image, all_boxes, output_path, img_num):
    """ Creates boxes over image.
        Boxes of form [ [(top_left_xy),(bottom_right_xy),(rgb)] ,...]"""
    cv2.imwrite(output_path + str(img_num) + "." + str(len(all_boxes) + 1) + '.jpg', image)
    for i in reversed(range(len(all_boxes))):
        in_frame = is_in_frame(all_boxes, i)
        is_sliver = is_a_sliver(all_boxes, i)
        if not in_frame and not is_sliver:
            image = cv2.rectangle(image, all_boxes[i][0], all_boxes[i][1], all_boxes[i][2], -1)
            cv2.imwrite(output_path + str(img_num) + "." + str(i + 1) + '.jpg', image)
