import threading
import cv2
import numpy as np
import concurrent.futures


class ConcurrentImageColorSegmentation:
    OUTPUT_FOLDER: str = "../output"
    scale = 255/360

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

        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = []
            for i in range(1, len(self.color_ranges)):
                future = executor.submit(self.create_colored_segment, i)
                futures.append(future)

            concurrent.futures.wait(futures)

    def create_colored_segment(self, i: int):
        ranged_image = cv2.inRange(self.image, np.array([self.color_ranges[i - 1], 0, 0]),
                                   np.array([self.color_ranges[i], 256, 256]))
        self.images.append(ranged_image)
        self.save_image(f"image{round(float(self.color_ranges[i] / self.scale))}.jpg", ranged_image)

    def process(self) -> None:
        final_colored_image = np.zeros_like(self.image)  

        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = []
            for i in range(0, len(self.images)):
                future = executor.submit(self.process_segment, i, final_colored_image)
                futures.append(future)

            concurrent.futures.wait(futures)

        self.save_image("final_colored_image.jpg", final_colored_image)

    def process_segment(self, i: int, final_colored_image):
        colored_image = cv2.cvtColor(self.images[i], cv2.COLOR_GRAY2BGR)
        colored_image = cv2.cvtColor(colored_image, cv2.COLOR_BGR2HLS)
        
        if i == 0:
            mid_hue = round((float(self.color_ranges[i]) + float(self.color_ranges[i + 1])) / 2)
        else:
            mid_hue = round((float(self.color_ranges[i - 1]) + float(self.color_ranges[i])) / 2)

        replacement = [mid_hue, 128, 255]
        colored_image[(colored_image[:, :, 1] == 255)] = replacement
        colored_image = cv2.cvtColor(colored_image, cv2.COLOR_HLS2BGR)

        with threading.Lock():
            final_colored_image[:] = cv2.add(final_colored_image, colored_image)

        self.save_image(f"coloredImage{i}.jpg", colored_image)

    def save_image(self, name: str, image) -> None:
        cv2.imwrite(f"{self.OUTPUT_FOLDER}/{name}", image)
