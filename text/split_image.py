import numpy as np
import cv2
import matplotlib.pyplot as plt
import time


def split_image(image_num):
    image = cv2.imread('/users/josh.flori/desktop/memes/'+str(image_num)+'.jpg')
    # get row-wise standard devisiation of pixel values
    stdv=[np.std(image[i]) for i in range(image.shape[0])]
    # get absolute difference between standard deviations of adjacent rows
    dif=np.array([abs(stdv[i]-stdv[i+1]) for i in range(len(stdv)-1)])
#
    # plt.plot(range(image.shape[0]-1),dif)
    # plt.ylabel('some numbers')
    # plt.show()
#
#
    # get standard deviation of differences, to define what is an anomalous deviation
    stdv_of_dif=np.std(dif)
    # get outliers
    divs=np.where(dif>np.mean(dif)+stdv_of_dif*4)
    # +3 just gives some padding because its necessary
    divs=[divs[0][i]+3 for i in range(len(divs[0])) if divs[0][i]>30 and divs[0][i] < image.shape[0]-80] 
    divs=[divs[i+1] for i in range(len(divs)-1) if divs[i+1]-divs[i]>image.shape[0]*.033] 
    # split up image
    for i in range(len(divs)):
        if i==len(divs)-1:
            cv2.imwrite('/users/josh.flori/desktop/'+str(image_num)+"-"+str(i)+'.jpg',image[0:divs[i],])
            cv2.imwrite('/users/josh.flori/desktop/'+str(image_num)+"-"+str(i+1)+'.jpg',image)
        else:
            cv2.imwrite('/users/josh.flori/desktop/'+str(image_num)+"-"+str(i)+'.jpg',image[0:divs[i],])