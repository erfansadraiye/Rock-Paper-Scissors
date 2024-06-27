import cv2
import matplotlib.pyplot as plt
import numpy as np
from cvzone.HandTrackingModule import HandDetector


def crop_image_using_bbox(img, bbox, padding=80):
    """
    Crop the image using a bounding box with additional padding, and ensure the crop stays within image boundaries.

    :param image_path: Path to the image file.
    :param bbox: A tuple (x_min, y_min, width, height) defining the bounding box.
    :param padding: Additional padding to add around the bounding box. Default is 50 pixels.
    :return: Cropped image as a NumPy array.
    """
    if img is None:
        raise FileNotFoundError("The image file was not found.")

    # Get image dimensions
    img_height, img_width = img.shape[:2]

    # Unpack the bounding box and apply padding
    x_min, y_min, width, height = bbox
    x_min_padded = max(0, x_min - padding)
    y_min_padded = max(0, y_min - padding)
    x_max_padded = min(img_width, x_min + width + padding)
    y_max_padded = min(img_height, y_min + height + padding)

    # Crop the image using array slicing with clipped coordinates
    cropped_img = img[y_min_padded:y_max_padded, x_min_padded:x_max_padded]

    return cropped_img


def recognize_images(image):
    image_original = image.copy()
    detector = HandDetector(maxHands=2)
    hands, img = detector.findHands(image)
    hands.sort(key=lambda x: x['center'])
    if len(hands) != 2:
        print('Error')
        return []
    left_hand = hands[0]
    right_hand = hands[1]
    left_bbox = left_hand['bbox']
    right_bbox = right_hand['bbox']
    left_image = crop_image_using_bbox(image_original, left_bbox)
    right_image = crop_image_using_bbox(image_original, right_bbox)
    left_rotated_image = cv2.rotate(left_image, cv2.ROTATE_90_COUNTERCLOCKWISE)
    right_rotated_image = cv2.rotate(right_image, cv2.ROTATE_90_CLOCKWISE)

    # plt.imshow(left_rotated_image)
    # plt.show()
    # plt.imshow(right_rotated_image)
    # plt.show()

    detector = HandDetector(maxHands=1)
    hands, img = detector.findHands(left_rotated_image)
    if len(hands) == 0:
        print('Error in catching left hand')
        left_fingers = [-1,-1,-1,-1,-1]
    else:
        left_fingers = detector.fingersUp(hands[0])
    hands, img = detector.findHands(right_rotated_image)
    if len(hands) == 0:
        print('Error in catching right hand')
        right_fingers = [-1,-1,-1,-1,-1]
    right_fingers = detector.fingersUp(hands[0])

    left_pos = None
    right_pos = None

    if np.sum(left_fingers) == 0 or np.sum(left_fingers) == 1:
        left_pos = 'rock'
    if np.sum(right_fingers) == 0 or np.sum(right_fingers) == 1:
        right_pos = 'rock'

    if np.sum(left_fingers) == 2 or np.sum(left_fingers) == 3:
        left_pos = 'scissors'
    if np.sum(right_fingers) == 2 or np.sum(right_fingers) == 3:
        right_pos = 'scissors'

    if np.sum(left_fingers) == 4 or np.sum(left_fingers) == 5:
        left_pos = 'paper'
    if np.sum(right_fingers) == 4 or np.sum(right_fingers) == 5:
        right_pos = 'paper'
    
    if np.sum(left_fingers) == -5:
        left_pos = 'NA'
        return [], []
    if np.sum(right_fingers) == -5:
        right_pos = 'NA'
        return [], []
    return (left_pos, right_pos), (left_image, right_image)

if __name__ == '__main__':
    image_path = 'cam-hi.jpg'
    img = cv2.imread(image_path)
    print(recognize_images(img))
