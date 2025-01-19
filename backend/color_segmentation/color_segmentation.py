import cv2 

class ImageColorSegmentation:
    OUTPUT_FOLDER: str = "../output/"
    hsl_to_cv2_scale = 255/360

    def __init__(self, task_id: str):
        self.images = []
        self.image = None
        self.task_id = task_id
          
        self.colorRanges = np.array([
            round(0 * hsl_to_cv2_scale),
            round(20 * hsl_to_cv2_scale),
            round(45 * hsl_to_cv2_scale),
            round(65 * hsl_to_cv2_scale),
            round(150 * hsl_to_cv2_scale),
            round(185 * hsl_to_cv2_scale),
            round(220 * hsl_to_cv2_scale),
            round(250 * hsl_to_cv2_scale),
            round(275 * hsl_to_cv2_scale),
            round(325 * hsl_to_cv2_scale),
            round(360 * hsl_to_cv2_scale)
        ])

    def load_image(image_path: str) -> None:
        self.image = cv2.imread(image_path)
        self.image = cv2.cvtColor(self.image, cv2.COLOR_BGR2HLS)
        self.images = []

        for i in range(1, self.colorRanges.size):
            rangedImage = cv2.inRange(image, np.array([colorRanges[i - 1], 0, 0]), np.array([colorRanges[i], 256, 256]))
            self.images.append(rangedImage)
            self.save_image(f"image{round(colorRanges[i] / scale)}.jpg", rangedImage)

    def process() -> None:
        final_colored_image = np.zeros_like(self.image)  

        for i in range(0, len(self.images)):
            coloredImage = cv2.cvtColor(self.images[i], cv2.COLOR_GRAY2BGR)
            coloredImage = cv2.cvtColor(coloredImage, cv2.COLOR_BGR2HLS)
            
            print(round((colorRanges[i] + colorRanges[i + 1])/2))

            # mid_hue = round((colorRanges[i - 1] + colorRanges[i]) / 2)
             # Przekroczenie zakresu indeksu w 'colorRanges', poprawka w obliczeniu mid_hue
            if i == 0:
                mid_hue = round((self.colorRanges[i] + self.colorRanges[i + 1]) / 2)
            else:
                mid_hue = round((self.colorRanges[i - 1] + self.colorRanges[i]) / 2)

            replacement = [mid_hue, 128, 255]
            coloredImage[(coloredImage[:, :, 1] == 255)] = replacement # Set the hue
            coloredImage = cv2.cvtColor(coloredImage, cv2.COLOR_HLS2BGR)
            final_colored_image = cv2.add(final_colored_image, coloredImage)

            self.save_image(f"coloredImage{i}.jpg", coloredImage)

         self.save_image("final_colored_image.jpg", final_colored_image)

    def save_image(name:str, image) -> None:
        cv2.imwrite(f"{OUTPUT_FOLDER}/{name}", image)