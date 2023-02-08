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



