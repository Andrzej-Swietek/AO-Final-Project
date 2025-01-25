from dataclasses import dataclass

import numpy as np
import cv2 as cv
import os


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


