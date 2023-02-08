import cv2
import numpy as np
# import tile as t



master = cv2.imread("./0070_023_02.png")
image = np.array(master)  # can draw on this one, have to use np.copy or els it passed by reference

tile1 = t.Tile(2,0,0,200,200)
tile1.populate(master)


def outlineTileParams(tile):
    startCo = (tile.imagex, tile.imagey)
    endCo = (tile.imagex+tile.width, tile.imagey+tile.width)
    color = (255, 0, 0)
    return[startCo,endCo,color]


params = outlineTileParams(tile1)

image = cv2.rectangle(image, params[0], params[1], params[2], 2)

cv2.imshow('sample image',image)

cv2.waitKey(0) # waits until a key is pressed

cv2.imshow('sample image',tile1.roi)

cv2.waitKey(0) # waits until a key is pressed

cv2.destroyAllWindows() # destroys the window showing image
