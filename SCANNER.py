# /////////////////////////////////////////////////////////////////////////////
# {{ CityScopePy }}
# Copyright (C) {{ 2018 }}  {{ Ariel Noyman }}

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# /////////////////////////////////////////////////////////////////////////////

# CityScopePy SCANNER
# a simple decoder of 2d array made of LEGO bricks, parsing and sending for visualzation

# "@context": "https://github.com/CityScope/", "@type": "Person", "address": {
# "@type": "75 Amherst St, Cambridge, MA 02139", "addressLocality":
# "Cambridge", "addressRegion": "MA",},
# "jobTitle": "Research Scientist", "name": "Ariel Noyman",
# "alumniOf": "MIT", "url": "http://arielnoyman.com",
# "https://www.linkedin.com/", "http://twitter.com/relno",
# https://github.com/RELNO]


# raise SystemExit(0)

import cv2
import numpy as np
import MODULES

##################################################
# NOTE: Don't change resolution
videoResX = 1200
videoResY = 600

# define the grid size
gridX = 6
gridY = 3

# define the size for each scanner
cropSize = 10


# load json file
tagsArray = MODULES.JSONparse('tags')
mapArray = MODULES.JSONparse('map')
rotationArray = MODULES.JSONparse('rotation')

# load the keystone data from file
keyStonePts = np.loadtxt('DATA/keystone.txt', dtype=np.float32)

# define the video
webcam = cv2.VideoCapture(0)

# define the video window
cv2.namedWindow('webcamWindow', cv2.WINDOW_NORMAL)

# make the sliders GUI
MODULES.GUI(keyStonePts, videoResX, videoResY)

# call colors dictionary
colors = MODULES.colDict

# create the location  array of scanners
scanLocArr = MODULES.makeGridOrigins(videoResX, videoResY, cropSize)

# get inital key Stone Data before interaction and keystone
keyStoneData = MODULES.fineGrainKeystone(
    videoResX, videoResY, keyStonePts, False)


##################################################
###################MAIN LOOP######################
##################################################


# run the video loop forever
while(True):

    # break video loop by pressing ESC
    key = cv2.waitKey(2) & 0xFF
    if key == 27:
        break

    '''
    NOTE:WIP dynamic keystone on runtime 
    '''
    keyStoneData = MODULES.fineGrainKeystone(
        videoResX, videoResY, keyStonePts, 0)

    cv2.getTrackbarPos('corner', 'webcamWindow')

    # zero an array to collect the scanners
    cellColorsArray = []

    # init counter for text display
    counter = 0

    # read video frames
    _, thisFrame = webcam.read()

    # warp the video based on keystone info
    distortVid = cv2.warpPerspective(
        thisFrame, keyStoneData, (videoResX, videoResY))

    # run through locations list and make scanners
    for loc in scanLocArr:

        # set x and y from locations array
        x = loc[0]
        y = loc[1]

        # set scanner crop box size and position
        # at x,y + crop box size
        scannerCropBox = distortVid[y:y+cropSize, x:x+cropSize]

        # draw rects with mean value of color
        meanCol = cv2.mean(scannerCropBox)

        # convert colors to rgb
        b, g, r, _ = np.uint8(meanCol)
        mCol = np.uint8([[[b, g, r]]])

        # select the right color based on sample
        scannerCol = MODULES.colorSelect(mCol)

        # get color from dict
        thisColor = colors[scannerCol]

        # add colors to array for type analysis
        cellColorsArray.append(scannerCol)

        # draw rects with frame colored by range result
        cv2.rectangle(distortVid, (x, y),
                      (x+cropSize, y+cropSize),
                      thisColor, 1)

        # add type and pos text
        cv2.putText(distortVid, str(counter),
                    (x-1, y-2), cv2.FONT_HERSHEY_PLAIN,
                    0.6, (0, 0, 0))

        counter += 1

    # send array to check types
    typesList = MODULES.findType(
        cellColorsArray, tagsArray, mapArray, rotationArray)
    # send to UDP here

    # add type and pos text
    cv2.putText(distortVid, str(typesList),
                (20, 20), cv2.FONT_HERSHEY_PLAIN,
                1.5, (0, 0, 0))

    # draw the video to screen
    cv2.imshow("webcamWindow", distortVid)


# break the loop
webcam.release()
cv2.destroyAllWindows()