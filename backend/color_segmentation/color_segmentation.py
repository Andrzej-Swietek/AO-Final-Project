import cv2
import numpy as np
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ImageColorSegmentation:
    OUTPUT_FOLDER: str = "../output"
    scale = 255 / 360

    def __init__(self, task_id: str):
        self.images = []
        self.image = None
        self.task_id = task_id
        self.hsl_to_cv2_scale = self.scale
        self.color_ranges = np.array([
            round(0 * self.hsl_to_cv2_scale),
            round(20 * self.hsl_to_cv2_scale),
            round(45 * self.hsl_to_cv2_scale),
            round(65 * self.hsl_to_cv2_scale),
            round(150 * self.hsl_to_cv2_scale),
            round(185 * self.hsl_to_cv2_scale),
            round(220 * self.hsl_to_cv2_scale),
            round(250 * self.hsl_to_cv2_scale),
            round(275 * self.hsl_to_cv2_scale),
            round(325 * self.hsl_to_cv2_scale),
            round(360 * self.hsl_to_cv2_scale)
        ])

    def load_image(self, image_path: str) -> None:
        self.image = cv2.imread(image_path)
        self.image = cv2.cvtColor(self.image, cv2.COLOR_BGR2HLS)
        self.images = []

        for i in range(1, self.color_ranges.size):
            ranged_image = cv2.inRange(self.image, np.array([self.color_ranges[i - 1], 0, 0]),
                                       np.array([self.color_ranges[i], 256, 256]))
            self.images.append(ranged_image)
            self.save_image(f"image{round(float(self.color_ranges[i] / self.hsl_to_cv2_scale))}.jpg", ranged_image)

    def process(self) -> None:
        final_colored_image = np.zeros_like(self.image)

        for i in range(0, len(self.images)):
            colored_image = cv2.cvtColor(self.images[i], cv2.COLOR_GRAY2BGR)
            colored_image = cv2.cvtColor(colored_image, cv2.COLOR_BGR2HLS)
            # logger.info(f"Iteracja {i}\n")
            print(round((float(self.color_ranges[i] + self.color_ranges[i + 1])) / 2))

            # mid_hue = round((colorRanges[i - 1] + colorRanges[i]) / 2)
            # Przekroczenie zakresu indeksu w 'colorRanges', poprawka w obliczeniu mid_hue
            if i == 0:
                mid_hue = round((float(self.color_ranges[i] + self.color_ranges[i + 1])) / 2)
            else:
                mid_hue = round((float(self.color_ranges[i - 1]) + float(self.color_ranges[i])) / 2)

            replacement = [mid_hue, 128, 255]
            colored_image[(colored_image[:, :, 1] == 255)] = replacement  # Set the hue
            colored_image = cv2.cvtColor(colored_image, cv2.COLOR_HLS2BGR)
            final_colored_image = cv2.add(final_colored_image, colored_image)
            self.save_image(f"coloredImage{i}.jpg", colored_image)

        self.save_image("final_colored_image.jpg", final_colored_image)

    def save_image(self, name: str, image) -> None:
        cv2.imwrite(f"{self.OUTPUT_FOLDER}/{name}", image)
