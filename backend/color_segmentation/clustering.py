from dataclasses import dataclass
from typing import Any

import cv2
import numpy as np
import cv2 as cv
import os

from cv2 import reduce
from fontTools.misc.cython import returns
from numpy import ndarray, dtype, floating


@dataclass
class KMeansResult:
    segmented_image: np.ndarray[np.uint8]  # shape (H, W, 3)
    labels: np.ndarray[np.int32]  # shape (H*W,)
    centers: np.ndarray[np.uint8]  # shape (K, 3)

def kmeans_image_segmentation(image: np.ndarray[np.uint8], k: int) -> KMeansResult:

    # Reshape image to a 2D array of pixels (H*W, 3)
    pixels = image.reshape((-1, 3))

    # Convert pixels to float32 for k-means
    pixels = np.float32(pixels)

    # Define k-means criteria
    criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 10, 1.0)

    # Apply k-means clustering
    _, labels, centers = cv.kmeans(
        pixels, k, None, criteria, 10, cv.KMEANS_RANDOM_CENTERS
    )

    # Convert cluster centers back to uint8
    centers = np.uint8(centers)

    # Map each pixel to its cluster center
    segmented_pixels = centers[labels.flatten()]

    # Reshape the segmented pixels back to the original image shape
    segmented_image = segmented_pixels.reshape(image.shape)

    # Return the result as a dataclass
    return KMeansResult(segmented_image=segmented_image, labels=labels, centers=centers)


def get_color_masks(result: KMeansResult) -> list[np.ndarray[np.uint8]]:
    h, w = result.segmented_image.shape[:2]
    labels = result.labels.reshape((h, w))
    masks: list[np.ndarray[np.uint8]] = []
    for cluster_idx in range(len(result.centers)):
        mask = (labels == cluster_idx).astype(np.uint8) * 255
        masks.append(mask)

    return masks


def remove_distortions(binary_image: np.ndarray[np.uint8], power: int = 5) -> np.ndarray[np.uint8]:
    result = cv2.erode(binary_image, np.ones((power, power), np.uint8), iterations=1)
    result = cv2.dilate(result, np.ones((power, power), np.uint8), iterations=1)
    return result

def get_edges(mask: np.ndarray):
    return cv2.dilate(mask, np.ones((5, 5), np.uint8), iterations=1) - cv2.erode(mask, np.ones((5, 5), np.uint8), iterations=1)


def combine_edges(edges: list[np.ndarray[np.uint8]]) -> np.ndarray[np.uint8]:

    combined = np.zeros_like(edges[0], dtype=np.uint8)
    for edge in edges:
        combined = cv.add(combined, edge)

    combined[combined > 255] = 255

    return combined


def shrink_to_points(binary_image: np.ndarray[np.uint8]) -> np.ndarray[np.uint8]:
    img = binary_image.copy()
    kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))

    while True:
        prev = img.copy()
        img = cv2.erode(img, kernel)
        if cv2.countNonZero(img ^ prev) == 0:
            break

    return prev



def combine_rgb_images(images: list[np.ndarray[np.uint8]]) -> np.ndarray[np.uint8]:

    combined = np.zeros_like(images[0], dtype=np.uint16)  # Use uint16 to avoid overflow during addition
    for image in images:
        combined += image  # Add pixel values

    combined = np.clip(combined, 0, 255).astype(np.uint8)  # Clip values to 0-255 and convert back to uint8
    return combined


def sharpen_image(image: np.ndarray[np.uint8], k: int = 3) -> np.ndarray[np.uint8]:
    kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
    sharpened_image = cv2.filter2D(image, -1, kernel)
    # filter_matrix = make_filter_matrix(k)
    # filtered_image = cv2.filter2D(src=image, ddepth=-1, kernel=filter_matrix)
    return sharpened_image

def make_filter_matrix(k: int) -> np.ndarray[np.float32]:
    if k % 2 == 0:
        raise ValueError("Filter size 'k' must be odd.")
    filter_matrix = -1 * np.ones((k, k), dtype=np.float32)
    center = k // 2
    filter_matrix[center, center] = k**2 - 1
    return filter_matrix


def find_inner_points_for_objects(bin_image):
    """
    bin_image: numpy array typu uint8, 0/255 (binarne tło/obiekt)

    Zwraca listę krotek (r, c) – po jednym punkcie dla każdego
    8-spójnego obiektu w obrazie. Punkt jest wybrany tak, by był
    maksymalnie daleko od brzegu (transformacja odległości).
    """
    num_labels, labels = cv2.connectedComponents(bin_image, connectivity=8)

    bin01 = (bin_image > 0).astype(np.uint8)
    dist_map = cv2.distanceTransform(bin01, cv2.DIST_L2, 3)

    points = []
    for label_idx in range(1, num_labels):
        masked_dist = dist_map.copy()
        masked_dist[labels != label_idx] = 0
        # Znajdź maksimum w "masked_dist"
        minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(masked_dist)
        # maxLoc jest (x, y) => (kolumna, wiersz)
        r, c = maxLoc[1], maxLoc[0]
        points.append((r, c))

    return points

