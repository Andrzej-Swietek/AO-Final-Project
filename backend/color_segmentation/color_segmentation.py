import logging
import os

import cv2
import numpy as np

from backend.color_segmentation.clustering import kmeans_image_segmentation, get_color_masks, remove_distortions, \
    get_edges, sharpen_image

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ImageColorSegmentation:
    OUTPUT_FOLDER: str = "./output"
    scale = 255 / 360


    def __init__(self, task_id: str):
        self.images = []
        self.color_masks = []
        self.original_image = None
        self.image = None
        self.task_id = task_id


    def load_image(self, image_path: str) -> None:
        self.original_image = cv2.imread(image_path)
        # self.original_image = sharpen_image(self.original_image)

        self.images = []
        k_means_result = kmeans_image_segmentation(self.original_image, 8)
        # k_means_result.segmented_image = cv2.medianBlur(k_means_result.segmented_image, 3)
        self.color_masks = get_color_masks(k_means_result)

        print(self.color_masks)
        self.color_masks = [remove_distortions(mask) for mask in self.color_masks]
        self.color_masks = [get_edges(mask) for mask in self.color_masks]

        for i in range(len(self.color_masks)):
            cv2.imwrite("mask" + str(i) + ".bmp", self.color_masks[i])

        # for i in range(0, self.color_ranges.size):
        #     hslRange: HslColorRange = self.color_ranges[i]
        #     ranged_image = ImageColorSegmentation.filter_image_by_hsl(self.image, hslRange)
        #     self.images.append(ranged_image)
        #     self.save_image(f"image{hslRange.representation}.jpg", ranged_image)


    def save_image(self, name: str, image) -> None:
        output_path = os.path.join(self.OUTPUT_FOLDER, self.task_id, name)
        try:
            if not os.path.exists(self.OUTPUT_FOLDER):
                os.makedirs(self.OUTPUT_FOLDER, exist_ok=True)

            success = cv2.imwrite(output_path, image)
            if success:
                logger.info(f"Image saved successfully: {output_path}")
            else:
                logger.error(f"Failed to save image: {output_path}")
        except Exception as e:
            logger.error(f"Error while saving image {output_path}: {e}")
