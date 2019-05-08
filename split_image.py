import numpy as np
import cv2
import matplotlib.pyplot as plt
import time

# load image
image = cv2.imread('/users/josh.flori/desktop/memes/8.jpg')
# get row-wise standard devisiation of pixel values
stdv=[np.std(image[i]) for i in range(image.shape[0])]
# get absolute difference between standard deviations of adjacent rows
dif=np.array([abs(stdv[i]-stdv[i+1]) for i in range(len(stdv)-1)])

plt.plot(range(image.shape[0]-1),dif)
plt.ylabel('some numbers')
plt.show()


# get standard deviation of differences, to define what is an anomalous deviation
stdv_of_dif=np.std(dif)
# get outliers
divs=np.where(dif>np.mean(dif)+stdv_of_dif*5)
divs=[divs[0][i] for i in range(len(divs[0])) if divs[0][i]>30 and divs[0][i] < image.shape[0]-30] 
divs=[divs[i+1] for i in range(len(divs)-1) if divs[i+1]-divs[i]>30] 
# split up image

for i in range(divs):
    cut_image=image[0:divs[i],]
    cv2.imshow('ImageWindow', cut_image)
    cv2.imshow("img", cut_image); cv2.waitKey(0); cv2.destroyAllWindows()
    time.sleep(2)
    

