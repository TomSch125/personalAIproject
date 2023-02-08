import cv2
import numpy as np
# import tile as t


import cv2 as cv
import numpy as np

class Tile:   
    x = 0
    y = 0
    width = 0
    height = 0
    imagex = 0
    imagey = 0
    roi = 0

    def __init__(self,x, y, overlap, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.imagex = x * (width - overlap)
        self.imagey = y * (height - overlap)

    def populate(self,master):
        y = self.imagey
        x = self.imagex
        height = self.height
        width = self.width

        self.roi = master[y:y+height, x:x+width]
        # self.roi = master[x:x+width,y:y+height]






# define the function to compute MSE between two images
def mse(img1, img2):
   h, w = img1.shape
   diff = cv2.subtract(img1, img2)
   err = np.sum(diff**2)
   mse = err/(float(h*w))
   return mse, diff




master = cv2.imread("./0070_023_02.png")
image = np.array(master)  # can draw on this one, have to use np.copy or els it passed by reference


t_width = 64
t_height = 64
overlap = 0

# get dimensions of image
dimensions = image.shape
 
# height, width, number of channels in image
height = image.shape[0]
width = image.shape[1]
channels = image.shape[2]

tilesInX = width / (t_width - overlap)
tilesInY = height / (t_height - overlap)

tiles = []

for y in range(int(tilesInY)):
    row = []
    for x in range(int(tilesInX)):
        # tile = t.Tile(x,y,overlap,t_width,t_height)
        tile = Tile(x,y,overlap,t_width,t_height)

        tile.populate(master)
        row.append(tile)
    tiles.append(row)



# master_Tile1 = t.Tile(10,0,overlap,t_width,t_height)
master_Tile1 = Tile(10,0,overlap,t_width,t_height)

master_Tile1.populate(master)


# master_Tile2 = t.Tile(17,2,overlap,t_width,t_height)
master_Tile2 = Tile(17,2,overlap,t_width,t_height)

master_Tile2.populate(master)


# master_Tile3 = t.Tile(30,1,overlap,t_width,t_height)
master_Tile3 = Tile(30,1,overlap,t_width,t_height)

master_Tile3.populate(master)

# convert the images to grayscale
gMT_1 = cv2.cvtColor(master_Tile1.roi, cv2.COLOR_BGR2GRAY) #gray master tile
gMT_2 = cv2.cvtColor(master_Tile2.roi, cv2.COLOR_BGR2GRAY) #gray master tile
gMT_3 = cv2.cvtColor(master_Tile3.roi, cv2.COLOR_BGR2GRAY) #gray master tile

cv2.imshow('master Image',image)
cv2.waitKey(0) # waits until a key is pressed
cv2.destroyAllWindows() # destroys the window showing image

# cv2.imshow('master Tile',tiles[0][10].roi)
cv2.imshow('master Tile 1',master_Tile1.roi)
cv2.waitKey(0) # waits until a key is pressed
cv2.destroyAllWindows() # destroys the window showing image

cv2.imshow('master Tile 2',master_Tile2.roi)
cv2.waitKey(0) # waits until a key is pressed
cv2.destroyAllWindows() # destroys the window showing image

cv2.imshow('master Tile 3',master_Tile3.roi)
cv2.waitKey(0) # waits until a key is pressed
cv2.destroyAllWindows() # destroys the window showing image

# Write some Text

font                   = cv2.FONT_HERSHEY_SIMPLEX
bottomLeftCornerOfText = (0,20)
fontScale              = 1
fontColor              = (255,0,0)
thickness              = 1
lineType               = 2


for y in range(int(tilesInY)):
    for x in range(int(tilesInX)):
        img = np.copy(tiles[y][x].roi)

        cv2.putText(img,str(y)+","+str(x), 
        bottomLeftCornerOfText, 
        font, 
        fontScale,
        fontColor,
        thickness,
        lineType)

        cv2.imshow('tile',img)
        cv2.waitKey(0) # waits until a key is pressed

errorThresh = 60

for y in range(int(tilesInY)):
    for x in range(int(tilesInX)):
        gT = cv2.cvtColor(tiles[y][x].roi, cv2.COLOR_BGR2GRAY) #gray tile
        error_1, diff_1 = mse(gMT_1, gT)
        error_2, diff_2 = mse(gMT_2, gT)
        error_3, diff_3 = mse(gMT_3, gT)
        errors = np.array([error_1,error_2,error_3])
        error = np.mean(errors)
        if error > errorThresh:
            img = np.copy(tiles[y][x].roi)

            cv2.putText(img,str(error), 
            bottomLeftCornerOfText, 
            font, 
            fontScale,
            fontColor,
            thickness,
            lineType)

            cv2.imshow('tile',img)
            cv2.waitKey(0) # waits until a key is pressed
            cv2.destroyAllWindows() # destroys the window showing image


        # cv2.waitKey(0) # waits until a key is pressed


cv2.destroyAllWindows() # destroys the window showing image
