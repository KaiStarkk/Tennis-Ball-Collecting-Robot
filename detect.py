'''
Adapted from SimpleCV example code published by developer xamo at:

https://gist.github.com/xamox/2438871
'''


from SimpleCV import *


display = SimpleCV.Display()
cam = SimpleCV.Camera()

hue = 33
bound = 30
erode = 1
dilate = 2
roundness = 0.35
minsat = 40
minval = 50

minsize = 200

while display.isNotDone():
	
	blobs = []
	splotches = []
	circles = []

	count = 0

	img = cam.getImage().flipHorizontal()
	dist = img.hueDistance(hue,minsat,minval)

	thresh = dist.binarize(bound).erode(erode).dilate(dilate)

	blobs = thresh.findBlobs()
	
	if blobs:
		splotches = blobs.filter([b.area() > minsize for b in blobs])
	if splotches:
		circles = splotches.filter([s.isCircle(roundness) for s in splotches])
	for c in circles:
		img.drawCircle((c.x, c.y), c.radius(),SimpleCV.Color.RED,3)
		img.drawText(str(len(circles)-count), c.x, c.y,SimpleCV.Color.BLUE,int(c.radius())-10)
		count += 1

	label = "Tennis Balls found: " + str(len(circles))
	panel = DrawingLayer(img.size())
	panel.polygon(((0,0),(0,60),(200,60),(200,0)),(100,100,100),0,True,True, 200)

	img.addDrawingLayer(panel)
	img.drawText(label,15,20,SimpleCV.Color.WHITE,24)

	img.show()
