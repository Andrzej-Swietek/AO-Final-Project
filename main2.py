import cv2
import numpy as np

scale: float = 255 / 360
colorRanges = np.array([
    round(0 * scale),
    round(20 * scale),
    round(45 * scale),
    round(65 * scale),
    round(150 * scale),
    round(185 * scale),
    round(220 * scale),
    round(250 * scale),
    round(275 * scale),
    round(325 * scale),
    round(360 * scale)
])

image = cv2.imread("kwiatki.jpg")
image = cv2.cvtColor(image, cv2.COLOR_BGR2HLS)
images = []

for i in range(1, colorRanges.size):
    rangedImage = cv2.inRange(image, np.array([colorRanges[i - 1], 0, 0]), np.array([colorRanges[i], 256, 256]))
    images.append(rangedImage)
    cv2.imwrite(f"image{round(colorRanges[i] / scale)}.jpg", rangedImage)

for i in range(0, len(images)):
    coloredImage = cv2.cvtColor(images[i], cv2.COLOR_GRAY2BGR)
    coloredImage = cv2.cvtColor(coloredImage, cv2.COLOR_BGR2HLS)
    print(round((colorRanges[i] + colorRanges[i + 1])/2))
    mid_hue = round((colorRanges[i - 1] + colorRanges[i]) / 2)
    replacement = [mid_hue, 128, 255]
    coloredImage[(coloredImage[:, :, 1] == 255)] = replacement # Set the hue
    coloredImage = cv2.cvtColor(coloredImage, cv2.COLOR_HLS2BGR)
    cv2.imwrite(f"coloredImage{i}.jpg", coloredImage)

# cv2.imwrite("addedImage.jpg", addedImage)
