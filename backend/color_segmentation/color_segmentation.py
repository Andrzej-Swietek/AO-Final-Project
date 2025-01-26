import logging
import os

import cv2

from backend.color_segmentation.clustering import kmeans_image_segmentation, get_color_masks, remove_distortions, \
    get_edges, scale_image, find_inner_points_for_objects, combine_rgb_images, combine_edges

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ImageColorSegmentation:
    OUTPUT_FOLDER: str = "./output"
    scale = 255 / 360

    def __init__(self, task_id: str, color_count: int = 4):
        self.images = []
        self.color_masks = []
        self.image = None
        self.task_id = task_id
        self.color_count = color_count

    def load_image(self, image_path: str) -> None:
        self.image = cv2.imread(image_path)
        self.image = scale_image(self.image)
        self.image = cv2.bilateralFilter(self.image, 9, 125, 125)

    def process_image(self):
        clustering_result = kmeans_image_segmentation(self.image, int(self.color_count))
        raw_masks = get_color_masks(clustering_result)
        contours = []
        colored_masks = []
        all_points = []

        for i in range(len(raw_masks)):
            mask = remove_distortions(raw_masks[i])
            edges = get_edges(mask)
            contours.append(edges)
            colored_mask = mask.copy()
            colored_mask = cv2.cvtColor(colored_mask, cv2.COLOR_GRAY2RGB)
            colored_mask[(colored_mask[:, :, 1] == 255)] = clustering_result.centers[i]
            colored_masks.append(colored_mask)

            object_points = find_inner_points_for_objects(mask)
            all_points.append(object_points)

        combined_colored = combine_rgb_images(colored_masks)
        combined_edges = combine_edges(contours)

        filtered_edges = remove_distortions(cv2.bitwise_not(combined_edges), 3)

        final_image = cv2.bitwise_and(cv2.cvtColor(filtered_edges, cv2.COLOR_GRAY2RGB), combined_colored)
        self.save_image("final_image.bmp", final_image)

        kolorowanka = cv2.cvtColor(filtered_edges, cv2.COLOR_GRAY2RGB)

        for i, object_points in enumerate(all_points):
            for j, (r, c, area) in enumerate(object_points):
                color = clustering_result.centers[i].astype("uint8")
                radius = 5
                if area < 100:
                    radius = 3
                cv2.circle(kolorowanka, (c, r), radius=radius, color=(int(color[0]), int(color[1]), int(color[2])), thickness=-1)

        self.save_image("result.jpg", kolorowanka)

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
