import math
import numpy as np
import cv2
import MODULES

# load the keystone data from file
M = np.loadtxt('keystone.txt')
# define the video
webcam = cv2.VideoCapture(0)
# define the video window
cv2.namedWindow('vid')
# set res. for vid
videoRes = 500
# define the number of grid scanners
gridSize = 10
# define the size for each scanner
cropSize = 5
# array to collect the scanners
colorArr = np.zeros((3, 2, 2), dtype=np.int64)

print(colorArr)
# raise SystemExit(0)

colors = MODULES.colDict

# run the video loop forever
while(True):
    _, frame = webcam.read()
    dst = cv2.warpPerspective(
        frame, M, (videoRes, videoRes))

    # if needed, implement max_rgb_filter
    # dst = MODULES.max_rgb_filter(dst)
    step = int(videoRes/gridSize)
    for x in range(int(step/2), videoRes, step):
        for y in range(int(step/2), videoRes, step):
            crop = dst[y:y+cropSize, x:x+cropSize]
            # draw rects with mean value of color
            meanCol = cv2.mean(crop)
            b, g, r, _ = np.uint8(meanCol)
            mCol = np.uint8([[[b, g, r]]])
            scannerCol = MODULES.colorSelect(mCol)
            thisColor = colors[scannerCol]

            # draw rects with frame colored by range result
            cv2.rectangle(dst, (x-1, y-1), (x+cropSize + 1, y+cropSize + 1),
                          thisColor, 1)

            # draw the mean color itself
            cv2.rectangle(dst, (x, y), (x+cropSize,
                                        y+cropSize), meanCol, -1)

            # add colors to array for type analysis
            # colorArr[x][y] = scannerCol

    # draw the video to screen
    cv2.imshow("vid", dst)

    # break video loop by pressing ESC
    key = cv2.waitKey(10) & 0xFF
    if key == 27:
        break

webcam.release()
cv2.destroyAllWindows()
