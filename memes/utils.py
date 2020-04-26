import cv2


def which_comes_next(image, all_boxes, output_path, img_num):
    """ Creates boxes over image.
        Boxes of form [ [(top_left_xy),(bottom_right_xy),(rgb)] ,...]"""
    cv2.imwrite(output_path + str(img_num) + "." + str(len(all_boxes) + 1) + '.jpg', image)
    for i in reversed(range(len(all_boxes))):
        # counts how many boxes on same line - helps escape the subsequent logic which would otherwise skip where
        # there are multiple boxes lined across
        # how_many = sum([box[0][1] == all_boxes[i][0][1] for box in all_boxes])
        is_in_frame = any([all([all_boxes[i][0][0] > box[0][0], all_boxes[i][0][1] > box[0][1], all_boxes[i][1][0] <
                               box[1][0], all_boxes[i][1][1] < box[1][1]]) for box in all_boxes])
        if not is_in_frame:
            image = cv2.rectangle(image, all_boxes[i][0], all_boxes[i][1], all_boxes[i][2], -1)
            cv2.imwrite(output_path + str(img_num) + "." + str(i + 1) + '.jpg', image)
            # you want the top to be below the end of the previous box, >0 just makes it so that no error on first box
            # if i > 0 and how_many < 2:
            #     if all_boxes[i][0][1] > all_boxes[i - 1][1][1] - 1:  # -1 at the end just helps boxes on EXACT same line
            #         image = cv2.rectangle(image, all_boxes[i][0], all_boxes[i][1], all_boxes[i][2], -1)
            #         cv2.imwrite(output_path + str(img_num) + "." + str(i + 1) + '.jpg', image)
            # else:
            #     image = cv2.rectangle(image, all_boxes[i][0], all_boxes[i][1], all_boxes[i][2], -1)
            #     cv2.imwrite(output_path + str(img_num) + "." + str(i + 1) + '.jpg', image)