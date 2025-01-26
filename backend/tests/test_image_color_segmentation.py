import os
import unittest

import cv2

from backend.color_segmentation.clustering import kmeans_image_segmentation, get_color_masks, remove_distortions, \
    get_edges, combine_edges, combine_rgb_images, find_inner_points_for_objects, \
    scale_image
from backend.color_segmentation.color_segmentation import ImageColorSegmentation


class TestImageColorSegmentation(unittest.TestCase):

    def test_development_case_1(self):
        image_color_segmentation = ImageColorSegmentation(task_id="test_task")
        image_color_segmentation.load_image("../example_images/img.png")
        assert 1 == 1

    def test_development_case_2(self):
        image_color_segmentation = ImageColorSegmentation(task_id="test_task")
        image_color_segmentation.load_image("../example_images/img_1.png")
        assert 1 == 1

    def test_clustering(self):
        directory = "."
        extension = ".bmp"
        for file in os.listdir(directory):
            if file.endswith(extension):
                file_path = os.path.join(directory, file)
                os.remove(file_path)  # Remove the file
                print(f"Deleted: {file_path}")

        og_image = cv2.imread("../example_images/img_1.png")
        og_image = scale_image(og_image)
        cv2.imwrite("original.bmp", og_image)
        og_image = cv2.bilateralFilter(og_image, 9, 125, 125)
        cv2.imwrite("original_filtered.bmp", og_image)
        # og_image = cv2.cvtColor(og_image, cv2.COLOR_RGB2LAB)
        clustering_result = kmeans_image_segmentation(og_image, 6)
        # clustering_result.segmented_image = cv2.cvtColor(clustering_result.segmented_image, cv2.COLOR_LAB2RGB)
        # print(clustering_result.centers)
        # clustering_result.centers = cv2.cvtColor(clustering_result.centers[np.newaxis, :, :], cv2.COLOR_LAB2RGB)[0]
        raw_masks = get_color_masks(clustering_result)
        contours = []
        colored_masks = []
        all_points = []

        for i in range(len(raw_masks)):
            cv2.imwrite("raw_mask" + str(i) + ".bmp", raw_masks[i])
            mask = remove_distortions(raw_masks[i])
            cv2.imwrite("mask" + str(i) + ".bmp", mask)
            edges = get_edges(mask)
            cv2.imwrite("contours" + str(i) + ".bmp", edges)
            contours.append(edges)
            colored_mask = mask.copy()
            colored_mask = cv2.cvtColor(colored_mask, cv2.COLOR_GRAY2RGB)
            colored_mask[(colored_mask[:, :, 1] == 255)] = clustering_result.centers[i]
            colored_masks.append(colored_mask)

            # 2. Znajdź punkt w każdym obiekcie
            object_points = find_inner_points_for_objects(mask)
            all_points.append(object_points)
            cv2.imwrite("colored_mask" + str(i) + ".bmp", colored_mask)

        combined_colored = combine_rgb_images(colored_masks)
        combined_edges = combine_edges(contours)
        canny = cv2.Canny(clustering_result.segmented_image, 75, 175, apertureSize=3, L2gradient=False)
        cv2.imwrite("canny.bmp", canny)
        cv2.imwrite("combined_colored.bmp", combined_colored)

        cv2.imwrite("combined_edges.bmp", combined_edges)
        filtered_edges = remove_distortions(cv2.bitwise_not(combined_edges), 3)

        final_image = cv2.bitwise_and(cv2.cvtColor(filtered_edges, cv2.COLOR_GRAY2RGB), combined_colored)
        cv2.imwrite("final_image.bmp", final_image)
        final_canny = cv2.Canny(final_image, 75, 175)
        cv2.imwrite("final_canny.bmp", final_canny)
        cv2.imwrite("combined_edges_filtered.bmp", filtered_edges)
        cv2.imwrite("segmented.bmp", clustering_result.segmented_image)

        kolorowanka = cv2.cvtColor(filtered_edges, cv2.COLOR_GRAY2RGB)

        for i, object_points in enumerate(all_points):
            for j, (r, c, area) in enumerate(object_points):
                # Rysujemy kółko w punkcie (czerwone)
                color = clustering_result.centers[i].astype("uint8")
                radius = 5
                if area < 100:
                    radius = 3
                cv2.circle(kolorowanka, (c, r), radius=radius, color=(int(color[0]), int(color[1]), int(color[2])), thickness=-1)

        cv2.imwrite("kolorowanka.bmp", kolorowanka)

    assert 1 == 1

    def test_of_test(self):
        assert 1 == 1


if __name__ == "__main__":
    unittest.main()
