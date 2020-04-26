import os, praw, requests, io, re, cv2
from google.cloud import vision


def create_blocks_from_words(image_text, image):
    for word in image_text[1:]:
        verts = word.bounding_poly.vertices
        image = cv2.rectangle(image, (verts[0].x, verts[0].y), (verts[2].x, verts[2].y), (255, 0, 0), -1)
    cv2.imwrite('/users/josh.flori/desktop/a.jpg', image)


def create_blocks_from_paragraph(image_text, image, img_num):
    """ image_text to be full document"""
    for page in image_text.pages:
        for block in page.blocks:
            for paragraph in block.paragraphs:
                verts = paragraph.bounding_box.vertices
                for word in paragraph.words:
                    for symbol in word.symbols:
                        if symbol.text == ':':
                            v0x = symbol.bounding_box.vertices[0].x
                            print("found")
                        else:
                            v0x = verts[0].x
                image = cv2.rectangle(image, (v0x, verts[0].y), (verts[2].x, verts[2].y), (255, 0, 0), -1)
    cv2.imwrite('/users/josh.flori/desktop/' + str(img_num) + '.jpg', image)
