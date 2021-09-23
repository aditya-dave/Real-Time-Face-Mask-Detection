import cv2

cam = cv2.VideoCapture(0)
currentframe = 0

while (True):
    ret, frame = cam.read()
    #Add the last number of the image we captured last to avoid overwriting and taking different angles.
    name = './images/withoutmask/wmimage' + str(currentframe) + '.jpg'
    print('Creating...' + name)
    cv2.imwrite(name, frame)
    currentframe += 1

    #Change the number here to limit the number of frames captured in one go.
    if currentframe>3:
        break
    cv2.imshow('img', frame)
    k = cv2.waitKey(30) & 0xff
    if k == 27:
        break

cam.release()
cv2.destroyAllWindows()