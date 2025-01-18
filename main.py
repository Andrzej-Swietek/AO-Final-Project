import math

import numpy as np
import cv2
from scipy.spatial import cKDTree
from PIL import Image

colorBoundary: int = 10

# img = cv.imread('cat.jpg')
# img = cv.resize(img, [600, 1000])
# Z = img.reshape((-1, 3))
#
# # convert to np.float32
# Z = np.float32(Z)
#
# # define criteria, number of clusters(K) and apply kmeans()
# criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 10, 1.0)
# K = 8
# ret, label, center = cv.kmeans(Z, K, None, criteria, 10, cv.KMEANS_RANDOM_CENTERS)
#
# # Now convert back into uint8, and make original image
# center = np.uint8(center)
# res = center[label.flatten()]
# res2 = res.reshape(img.shape)

# Load the image
# image = cv2.imread('cat.jpg')
# originalHeight = image.shape[0]
# originalWidth = image.shape[1]
#
# targetWidth = 1000
# targetHeight = math.floor((targetWidth/originalWidth) * originalHeight)
#
# image = cv2.resize(image, [targetWidth, targetHeight])
#
# canny = cv2.Canny(image, 0, 10)
# cv2.imwrite('canny.jpg', canny)

# data = image.reshape((-1, 3))  # Reshape to 2D array
# data = np.float32(data)
#
# # Define criteria and number of clusters (k)
# criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.2)
# k = 12
# _, labels, centers = cv2.kmeans(data, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
#
# # Convert centers to uint8 and replace pixel values
# centers = np.uint8(centers)
# quantized_image = centers[labels.flatten()]
# quantized_image = quantized_image.reshape(image.shape)
#
# for i in range(0, 10):
#     quantized_image = cv2.medianBlur(quantized_image, 3)
#
# # Save/Display
# cv2.imwrite('quantized.jpg', quantized_image)

#
# Load the image
image = cv2.imread('cat.jpg')
image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

# Define a predefined palette (RGB values)
palettes = np.array([
    [0, 0, 0],       # Black
    [255, 255, 255], # White
    [255, 0, 0],     # Red
    [0, 255, 0],     # Green
    [0, 0, 255],     # Blue
    [255, 255, 0],   # Yellow
    [255, 0, 255],   # Magenta
    [0, 255, 255],   # Cyan
], dtype=np.uint8)

# Convert palette to float32 for distance calculation
palette_float = np.float32(palette)

# Flatten the image to a 2D array
image_flat = image_rgb.reshape((-1, 3))

# Use cKDTree for fast nearest neighbor search
tree = cKDTree(palette_float)
_, indices = tree.query(image_flat, k=1)  # Find nearest color in the palette

# Map image pixels to the nearest palette color
quantized_image_flat = palette[indices]
quantized_image = quantized_image_flat.reshape(image_rgb.shape)

cv2.imwrite("result.jpg", quantized_image)

