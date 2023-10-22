# 2023 Obstacle
import cv2 
import numpy as np
import time

# Binarize for the red areas in the image
def red_detect(img):
    # Converted to HSV color space
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # Red HSV value range 1
    hsv_min = np.array([0, 80, 60])
    hsv_max = np.array([2, 255, 255])
    mask1 = cv2.inRange(hsv, hsv_min, hsv_max)

    # Red HSV value range 2
    hsv_min = np.array([150, 80, 60])
    hsv_max = np.array([180, 255, 255])
    mask2 = cv2.inRange(hsv, hsv_min, hsv_max)

    mask = mask1 + mask2
    return mask

# Binarize for the green areas in the image
def green_detect(img):
    # Converted to HSV color space
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # Green HSV value range
    hsv_min = np.array([30, 80, 60])
    hsv_max = np.array([90, 255, 255])

    mask = cv2.inRange(hsv, hsv_min, hsv_max)
    return mask

# Binarize for the orange areas in the image
def orange_detect(img):
    # Converted to HSV color space
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # Orange HSV value range
    hsv_min = np.array([5, 40, 80])
    hsv_max = np.array([17, 250, 255])

    mask = cv2.inRange(hsv, hsv_min, hsv_max)
    return mask

# Binarize for the blue areas in the image
def blue_detect(img):
    # Converted to HSV color space
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # Blue HSV value range
    hsv_min = np.array([100, 40, 80]) 
    hsv_max = np.array([130, 255, 255]) 

    mask = cv2.inRange(hsv, hsv_min, hsv_max)
    return mask

# Binarize for the black areas in the image
def black_detect(img):
    # Converted to HSV color space
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # Black HSV value range
    hsv_min = np.array([0, 0, 0])
    hsv_max = np.array([180, 210, 80])

    mask = cv2.inRange(hsv, hsv_min, hsv_max)
    return mask


# Methods that primarily analyze blobs of labels
def analysis_blob(binary_img):  
    max_blob = {}

    # connectedComponentsWithStats is a method to detect objects (connected areas)
    data = cv2.connectedComponentsWithStats(binary_img)

    # Number of labels (the background is also labeled, so the number of objects is data[0] - 1)
    n_labels = data[0] - 1

    # Only the background may be extracted at startup or when objects are completely absent
    if n_labels == 0:
        # It is more convenient to shove the value into max_blob at the time of exception
        # area is 0, so nothing happens.
        max_blob["upper_left"] = (0, 0)  # left upper coordinate
        max_blob["width"] = 0
        max_blob["height"] = 0
        max_blob["area"] = 0
        max_blob["center"] = (0, 0)

        return max_blob

    # Background is labeled 0, so delete and store the first row
    # stats contains the label's {x-coordinate at top left, y-coordinate at top left, width, height, area} information.
    stats = np.delete(data[2], 0, axis=0)

    # center of gravity of an object
    centroids = np.delete(data[3], 0, axis=0)

    # Index of the label with the largest area
    max_area_index = np.argmax(stats[:, 4])

    # Extract information on the largest object
    # Area (number of pixels out of 1280 x 720, may vary depending on the environment.)
    max_blob["area"] = stats[:, 4][max_area_index]
    max_blob["center"] = centroids[max_area_index]  # center coordinates

    return max_blob

# Methods to analyze lines for blobs
def analysis_blob_line(binary_img):  
    max_blob = {}

    # connectedComponentsWithStats is a method to detect objects (connected areas)
    data = cv2.connectedComponentsWithStats(binary_img)

    # Number of labels (the background is also labeled, so the number of objects is data[0]-1)
    n_labels = data[0] - 1

    # Only the background may be extracted at startup or when objects are completely absent
    if n_labels == 0:
        # It is more convenient to shove the value into max_blob at the time of exception
        # area is 0, so nothing happens.
        max_blob["upper_left"] = (0, 0)  # left upper coordinate
        max_blob["width"] = 0
        max_blob["height"] = 0
        max_blob["area"] = 0
        max_blob["center"] = (0, 0)
        return max_blob

    # Background is labeled 0, so delete the first line and store it
    # stats stores the label's {x-coordinate at top left, y-coordinate at top left, width, height, area} information
    stats = np.delete(data[2], 0, axis=0)

    # center of gravity of an object
    centroids = np.delete(data[3], 0, axis=0)

    # Index of the label with the largest area
    max_area_index = np.argmax(stats[:, 4])

    # Index with maximum width
    max_width_index = np.argmax(stats[:, 2])
    height, width = binary_img.shape[:3]

    # Extract information on the largest object
    max_blob["upper_left"] = (
        stats[:, 0][max_area_index], stats[:, 1][max_area_index])  # left upper coordinate
    max_blob["width"] = stats[:, 2][max_area_index]  # width
    max_blob["height"] = stats[:, 3][max_area_index]  # height
    # Area (number of pixels out of 1280 x 720, may vary depending on environment.)
    max_blob["area"] = stats[:, 4][max_area_index]
    max_blob["center"] = centroids[max_area_index]  # center coordinates
    area = stats[:, 4][max_area_index]

    return max_blob


def main():
    # Camera Capture
    cap = cv2.VideoCapture(0)
    while (cap.isOpened()):
        _, frame = cap.read()

        # Red detection
        mask_red = red_detect(frame)

        # Green detection
        mask_green = green_detect(frame)

        # Orange detection
        mask_orange = orange_detect(frame)

        # Blue detection
        mask_blue = blue_detect(frame)

        # Black detection
        mask_black1 = black_detect(frame)

        # Blob analysis of mask image (obtain blob information determined to be labeling)
        max_blob_red = analysis_blob(mask_red)
        max_blob_green = analysis_blob(mask_green)

        # Result display
        """
        cv2.imshow("Frame", frame)
        cv2.imshow("Mask red", mask_red)
        cv2.imshow("Mask green", mask_green)
        cv2.imshow("Mask orange", mask_orange)
        cv2.imshow("Mask blue", mask_blue)
        cv2.imshow("Mask black",mask_black1)
        """

        # Ends midway when the q key is pressed.
        if cv2.waitKey(25) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

 # DETECT_SIGN to return the area of the sign (because we want to change the behavior depending on the area)
def detect_sign_area(cap, mode=""): 
    is_red = False
    is_green = False

    ok_blue = False
    ok_orange = False

    clip_ratio = 0.55 
    img_shape = (320, 320, 3)
    mask_arr = np.ones(img_shape, dtype=np.uint8)
    mask_arr[:int(clip_ratio*320), :, :] = 0

    assert cap.isOpened(), "The camera is not recognized!"
    _, frame = cap.read()

    cut_frame = cv2.resize(frame, dsize=(320, 320))
    cut_frame = cut_frame * mask_arr
    cv2.imshow("cut_frame", cut_frame)

    frame = cv2.resize(frame, dsize=(160, 120))

    frame_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    frame = cv2.cvtColor(frame_hsv, cv2.COLOR_HSV2BGR)

    # Color detection
    mask_red = red_detect(frame)
    mask_green = green_detect(frame)
    mask_orange = orange_detect(frame)
    mask_blue = blue_detect(frame)
    mask_black = black_detect(frame)
    mask_black_left = black_detect(frame)
    mask_black_right = black_detect(frame)
    mask_black_left_middle = black_detect(frame)
    mask_black_right_middle = black_detect(frame)
    mask_black_right_middle = black_detect(frame)
    mask_black_core = black_detect(frame)

    height, width, channels = frame.shape[:3]

    # Set the area to be cut for each color
    mask_red[0:int(4.5 * height/10), :] = 0
    mask_green[0:int(4.5 * height/10), :] = 0
    mask_blue[0:int(3 * height/5), :] = 0
    mask_orange[0:int(3 * height/5), :] = 0

    mask_black_left[0:int(6 * height/10), :] = 0
    mask_black_left[int(6 * height/10):int(height), int(width/2):int(width)] = 0

    mask_black_right[0:int(6 * height/10), :] = 0
    mask_black_right[int(6 * height/10):int(height), 0:int(width/2)] = 0

    mask_black_right_middle[0:int(3 * height/6), :] = 0
    mask_black_right_middle[int(3*height/6):int(5 * height/6), 0:int(width/2)] = 0
    mask_black_right_middle[int(5 * height/6):int(height), ] = 0

    mask_black_left_middle[0:int(3 * height/6), :] = 0
    mask_black_left_middle[int(3 * height/6):int(5 * height/6), int(width/2):int(width)] = 0
    mask_black_left_middle[int(5 * height/6):int(height), :] = 0

    mask_black_core[0:int(3 * height/5), :] = 0
    mask_black_core[int(3 * height/5):int(5 * height/5), 0:int(width/5)] = 0
    mask_black_core[int(3 * height/5):int(5 * height/5), int(4 * width/5):int(width)] = 0

    # blob analysis
    blob_red = analysis_blob(mask_red)
    blob_green = analysis_blob(mask_green)
    blob_orange = analysis_blob_line(mask_orange)
    blob_blue = analysis_blob_line(mask_blue)
    blob_black_right = analysis_blob_line(mask_black_right)
    blob_black_left = analysis_blob_line(mask_black_left)
    blob_black_right_middle = analysis_blob_line(mask_black_right_middle)
    blob_black_left_middle = analysis_blob_line(mask_black_left_middle)
    blob_black_core = analysis_blob_line(mask_black_core)

    black_left_area = blob_black_left["area"]
    black_right_area = blob_black_right["area"]
    black_left_middle_area = blob_black_left_middle["area"]
    black_right_middle_area = blob_black_right_middle["area"]
    black_core_area = blob_black_core["area"]

    # Ratio of which black color occupies what percentage of the screen
    black_right_ratio = black_right_area * 6 / (width * height)
    black_left_ratio = black_left_area * 6/ (width * height)
    black_left_middle_ratio = black_left_middle_area * 6 / (width * height)
    black_right_middle_ratio = black_right_middle_area * 6 / (width * height)
    black_core_ratio = black_core_area * ((5/2) * (5/3))/(width * height)

    if black_left_ratio < black_left_middle_ratio and black_left_middle_ratio > 0.85 and black_left_ratio > 0.55:
        black_left_ratio = black_left_middle_ratio
    if black_right_ratio < black_right_middle_ratio and black_right_middle_ratio > 0.85 and black_right_ratio > 0.55:
        black_right_ratio = black_right_middle_ratio

    # Determining if the wall is closed or not
    wall_right,wall_left = False,False
    if black_right_ratio > 0.45:
        wall_right = True
    elif black_left_ratio > 0.45:
        wall_left = True
    if not wall_right and not wall_left:
        if black_core_ratio > 0.4:
            black_left_ratio = 0.9
            black_right_ratio = 0.9

    rcx = blob_red["center"][0]
    rcy = blob_red["center"][1]
    gcx = blob_green["center"][0]
    gcy = blob_green["center"][1]


    # Flag if the area of the larger of the red object and the green object is greater than THRESHOLD.
    area_red = blob_red["area"]
    area_green = blob_green["area"]

    blue_center_y = 0
    orange_center_y = 0

    # Conditions for flagging by reading the blue line
    if blob_blue != 0:
        blue_center = blob_blue["center"]
        blue_area = blob_blue["area"]
        if blue_area/(height * width) > 0.004 : #0.004
            if blue_center[1] > 7 * height / 10:
                ok_blue = True
            blue_center_y = blue_center[1]/height

    # Conditions for flagging by reading the orange line
    if blob_orange != 0:
        orange_center = blob_orange["center"]
        orange_area = blob_orange["area"]
        if orange_area/(width * height) > 0.004 : #0.004
            if orange_center[1] > 7 * height / 10:
                ok_orange = True
            orange_center_y = orange_center[1]/height

    orange_center = blob_orange["center"]
    orange_center_x = orange_center[0]/width
    orange_center_y = orange_center[1]/height
    blue_center = blob_blue["center"]
    blue_center_x = blue_center[0]/width
    blue_center_y = blue_center[1]/height

    # Output of each image
    """
    cv2.imshow("Frame", frame)
    cv2.imshow("Mask red", mask_red)
    cv2.imshow("Mask green", mask_green)
    cv2.imshow("Mask orange", mask_orange)
    cv2.imshow("Mask blue", mask_blue)
    cv2.imshow("Mask black", mask_black)
    cv2.imshow("Mask black left", mask_black_left)
    cv2.imshow("Mask black right", mask_black_right)
    cv2.imshow("Mask black core", mask_black_core)
    """

    # Close the window of the camera image when the Q key is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        cv2.destroyAllWindows()

    return frame, cut_frame, mask_red, mask_green, blob_red, blob_green, blue_center_x, orange_center_x, blue_center_y, orange_center_y, ok_blue, ok_orange, black_right_ratio, black_left_ratio

# The main function is made to work when this file is run by itself.
# Mainly used for adjustment of threshold
if __name__ == '__main__':
    main()
