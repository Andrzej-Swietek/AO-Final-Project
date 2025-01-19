import cv2
import numpy as np
import concurrent.futures

class ConcurrentImageColorSegmentation:
    OUTPUT_FOLDER: str = "../output/"
    scale = 255/360

    def __init__(self, task_id: str):
        self.images = []  
        self.image = None  
        self.task_id = task_id 
        self.hsl_to_cv2_scale = self.scale
        self.colorRanges = np.array([
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
            for i in range(1, len(self.colorRanges)):
                future = executor.submit(self.create_colored_segment, i)
                futures.append(future)

            concurrent.futures.wait(futures)

    def create_colored_segment(self, i: int):
        rangedImage = cv2.inRange(self.image, np.array([self.colorRanges[i - 1], 0, 0]), np.array([self.colorRanges[i], 256, 256]))
        self.images.append(rangedImage)
        self.save_image(f"image{round(self.colorRanges[i] / self.scale)}.jpg", rangedImage)

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
        coloredImage = cv2.cvtColor(self.images[i], cv2.COLOR_GRAY2BGR)
        coloredImage = cv2.cvtColor(coloredImage, cv2.COLOR_BGR2HLS)
        
        if i == 0:
            mid_hue = round((self.colorRanges[i] + self.colorRanges[i + 1]) / 2)
        else:
            mid_hue = round((self.colorRanges[i - 1] + self.colorRanges[i]) / 2)

        replacement = [mid_hue, 128, 255]
        coloredImage[(coloredImage[:, :, 1] == 255)] = replacement  
        coloredImage = cv2.cvtColor(coloredImage, cv2.COLOR_HLS2BGR)

        with threading.Lock():
            final_colored_image[:] = cv2.add(final_colored_image, coloredImage)

        self.save_image(f"coloredImage{i}.jpg", coloredImage)

    def save_image(self, name: str, image) -> None:
        cv2.imwrite(f"{self.OUTPUT_FOLDER}/{name}", image)
